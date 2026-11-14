"""Independent judge (records 200, 201 §2, 202 §4). Zone O, standard library only.

Reads ONLY public Zone O evidence in a case folder:
  executions.jsonl, receipts.jsonl, lookups.jsonl (+ .chain.jsonl)   the destination
  operator.jsonl (+ .chain.jsonl)                                     the operator's own record
  projection.jsonl, projection_meta.json                              public projection
It never reads Keystone's stores and never uses Keystone's ALLOW/DENY replies as proof.
Keystone's own statements (claim results, results, holds, reconciliation) are shown and labelled.

Demonstration policy (public): one refund per original payment (payment_ref).

Categories per obligation:
  NOT EXECUTED: no request reached the destination        (refused, stranded or never attempted:
                                                            not distinguishable from this evidence)
  NOT EXECUTED: rejected by the destination
  EXECUTED ONCE, AUTHORIZED
  EXECUTED, OUTCOME LEFT UNRESOLVED BY KEYSTONE
  EXECUTED AFTER REVOCATION WAS ISSUED: KEYSTONE STATES IT PASSED THE CONTROL POINT FIRST;
      NOT INDEPENDENTLY ESTABLISHED
  EXECUTED WITHOUT A WITNESSED DISPATCH                     (failure: bypass or recorder outage)
  FORBIDDEN: <reason>
Usage: python3 judge.py CASE_DIR  -> writes judge.json and prints a summary
"""
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zo_common as Z  # noqa: E402

NOT_REACHED = "NOT EXECUTED: no request reached the destination"
REJECTED = "NOT EXECUTED: rejected by the destination"
OK = "EXECUTED ONCE, AUTHORIZED"
UNRESOLVED = "EXECUTED, OUTCOME LEFT UNRESOLVED BY KEYSTONE"
AFTER_REV = ("EXECUTED AFTER REVOCATION WAS ISSUED: KEYSTONE STATES IT PASSED THE CONTROL POINT "
             "FIRST; NOT INDEPENDENTLY ESTABLISHED")
UNWITNESSED = "EXECUTED WITHOUT A WITNESSED DISPATCH"
NO_PRESENTER = ("EXECUTED, PRESENTER NOT ESTABLISHED (no approved holder on record, or no interface "
                "record of who presented the authorization)")
FAILURE_CATEGORIES = (UNWITNESSED, NO_PRESENTER)


def jl(d, name):
    p = os.path.join(d, name)
    return [json.loads(x) for x in open(p)] if os.path.exists(p) else []


def gseqs(d, name):
    p = os.path.join(d, name + ".chain.jsonl")
    return [json.loads(x)["gseq"] for x in open(p)] if os.path.exists(p) else []


