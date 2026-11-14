"""Zone O simulated payment destination. Independent replacement for run 7's endpoint process.

Written to the same PUBLIC protocol as the run 7 endpoint (record 188 section 3), standard library
only, no Keystone code. HTTP/1.1 over <run_dir>/endpoint.sock; caller identity by SO_PEERCRED;
credential = "Authorization: Bearer <secret>" where the secret is in <run_dir>/endpoint_secret.

Logs (same line formats as run 7, plus Zone O sequence and hash chains):
  receipts.jsonl    every complete request, fsynced before anything else
  executions.jsonl  ACCEPTED EFFECTS, written only by execute(): the ground truth
  lookups.jsonl     read-only /lookup and /settlement calls

Behaviour per payment reference ref, from <run_dir>/faults.json
  {"modes": {ref: mode}, "lookup": {ref: "lag"}, "settle": {ref: "failed_after_paid"}}
  executes:       normal(200) 500(500) reset(connection reset) hold(executes; reply held until
                  <run_dir>/release_<ref> exists, max 30 s)
  never executes: 401 403 422 (that code); declined (500; look-up answers declined, final);
                  500_noexec (500); reset_noexec (reset)
  no or wrong credential -> 401, never executes.
/lookup {ref}: paid if executed (unless lookup lag -> not_found); declined/final if declined;
               else not_found.   /settlement {ref}: settled if executed (unless
               failed_after_paid); else not_found.
Usage: python3 destination_o.py RUN_DIR
"""
import json
import os
import socket
import socketserver
import struct
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zo_common as Z  # noqa: E402

RUN_DIR = sys.argv[1]
SECRET = open(os.path.join(RUN_DIR, "endpoint_secret")).read().strip()
EXECUTES = {"normal", "500", "reset", "hold"}
lock = threading.Lock()
n = [0]


def cfg():
    try:
        with open(os.path.join(RUN_DIR, "faults.json")) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def jl(name):
    p = os.path.join(RUN_DIR, name)
    return [json.loads(x) for x in open(p)] if os.path.exists(p) else []


def execute(rn, body, peer):
    Z.append_chained(RUN_DIR, "executions.jsonl", {
        "receipt_n": rn, "ref": body.get("ref"), "obligation": body.get("obligation"),
        "attempt": body.get("attempt"), "customer": body.get("customer"),
        "payment_ref": body.get("payment_ref"), "amount": body.get("amount"),
        "token_id": body.get("token_id"), "peer_uid": peer["uid"], "t": time.time()},
        Z.next_seq(RUN_DIR))


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def address_string(self):
        return "unix"

    def log_message(self, *a):
        pass

    def reply(self, code, obj):
        out = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def do_POST(self):
        ln = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(ln)
        if len(raw) != ln:
            return                              # incomplete request: not a receipt
        peer = Z.peercred(self.connection)
        cred_ok = self.headers.get("Authorization") == "Bearer " + SECRET
        try:
            body = json.loads(raw)
        except ValueError:
            body = {}
        if self.path in ("/lookup", "/settlement"):
            return self.read_only(body, peer, cred_ok)
        ref = body.get("ref") or ""
        mode = cfg().get("modes", {}).get(ref, "normal") if cred_ok else "401"
        with lock:
            n[0] += 1
            rn = n[0]
            Z.append_chained(RUN_DIR, "receipts.jsonl", {
                "n": rn, "path": self.path, "peer_uid": peer["uid"], "peer_pid": peer["pid"],
                "cred_ok": cred_ok, "ref": ref, "token_id": body.get("token_id"), "body": body,
                "disposition": mode, "t": time.time()}, Z.next_seq(RUN_DIR))
            if mode in EXECUTES:
                execute(rn, body, peer)
        if mode == "hold":
            rel = os.path.join(RUN_DIR, "release_" + ref.replace(":", "_"))
            t0 = time.time()
            while not os.path.exists(rel) and time.time() - t0 < 30:
                time.sleep(0.01)
            mode = "normal"
        if mode in ("reset", "reset_noexec"):
            self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
            self.close_connection = True
            self.connection.shutdown(socket.SHUT_RDWR)
            return
        code = {"normal": 200, "401": 401, "403": 403, "422": 422, "500": 500,
                "500_noexec": 500, "declined": 500}[mode]
        self.reply(code, {"status": "accepted" if code == 200 else "error", "code": code})

    def read_only(self, body, peer, cred_ok):
        ref = body.get("ref") or ""
        c = cfg()
        if not cred_ok:
            ans = {"error": "unauthorized"}
        else:
            executed = any(e["ref"] == ref for e in jl("executions.jsonl"))
            declined = any(r["ref"] == ref and r["disposition"] == "declined"
                           for r in jl("receipts.jsonl") if r.get("path") == "/refund")
            if self.path == "/lookup":
                if executed:
                    ans = {"status": "not_found"} if c.get("lookup", {}).get(ref) == "lag" \
                        else {"status": "paid"}
                elif declined:
                    ans = {"status": "declined", "final": True}
                else:
                    ans = {"status": "not_found"}
            else:
                ans = {"status": c.get("settle", {}).get(ref, "settled")} if executed \
                    else {"status": "not_found"}
        with lock:
            Z.append_chained(RUN_DIR, "lookups.jsonl", {
                "path": self.path, "ref": ref, "peer_uid": peer["uid"], "cred_ok": cred_ok,
                "answer": ans, "t": time.time()}, Z.next_seq(RUN_DIR))
        self.reply(200 if cred_ok else 401, ans)


class S(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True


if __name__ == "__main__":
    p = os.path.join(RUN_DIR, "endpoint.sock")
    if os.path.exists(p):
        os.unlink(p)
    srv = S(p, H)
    os.chmod(p, 0o666)
    open(os.path.join(RUN_DIR, "endpoint.ready"), "w").close()
    srv.serve_forever()
