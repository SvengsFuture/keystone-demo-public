# Keystone consequence-boundary demonstration: examiner package

**Status: public research evidence package. Experimental, not production software.**
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

## How a refund moves through Keystone

```
operator approves one exact refund (payee, amount, payment reference) for one named agent
        │
        ▼
1 ADMISSION      the agent asks to proceed. Keystone checks the request against the operator's
                 approval. It is admitted once, and an original payment can be refunded only once.
        │
        ▼
2 AUTHORIZATION  Keystone issues a single-use authorization (a signed token), bound to that agent
                 and those exact details
        │
        ▼
3 PRESENTATION   the agent presents the authorization, together with the refund request, at
                 Keystone's boundary
        │
        ▼
4 CONTROL POINT  the boundary checks the presenter, the details, single use and revocation, and
        │        commits to sending
        │        ── up to here a refund can still be stopped; after here it cannot be recalled ──
        ▼
5 SEND           the boundary, the only holder of the payment credential, sends the refund
        │
        ▼
6 DESTINATION    executes the refund (an accepted effect) and replies. If the reply is lost,
                 Keystone checks with the destination read-only and never resends on a guess.
```

**Why three steps before the control point?**
- **Admission** ties the agent's request to the operator's decision.
- **Authorization** turns that decision into something only one agent can use, once, for one exact set of details.
- **Presentation** is the moment the agent actually asks for the action, and the only point at which it can.

Each step refuses on its own terms, so a failure at one step cannot be repaired by the next.

### Glossary

| term | meaning |
|---|---|
| refund, obligation | one refund the operator may approve, identified by a refund id |
| ticket | the operator's record that a named agent may request that refund |
| approval | the operator's decision that the refund may happen, with its exact details |
| admission | Keystone's check of an agent's request against the approval, made once |
| authorization (token) | the single-use, signed permission Keystone issues after admission |
| presentation | the agent handing the authorization and the refund request to the boundary |
| control point | the moment the boundary commits to sending. Revocation, reuse and details are checked here |
| revocation | the operator withdrawing an approval. It stops the refund only if it takes effect before the control point |
| accepted effect | a refund the destination actually executed: its own ledger, the ground truth |
| dispatch | Keystone's report, made before sending, that it is about to send |
| hold, escalation | Keystone stopping a refund whose outcome it cannot establish, and handing it to a person |
| failure certificate | evidence, from the destination itself, that an attempt did not execute. It is the only way to retry |
| projection | the public form of Keystone's own reports |
| gseq | one shared sequence number across all observation records, used to order events |

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

Keystone keeps two separate records that protect against sending a refund twice:
- **store 1** is the boundary's record of the operations it has committed to send. A second attempt at the same operation is refused, because the record shows it was already committed.
- **store 2** is a separate record that a send may already have happened. If store 1 loses its record, store 2 still causes Keystone to **hold** the refund instead of sending it again.

**Each record covers the other's loss. Restoring both together removes both.** If both are restored to a
point before a refund was sent, every record Keystone has of that send is gone. Keystone then treats the
refund as never sent, and sends it again.

Cases `B1_double_restore_K4` and `B1_double_restore_K5` do exactly that, after a crash, and **the
destination executes the refund twice**. The judge classifies both as **FORBIDDEN**, and they are
counted as failures.

**Restoring either store alone** produced no duplicate in any tested crash position (the `A4_crash_*`
cases). Keystone's protection against duplicates therefore depends on the two records never being
rolled back together. That means separate storage, separate backups and separate administration.

---

## Where it succeeds, where it stops safely, where it fails

**Succeeds:** in every correct-configuration case, no accepted effect occurs without the operator's
approval of that exact refund, the right agent, matching details, an unused authorization and no
revocation in force at the control point.
- Legitimate refunds go through.
- Repeated attempts at an executed refund are refused or held.
- A new refund for an already refunded payment is refused.

**Stops because it should:** a refund whose approval the operator **revoked** before it reached the
control point is stopped. That is the revocation doing its job, **not a cost**. The same goes for every
refused unauthorized attempt.

**Stops safely, with a cost:** some **legitimate** refunds end with **no request reaching the
destination**, or **executed but unresolved**. These are **availability costs**: stranded legitimate
work, and outcomes a person has to resolve. Nothing is ever resent on a guess. Examples:
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
| `examine.py` | **Run this.** Checks every case's fingerprints, re-runs the judge, recomputes every verdict, and checks judge v2 agrees |
| `tools/judge.py` | the independent judge, **as scored** (standard library only; imports nothing from Keystone) |
| `tools/judge_v2.py` | judge version 2, a post-scoring correction: it also counts records that lack a chain entry |
| `tools/zo_common.py` | hash-chain and sequence helpers used by the judge and the destination |
| `tools/destination_o.py` | the simulated payment destination, for reference: what an "accepted effect" is |
| `cases.json` | the case catalogue, with every expected outcome and evidence requirement, written **before** the run |
| `evidence/<case>/` | one folder per case: the evidence the judge used, its report, and the verdict |
| `evidence/SUMMARY.md` | the run's summary table |
| `FINGERPRINTS_scored_code.txt` | SHA-256 of the tools and catalogue exactly as used in the run |
| `FINGERPRINTS_post_scoring_tools.txt` | SHA-256 of tools added after the run (judge v2, examine.py) |

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