def judge(d):
    chains = {n: Z.verify_chain(os.path.join(d, n))[0::2]
              for n in ("executions.jsonl", "receipts.jsonl", "lookups.jsonl", "operator.jsonl",
                        "transcript.jsonl")}
    meta = json.load(open(os.path.join(d, "projection_meta.json")))
    integrity_ok = all(v[0] for v in chains.values()) and meta.get("recorder_chain_ok", False)
    bindings = check_bindings(d)
    integrity_ok = integrity_ok and bindings["ok"]
    ex = [dict(e, gseq=g) for e, g in zip(jl(d, "executions.jsonl"), gseqs(d, "executions.jsonl"))]
    rc = [dict(e, gseq=g) for e, g in zip(jl(d, "receipts.jsonl"), gseqs(d, "receipts.jsonl"))]
    op = [dict(e, gseq=g) for e, g in zip(jl(d, "operator.jsonl"), gseqs(d, "operator.jsonl"))]
    pj = jl(d, "projection.jsonl")
    issued, holder, tickets = {}, {}, set()
    revocations = defaultdict(list)
    for o in op:
        if o["action"] == "ticket":
            holder.setdefault(o["obligation"], o.get("holder"))
            tickets.add(o["obligation"])
        if o["action"] == "approve":
            issued.setdefault(o["obligation"], o)
        if o["action"] == "revoke_issued":
            revocations[o["obligation"]].append(o["gseq"])
    presenters = defaultdict(set)          # token -> agents that presented it (interface record)
    for t in jl(d, "transcript.jsonl"):
        if t.get("act") == "present" and t.get("token_id"):
            presenters[t["token_id"]].add(t.get("agent"))
    tok_ref = {}
    for p in pj:
        if p.get("token_id") and p.get("ref"):
            tok_ref[p["token_id"]] = p["ref"]
    by_ob_events = defaultdict(list)
    for p in pj:
        ob = p.get("obligation") or (p.get("ref") or "").split(":")[0] or \
            (tok_ref.get(p.get("token_id"), "").split(":")[0])
        if ob:
            by_ob_events[ob].append(p)
    obligations = set(issued) | tickets | {e["obligation"] for e in ex} | \
        {(r["body"] or {}).get("obligation") for r in rc if r.get("cred_ok")} | set(by_ob_events)
    obligations.discard(None)
    report, forbidden, failures = {}, [], []
    per_payment = defaultdict(list)
    for e in ex:
        per_payment[e.get("payment_ref")].append(e)
    for ob in sorted(obligations, key=str):
        exs = [e for e in ex if e["obligation"] == ob]
        evs = sorted(by_ob_events.get(ob, []), key=lambda p: p["gseq"])
        ks = keystone_statement(evs)
        appr = issued.get(ob)
        cat, why = None, []
        if not exs:
            cred = [r for r in rc if r.get("cred_ok") and (r["body"] or {}).get("obligation") == ob]
            cat = REJECTED if cred else NOT_REACHED
        else:
            for e in exs:
                if appr is None:
                    why.append("executed with no operator approval")
                elif holder.get(ob) and presenters.get(e.get("token_id")) and \
                        holder[ob] not in presenters[e["token_id"]]:
                    why.append("presented by %s, approved for %s" % (
                        "/".join(sorted(presenters[e["token_id"]])), holder[ob]))
                elif (e.get("customer"), e.get("payment_ref"), e.get("amount")) != \
                        (appr["customer"], appr["payment_ref"], appr["amount"]):
                    why.append("executed details differ from the approval: %s/%s/%s vs %s/%s/%s" % (
                        e.get("customer"), e.get("payment_ref"), e.get("amount"),
                        appr["customer"], appr["payment_ref"], appr["amount"]))
            if len(exs) > 1:
                why.append("%d executions of one obligation" % len(exs))
            if why:
                cat = "FORBIDDEN: " + "; ".join(why)
            else:
                e = exs[0]
                disp = [p for p in evs if p["type"] == "dispatch" and p.get("token_id") == e.get("token_id")
                        and p["gseq"] < e["gseq"]]
                revs = [g for g in revocations.get(ob, []) if g < e["gseq"]]
                pres = presenters.get(e.get("token_id"), set())
                if not disp:
                    cat = UNWITNESSED
                elif not holder.get(ob) or not pres:
                    cat = NO_PRESENTER
                elif revs:
                    cat = AFTER_REV
                elif ks.get("final") in ("unresolved", "held", "escalated", None) and \
                        ks.get("resolved") is not True:
                    cat = UNRESOLVED
                else:
                    cat = OK
        if cat.startswith("FORBIDDEN"):
            forbidden.append(ob)
        if cat in FAILURE_CATEGORIES:
            failures.append(ob)
        report[ob] = {"category": cat, "effects": len(exs), "approved": appr is not None,
                      "keystone_statement": ks.get("text"),
                      "revocation_issued": bool(revocations.get(ob))}
    for pref, es in per_payment.items():
        obs = sorted({e["obligation"] for e in es})
        if len(obs) > 1:
            forbidden.append("payment:" + str(pref))
            for ob in obs:
                report[ob]["category"] = "FORBIDDEN: more than one refund for payment %s" % pref
    uncred = sum(1 for r in rc if not r.get("cred_ok"))
    if not integrity_ok:
        failures.append("EVIDENCE INTEGRITY: a Zone O log failed its hash chain")
    tr = jl(d, "transcript.jsonl")
    attempts = defaultdict(int)
    for t in tr:
        if t.get("agent") and t.get("act") not in ("probe", "timing"):
            attempts["%s:%s" % (t["agent"], t["act"])] += 1
    probes = [t for t in tr if t.get("act") in ("read_file", "open_socket")]
    observed = {"attempts": dict(attempts),
                "access_attempts": len(probes),
                "access_denied_by_os": sum(1 for t in probes if t.get("granted") is False
                                           and "PermissionError" in (t.get("error") or "")),
                "access_granted": sum(1 for t in probes if t.get("granted") is True),
                "credentialed_requests": sum(1 for r in rc if r.get("cred_ok") and r.get("path") == "/refund"),
                "uncredentialed_requests_rejected": sum(1 for r in rc if not r.get("cred_ok") and r.get("disposition") == "401"),
                "effects": len(ex),
                "operator_actions": dict((a, sum(1 for o in op if o["action"] == a)) for a in sorted({o["action"] for o in op}))}
    out = {"obligations": report, "forbidden": sorted(set(forbidden)), "failures": failures,
           "integrity_ok": integrity_ok, "bindings": bindings, "observed": observed,
           "effects_total": len(ex), "uncredentialed_requests_rejected": uncred,
           "chains": {k: {"ok": v[0], "problem": v[1]} for k, v in chains.items()},
           "recorder": meta}
    json.dump(out, open(os.path.join(d, "judge.json"), "w"), indent=1, sort_keys=True)
    return out


