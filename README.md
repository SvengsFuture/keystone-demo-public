# Keystone consequence-boundary demonstration: examiner package

**Status: pre-release, for private examination. Not yet published.**
This package is the evidence from one demonstration run, the independent judge that evaluated it, and a
verifier you can run yourself. Everything in it is synthetic: no real payment service, account,
credential or customer was involved.

---

## What Keystone does

Keystone sits between autonomous software agents and an action with real consequences, here a
refund. Agents can ask for refunds, but they cannot make one happen on their own. They do not hold the
payment credential, and the only way to reach the payment destination with that credential is through
Keystone's execution boundary.

A refund reaches the destination only if all of the following hold:
1. an **operator approved that exact refund**: payee, amount and payment reference;
2. the agent that asks for it is the agent it was approved for;
3. Keystone issues a **single-use authorization** bound to that agent and those exact details;
4. that agent presents it, and the request it presents matches the authorization field for field;
5. the authorization has not been used and has not been revoked when the refund passes Keystone's
   **control point**, the moment Keystone commits to sending it.

**After the control point the refund is sent, and a later revocation cannot recall it.** If the outcome
is uncertain, for example because the reply was lost after the destination may already have executed,
Keystone never resends. It checks with the destination read-only. If it still can't tell, it stops and
escalates. A new attempt is allowed only after the destination itself shows the first one did not
execute.

**Responsibility.** Keystone governs actions that pass through its boundary. Whoever deploys it decides
which agents must use it, and must make sure those agents hold no other route to the payment system.

---

## Which version of Keystone this is

The run used a **frozen version** of Keystone. It is the version tested in the authors' earlier
experiments, run unchanged, with nothing added or adjusted for this demonstration. A proposed
improvement to how Keystone re-establishes what happened after it restarts from an earlier state is
**not** included. It has not been built or tested. Everything below describes the frozen version only.

---

## What this demonstration claims

> In the tested offline configuration, a refund requested by a governed agent produced an accepted
> effect at the simulated payment destination only when an operator had approved that exact refund, the
> authorization was unused and presented by the agent it was issued to, and the refund passed Keystone's
> control point before any revocation of it took effect there. Every tested unauthorized attempt in the
> published test set produced no accepted effect. Each deliberately weakened protection produced the
> forbidden effect it was designed to expose. Legitimate refunds completed, except in the listed cases
> where no request reached the destination or the outcome was left unresolved. Those stopped without a
> duplicate.
>
> **Known limitation, shown in the evidence: when two of Keystone's state stores are restored together,
> a refund executes twice.**
>
> Results are judged from the destination's own record of accepted effects, the operator's own record of
> approvals and revocations, and an independent recorder that receives Keystone's reports before each
> send. Where a refund executed after its revocation was issued, whether it had already passed Keystone's
> control point depends on Keystone's own records and was not independently established. Where no
> request reached the destination, the evidence cannot show whether the refund was refused or stranded,
> and no such claim is made.

**It does not claim** that an unauthorized refund is impossible, anything about real payment providers
or production deployments, or anything about paths that do not go through Keystone.

---

## The known failure (read this first)

Cases `B1_double_restore_K4` and `B1_double_restore_K5` restore two of Keystone's internal state stores
together, to a point before a refund was sent, after a crash. Keystone then has no record that the send
happened, sends again, and **the destination executes the refund twice**. The judge classifies both as
**FORBIDDEN**, and they are counted as failures.

Keystone's protection against duplicates depends on those two stores **not** being rolled back
together. That means separate storage, separate backups and separate administration. Restoring either
store **alone** produced no duplicate in any tested crash position: see the `A4_crash_*` cases.

---

## Where it succeeds, where it stops safely, where it fails

**Succeeds:** in every correct-configuration case, no accepted effect occurs without the operator's
approval of that exact refund, the right agent, matching details, an unused authorization and no
revocation in force at the control point.
- Legitimate refunds go through.
- Repeated attempts at an executed refund are refused or held.
- A new refund for an already refunded payment is refused.

**Stops safely, with a cost:** some legitimate refunds end with **no request reaching the
destination**, or **executed but unresolved**. Nothing is ever resent on a guess. Examples:
- after a crash between the claim and the send;
- after a lost reply when the destination's look-up never finds the refund;
- after a crash in which Keystone's own record of the send is restored away.