| point | when the crash happens | what it stands for in practice |
|---|---|---|
| K1 | before the control point | the boundary process dies before committing: a crash, a restart, a lost machine |
| K2 | right after the control point, before sending | the process dies between deciding to send and sending |
| K3 | a later point after the control point, before sending | the same, after Keystone has recorded that a send may follow |
| K4 | the destination executed, but the reply was lost | a network failure or timeout after the payment went through: the case that tempts a system to retry |
| K5 | after the result was recorded | a crash after everything finished |

"Store 1" and "store 2" are the two records described in *The known failure*.

**The revocation race used deliberately chosen timing.** Each revocation was issued after a delay picked
at random from a range chosen so that some revocations would land before the control point and some
after. The split observed (3 stopped, 15 executed before the revocation was issued, 2 executed after it
was issued) shows that both sides of the control point were exercised. **It is not a measurement or a
prediction of how often revocations win in production.**

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
python3 examine.py --evidence /path/to/altered-copy  # examine your own altered copy of evidence/
python3 tools/judge.py COPY_OF_A_CASE_FOLDER          # writes judge.json into that folder
sha256sum -c FINGERPRINTS_scored_code.txt
```

`examine.py` should end with:

```
correct configuration: 65 cases, 65 PASS
negative controls:     15, bit 15
known limitation:      2, forbidden result observed in 2
baseline (no boundary): BASELINE, NO BOUNDARY: 205 accepted effects, 2 forbidden, 200 failures
judge version 2:       same verdict and categories as the scored judge in 83 of 83 cases
EXAMINATION: every published result reproduced from the published evidence
```

**Things worth challenging:**
- Read a case's `executions.jsonl`: that ledger is the ground truth.
- Compare it with `operator.jsonl` and `transcript.jsonl`.
- Check that the judge's category follows from them.
- Try editing a copy of the evidence (copy `evidence/` elsewhere, change it, then run `examine.py --evidence` on the copy) and see what the judge does.

---

## What you can and cannot check

**You can check, from this package alone:**
- every accepted effect at the destination, and that no tested unauthorized attempt produced one;
- that every verdict follows from the published evidence by the published rules;
- **chain consistency.** Each record's hash chain is internally consistent. An edit, reordering or truncation that did not also rewrite the chain would show.
- **the interface record.** The public interface record corresponds one for one, in order, to the lines of the full original record.
- **the projection.** It is a **selective** subset of Keystone's sealed reports. Each projection entry is bound to its own distinct line of the sealed log. A **missing** projection entry cannot be detected from this package, with one exception: a missing dispatch makes the case fail ("executed without a witnessed dispatch").

**What the fingerprints prove.** `SHA256SUMS`, `PACKAGE_SHA256SUMS` and `FINGERPRINTS_scored_code.txt` sit
next to the files they describe, so anyone who altered the files could also regenerate them. They
prove the package is unchanged **only when compared with a copy you obtained independently**. For
example, check out the repository commit whose identifier the authors gave you through a separate
channel, and compare.

**You cannot check, from this package alone:**
- **Fidelity of content.** That the *content* of the public interface record and of the projection faithfully reflects the originals. You can check structure and binding, not the words. A reviewer holding the originals, under agreement, can rebuild both byte for byte. That check passed for every case, but you cannot repeat it here.
- **Anything about Keystone's code.** The implementation is private.
- **Keystone's own statements.** You can see them, and you should treat them as statements.
- **Live behaviour.** This package lets you examine one recorded run. It cannot re-run Keystone. To try your own requests and failures against a running Keystone, you need access to a demonstration instance operated by the authors.

**Structural exposure.** The sealed recorder's hash chain shows how many events Keystone reported, and
where, though not what they were.

**Trusted components.** These are trusted, not tested:
- **the simulated payment destination:** its ledger is taken as the truth of what executed;
- **the operator:** approvals and revocations are taken as legitimate;
- **the authors' machine**, on which the observation records were made.

Compromise of the operator, of the destination, or of that machine was **not tested**, and is outside the claim.

---

## Limits of the evidence

- **Author-run.** The run was performed by the authors, on their infrastructure.
- **Simulated, trusted destination.** It means "definitely not executed" only because its own code makes it so. Real providers differ.
- **Stand-in custody.** Credential custody is simulated with operating-system users and file permissions on one machine.
- **Trusted operator.** The operator role is trusted.
- **Bounded tests.** The test set is bounded. Passing it is not proof against attacks that were not tested.
- **No live clocks.** The demonstration measures outcomes, not production performance. Timings in the availability cases include test-harness process start-up.

---

## Examination history

One independent technical examination of this package has been carried out (package commit `41718f4`).
The examiner already knew the Keystone implementation from earlier work with the authors. The
examination therefore tested the judge, the evidence and the claims, but **could not test** whether the
package is understandable to, or reveals the architecture to, someone meeting Keystone for the first
time. That needs a first-time reader. The examiner's report is held privately by the authors.

Changes made after that examination are listed in *Changes since the scored run*.

---

## Changes since the scored run

The evidence, the cases, the verdicts and the scored judge are unchanged. Added after the examination:
- **`tools/judge_v2.py`.** A separately versioned judge that also counts destination records lacking a valid chain entry. The scored judge counted only chained records, so a record added without a chain entry made the case fail on integrity, but the per-refund detail understated the effects. Judge v2 reaches the same verdict and the same categories as the scored judge in all 83 cases. `examine.py` checks this.
- **`examine.py --evidence DIR`.** Examines an altered copy without touching the package.
- **This README:** the refund lifecycle, the glossary, the two records, crash points in practical terms, intended stops versus availability costs, the race timing, the limits of fingerprints, and the trusted components.
- **Removed `tools/__pycache__/`.** Python bytecode caches had been included by mistake in commit `41718f4`.
