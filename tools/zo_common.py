"""Zone O shared helpers: a cross-process Zone O sequence and hash-chained side logs.

Independent of Keystone: standard library only, imports nothing from Zone P.
Every Zone O record (recorder event, destination receipt/execution/lookup, operator action) takes
the next number from ONE Zone O sequence, so the judge can order them against each other.
Each Zone O log line is also entered in a hash chain (<name>.chain.jsonl): an edited, removed or
reordered line breaks the chain.
"""
import fcntl
import hashlib
import json
import os
import socket
import struct


def _seq_path(run_dir):
    return os.path.join(run_dir, "zone_o_seq")


def next_seq(run_dir):
    p = _seq_path(run_dir)
    fd = os.open(p, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        raw = os.read(fd, 64)
        n = int(raw) + 1 if raw.strip() else 1
        os.lseek(fd, 0, 0)
        os.ftruncate(fd, 0)
        os.write(fd, str(n).encode())
        os.fsync(fd)
        return n
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def append_chained(run_dir, name, line_obj, gseq):
    """Append line_obj (exact JSON line) to <name> and its chain entry to <name>.chain.jsonl.
    Caller must hold whatever lock orders appends to <name>."""
    line = json.dumps(line_obj, sort_keys=True)
    p = os.path.join(run_dir, name)
    with open(p, "a") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())
    cp = p + ".chain.jsonl"
    prev = "0" * 64
    if os.path.exists(cp):
        with open(cp) as f:
            last = None
            for last in f:
                pass
            if last:
                prev = json.loads(last)["h"]
    h = sha((prev + sha(line.encode())).encode())
    with open(cp, "a") as f:
        f.write(json.dumps({"gseq": gseq, "line_sha": sha(line.encode()), "prev": prev, "h": h},
                           sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def verify_chain(path):
    """Returns (ok, n_lines, problem)."""
    cp = path + ".chain.jsonl"
    if not os.path.exists(path):
        return (not os.path.exists(cp)), 0, None
    lines = open(path).read().splitlines()
    chain = [json.loads(x) for x in open(cp).read().splitlines()] if os.path.exists(cp) else []
    if len(lines) != len(chain):
        return False, len(lines), f"{len(lines)} lines but {len(chain)} chain entries"
    prev = "0" * 64
    for i, (ln, c) in enumerate(zip(lines, chain)):
        if c["line_sha"] != sha(ln.encode()) or c["prev"] != prev:
            return False, len(lines), f"line {i + 1} does not match its chain entry"
        h = sha((prev + c["line_sha"]).encode())
        if h != c["h"]:
            return False, len(lines), f"chain hash broken at line {i + 1}"
        prev = h
    return True, len(lines), None


def peercred(conn):
    pid, uid, gid = struct.unpack("3i", conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED,
                                                        struct.calcsize("3i")))
    return {"pid": pid, "uid": uid, "gid": gid}


def verify_chain_entries(chain):
    """Verify a chain from its entries alone (no access to the underlying lines): each entry's
    prev is the previous h, and h = sha(prev + line_sha). Returns (ok, problem)."""
    prev = "0" * 64
    for i, c in enumerate(chain):
        if c["prev"] != prev or sha((prev + c["line_sha"]).encode()) != c["h"]:
            return False, "chain broken at entry %d" % (i + 1)
        prev = c["h"]
    return True, None