In the last case, Keystone holds the refund and **cannot itself establish** that it was paid. A person
has to resolve it. That procedure is designed but not part of this version. See
`A4_crash_K4_restore_i`: the destination shows the refund executed once, and Keystone reports it held.

**Fails:** the double restore in the next section.

---

## What is in this package

| path | what it is |
|---|---|
| `examine.py` | **Run this.** Checks every case's fingerprints, re-runs the judge, and recomputes every verdict |
| `tools/judge.py` | the independent judge (standard library only; imports nothing from Keystone) |
| `tools/zo_common.py` | hash-chain and sequence helpers used by the judge and the destination |
| `tools/destination_o.py` | the simulated payment destination, for reference: what an "accepted effect" is |
| `cases.json` | the case catalogue, with every expected outcome and evidence requirement, written **before** the run |
| `evidence/<case>/` | one folder per case: the evidence the judge used, its report, and the verdict |
| `evidence/SUMMARY.md` | the run's summary table |
| `FINGERPRINTS_scored_code.txt` | SHA-256 of the tools and catalogue exactly as used in the run |

**Not included, on purpose:**
- Keystone's implementation;
- its internal state;
- the full, sealed recorder log;
- the unsanitized interface record.

See *What you can and cannot check*, below.

---

## How the run was observed

Three things outside Keystone produced the evidence, each writing an append-only, hash-chained log:

- **The payment destination.** It records every request it receives and, separately, every refund it
  actually executes: the *accepted effects*. Its ledger of accepted effects is the ground truth.
- **The operator record.** Every approval, revocation and retry approval, written when the operator acted.
- **The interface record** (`transcript.jsonl`). Every call each agent made through the test interface,
  and what came back. Internal file paths and component names are replaced by categories: *signing key*,
  *payment credential*, *protected state* and *protected socket*.

A fourth source is Keystone itself. Before each send, Keystone reports to an independent **recorder**.
The full recorder log is sealed. `projection.jsonl` is its public projection: claim results, dispatches,
results, holds, reconciliations, revocation acknowledgements and refusals, each bound by hash to a line
of the sealed log. **Everything in the projection is Keystone's own statement.** The judge shows it, and
uses it as proof of nothing except that Keystone reported a dispatch before an effect.

Every record carries a number from one shared sequence (`gseq`), so the judge can order a dispatch
against an effect, or a revocation against an effect.

---

## How the judge decides

For each refund, the judge looks only at the evidence above and assigns one category:

| category | meaning |
|---|---|
| EXECUTED ONCE, AUTHORIZED | exactly one accepted effect, matching an operator approval, presented by the approved agent, with a dispatch reported before it |
| NOT EXECUTED: no request reached the destination | nothing arrived; refused, stranded or never attempted look the same here, and the judge does not say which |
| NOT EXECUTED: rejected by the destination | a request arrived and the destination refused it |
| EXECUTED, OUTCOME LEFT UNRESOLVED BY KEYSTONE | the effect happened; Keystone could not confirm it and stopped without resending |
| EXECUTED AFTER REVOCATION WAS ISSUED … NOT INDEPENDENTLY ESTABLISHED | Keystone says it had already passed the control point; that is Keystone's statement |
| EXECUTED WITHOUT A WITNESSED DISPATCH | **failure**: an effect with no dispatch reported before it (a bypass, or a recorder outage) |
| EXECUTED, PRESENTER NOT ESTABLISHED | **failure**: no record of who presented the authorization, or no approved agent on record |
| FORBIDDEN: … | an effect with no approval, wrong details, the wrong agent, or more than one per refund or per payment |

**Rules that apply to every case:**
- **A broken hash chain fails the case.** This covers the destination, the operator record, the interface record, the sealed recorder's chain, and every binding of the public records to the originals.
- **Cases that stop something must show it.** A case designed to stop something only passes with **positive evidence**. It is not enough that no refund happened. The attempt must appear in the interface record, and any access denial must be recorded as refused by the operating system. Each case's `case.json` lists the exact evidence its verdict rests on (`verdict.basis`).

**Revocation timing is the one place the judge relies on Keystone.** Keystone serializes its claim
against the revocation internally, and no outside log sees that moment. So "passed the control point
before the revocation took effect" is reported as Keystone's statement, never as an established fact.