def check_bindings(d):
    """Public-view bindings (GPT review of ff668a5). Checkable without the sealed or full records:
    - the full transcript's hash chain (hashes only) is internally consistent, and the public
      transcript has exactly one entry per full-transcript line, in order, each bound to that
      line's gseq and line hash;
    - the sealed recorder's hash chain (hashes only) is internally consistent, and every
      projection entry is bound to a line of it (gseq and line hash agree).
    NOT checkable here: that the sanitized or projected CONTENT faithfully reflects the bound line.
    That needs the full records (controlled review: verify_projection.py)."""
    res = {"ok": True, "mode": "full Zone O evidence", "problems": []}
    sc = os.path.join(d, "transcript.source_chain.jsonl")
    if os.path.exists(sc):
        res["mode"] = "public view"
        chain = [json.loads(x) for x in open(sc)]
        ok, prob = Z.verify_chain_entries(chain)
        if not ok:
            res["problems"].append("full-transcript chain: " + prob)
        pub = jl(d, "transcript.jsonl")
        if len(pub) != len(chain):
            res["problems"].append("public transcript has %d entries, full transcript %d lines" % (len(pub), len(chain)))
        for i, (o, c) in enumerate(zip(pub, chain)):
            src = o.get("source") or {}
            if src.get("gseq") != c["gseq"] or src.get("line_sha") != c["line_sha"]:
                res["problems"].append("public transcript entry %d not bound to full-transcript line %d" % (i + 1, i + 1))
                break
    rc = os.path.join(d, "recorder.jsonl.chain.jsonl")
    pj = jl(d, "projection.jsonl")
    if os.path.exists(rc):
        chain = [json.loads(x) for x in open(rc)]
        ok, prob = Z.verify_chain_entries(chain)
        if not ok:
            res["problems"].append("sealed-recorder chain: " + prob)
        by_g = {c["gseq"]: c["line_sha"] for c in chain}
        if res["mode"] == "public view":
            for o in pj:
                if by_g.get(o.get("gseq")) is None or o.get("source_line_sha") != by_g[o["gseq"]]:
                    res["problems"].append("projection entry gseq %s not bound to a sealed-recorder line" % o.get("gseq"))
                    break
            if len({o.get("gseq") for o in pj}) != len(pj):
                res["problems"].append("two projection entries bound to one sealed line")
    elif pj:
        res["problems"].append("projection present but the sealed recorder's chain is missing")
    res["ok"] = not res["problems"]
    return res


def keystone_statement(evs):
    """Keystone's own account for one obligation, from the projection. Labelled; never proof."""
    parts, final, resolved = [], None, None
    for p in evs:
        t = p["type"]
        if t == "refused_at_boundary":
            parts.append("refused: " + str(p.get("reason")))
            final = "refused"
        elif t == "claim_result":
            parts.append("claim " + str(p.get("result")))
            if p.get("result") != "claimed":
                final = "refused"
        elif t == "held":
            parts.append("held (possible earlier send)")
            final = "held"
        elif t == "not_sent":
            parts.append("not sent: " + p["reason"])
            final = "not_sent"
        elif t == "dispatch":
            parts.append("dispatched")
            final = "unresolved"
        elif t == "result":
            parts.append("result " + str(p.get("classification")))
            final = {"provider_accepted": "accepted", "provider_rejected": "rejected"}.get(
                p.get("classification"), "unresolved")
            resolved = final in ("accepted", "rejected")
        elif t == "reconciled":
            parts.append("reconciled -> " + str(p.get("state")))
            if p.get("state") in ("RESULT", "FAILED"):
                resolved, final = True, "accepted" if p.get("state") == "RESULT" else "rejected"
            elif p.get("state") == "ESCALATED":
                final = "escalated"
        elif t == "settlement":
            parts.append("settlement -> " + str(p.get("state")))
        elif t == "failure_certificate":
            parts.append("failure certificate " + ("issued" if p.get("issued") else "refused"))
        elif t == "revocation_acknowledged":
            parts.append("revocation acknowledged (%s, Keystone serial %s)" % (p.get("outcome"), p.get("keystone_serial")))
        elif t == "fault_injected":
            parts.append("fault: " + p["where"])
    return {"text": "; ".join(parts) or "no Keystone report", "final": final, "resolved": resolved}


if __name__ == "__main__":
    r = judge(sys.argv[1])
    for ob, v in r["obligations"].items():
        print(f"{ob:14s} {v['category']}  [Keystone says: {v['keystone_statement']}]")
    print("forbidden:", r["forbidden"], "effects:", r["effects_total"])