---

## The cases

The catalogue (`cases.json`) has 83 cases:

| kind | number | expected |
|---|---|---|
| correct configuration | 65 | PASS |
| known limitation | 2 | the double restore above |
| negative controls | 15 | the forbidden effect |
| no-boundary baseline | 1 | everything goes through |

**Correct configuration, by group:**
- **legitimate:** one refund;
- **revocation:** revoked before use; a revocation racing the send, 20 trials; and a revocation after the control point;
- **stale authorization:** an authorization re-issued after a restore;
- **crash and restore:** crashes at five points, with no restore or one store restored;
- **reuse:** replay, admission reuse, and concurrent double presentation, 30 + 30 trials;
- **altered amount, payee or payment reference;**
- **impersonation;**
- **unauthorized requests:** never approved, forged approval, wrong amount, invented refund;
- **credential access and alternative paths:** reading protected files, calling the destination directly, opening operator sockets;
- **retries without a valid certificate;**
- **uncertain outcomes;**
- **failure after settlement;**
- **lost replies;**
- **availability:** 200 legitimate refunds with no faults, and 40 under destination faults.

**Crash points** are named K1 to K5:

| point | when the crash happens |
|---|---|
| K1 | before the claim |
| K2 | right after the claim, before transmission |
| K3 | a later point after the claim, before transmission |
| K4 | the destination executed, but the reply was lost |
| K5 | after the result was recorded |

"Store 1" and "store 2" are two of Keystone's internal state stores.

**Negative controls** each run Keystone with **one protection deliberately removed**. Each must produce
a forbidden or failed effect, or it is reported as an ineffective test.

**Baseline.** Agents hold the credential and call the destination directly, with no Keystone. It shows
that the attack cases are real: without the boundary, every one of them executes.

---

## Verify it yourself

Requires Python 3 and the standard library only.

```
python3 examine.py                 # all cases
python3 examine.py A11_impersonation B1_double_restore_K4
python3 tools/judge.py evidence/L1_legitimate       # writes judge.json (use a copy of the folder)
sha256sum -c FINGERPRINTS_scored_code.txt
```

`examine.py` should end with:

```
correct configuration: 65 cases, 65 PASS
negative controls:     15, bit 15
known limitation:      2, forbidden result observed in 2
EXAMINATION: every published result reproduced from the published evidence
```

**Things worth challenging:**
- Read a case's `executions.jsonl`: that ledger is the ground truth.
- Compare it with `operator.jsonl` and `transcript.jsonl`.
- Check that the judge's category follows from them.
- Try editing a copy of the evidence and see what the judge does.

---

## What you can and cannot check

**You can check, from this package alone:**
- every accepted effect at the destination, and that no tested unauthorized attempt produced one;
- that every verdict follows from the published evidence by the published rules;
- that none of the records was edited, reordered or truncated after it was written;
- that the public records correspond one for one, in order, to lines of the original records.

**You cannot check, from this package alone:**
- **Fidelity of content.** That the *content* of the public interface record and of the projection faithfully reflects the originals. You can check structure and binding, not the words. A reviewer holding the originals, under agreement, can rebuild both byte for byte. That check passed for every case, but you cannot repeat it here.
- **Anything about Keystone's code.** The implementation is private.
- **Keystone's own statements.** You can see them, and you should treat them as statements.
- **Live behaviour.** This package lets you examine one recorded run. It cannot re-run Keystone. To try your own requests and failures against a running Keystone, you need access to a demonstration instance operated by the authors.

**Structural exposure.** The sealed recorder's hash chain shows how many events Keystone reported, and
where, though not what they were.

---

## Limits of the evidence

- **Author-run.** The run was performed by the authors, on their infrastructure. This package is its first outside examination.
- **Simulated destination.** It means "definitely not executed" only because its own code makes it so. Real providers differ.
- **Stand-in custody.** Credential custody is simulated with operating-system users and file permissions on one machine.
- **Trusted operator.** The operator role is trusted.
- **Bounded tests.** The test set is bounded. Passing it is not proof against attacks that were not tested.
- **No live clocks.** The demonstration measures outcomes, not production performance. Timings in the availability cases include test-harness process start-up.
