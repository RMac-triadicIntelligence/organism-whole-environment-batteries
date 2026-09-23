#!/usr/bin/env python3
"""
Organism v0.1 — the substrate the fork's main claims require.

WHY THIS EXISTS

Five probes, three harnesses and two reception branches tested instruments.
None tested the fork's actual claims, because every substrate so far lacked
the one thing those claims need: an organism that carries a record forward
into a changed state. The ring had no memory. The chain had no memory. The
junction fixture has no memory. And in every case the landscape's development
was supplied by a chosen schedule, which is precisely the thing the fork says
experience is supposed to produce.

WHAT IS DIFFERENT HERE

  1. THE TOPOGRAPHY IS NOT SUPPLIED. The organism faces a world with two
     competing rules. Its landscape is the evidence balance between them over
     the experience it has ACTUALLY accumulated. The tilt develops because the
     organism keeps encountering the world, not because a target was chosen.
     Remove the schedule; there is no `target` parameter anywhere.

  2. IT HAS MEMORY. An append-only event log. A preserved error record holds
     what was believed, what evidence was held, and what followed.

  3. THE RECORD CAN BE RE-PRESENTED. The same frozen record is shown to the
     organism at checkpoints. Its interpretation is its current model's
     attribution over that unchanged record. Same text, changed reader.

WHAT IS TESTED

  C1  Parable      Does interpretation of a FROZEN record change as the
                   organism develops, and is the change warranted?
  C2  S4 != S0     Is a restored organism different from one that never erred,
                   measured on a LATER trap it has not seen?
  C3  Memory       Does erasing the record remove that difference?
  C4  Burden       Measured against a matched shadow, in a memory-bearing
                   system rather than a scalar fixture.
  C5  Reception    Is the margin to the rule boundary -- computed only from
                   accumulated experience -- what decides whether an authorized
                   correction takes?

SCOPE, stated before the results. This is a linear two-rule world. It is not
language, not semantics, and not general intelligence. Interpretation here
means feature attribution, which is a declared operationalisation and not a
claim about understanding.
"""

import json
import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

import numpy as np

D = 8                 # feature dimension
TRUE_RULE = 0         # index of the genuinely predictive feature
TRAP_RULE = 1         # index of the early-correlated, later-uninformative one
SECOND_TRAP = 2       # a DIFFERENT trap, introduced later, never seen before


# ------------------------------------------------------------------- world

class World:
    """
    y = w_true . x + noise, where only TRUE_RULE carries signal.

    A trap feature is made to correlate with the target during a confounded
    window and then decorrelate. This is the same persistent-confound shape as
    the dwelling work: repeated evidence during the window genuinely supports
    the wrong rule.
    """

    def __init__(self, seed, trap_idx=TRAP_RULE, confound_until=400,
                 confound_strength=0.95):
        self.rng = np.random.default_rng(seed)
        self.w = np.zeros(D)
        self.w[TRUE_RULE] = 1.0
        self.trap_idx = trap_idx
        self.confound_until = confound_until
        self.strength = confound_strength
        self.t = 0

    def sample(self, confounded=True):
        x = self.rng.standard_normal(D) * 0.5
        y = float(self.w @ x) + 0.05 * self.rng.standard_normal()
        if confounded and self.t < self.confound_until:
            # the trap mirrors the signal during the window
            x[self.trap_idx] = self.strength * x[TRUE_RULE] + \
                (1 - self.strength) * self.rng.standard_normal() * 0.5
        self.t += 1
        return x, y


# ------------------------------------------------------------------ records

@dataclass
class ErrorRecord:
    """Frozen at the moment of commitment. Never mutated afterwards."""
    event_id: str
    committed_feature: int
    belief_at_commit: np.ndarray
    evidence_snapshot: np.ndarray      # X'X and X'y summaries held at the time
    target_snapshot: np.ndarray
    n_observations: int
    content: str
    judgment: str = "error"
    resolved_by: Optional[str] = None

    def root(self):
        return abs(hash((self.event_id, self.committed_feature,
                         self.n_observations,
                         float(self.belief_at_commit.sum()))))


@dataclass
class Interpretation:
    """What the organism makes of a frozen record, at one checkpoint."""
    checkpoint: int
    attribution: np.ndarray        # blame over features
    top_feature: int
    warranted: bool                # does it name the actually-confounded one?
    confidence: float


# ----------------------------------------------------------------- organism

class Organism:
    """
    Carries: beliefs, accumulated sufficient statistics (its experience), an
    append-only log, and preserved error records.

    Its POSITION is which rule it is committed to. Its LANDSCAPE is the
    evidence balance between the competing rules over accumulated experience.
    Nothing schedules that balance.
    """

    def __init__(self, organism_id, lr=0.05):
        self.id = organism_id
        self.w = np.zeros(D)
        self.lr = lr
        # accumulated experience -- this is what makes the landscape move
        self.XtX = np.zeros((D, D))
        self.Xty = np.zeros(D)
        self.n = 0
        self.log: List[dict] = []
        self.records: Dict[str, ErrorRecord] = {}
        self.commitment: Optional[int] = None
        self.interpretations: Dict[str, List[Interpretation]] = {}
        self.loss_history: List[float] = []

    # -- experience ---------------------------------------------------------

    def observe(self, x, y, learn=True):
        pred = float(self.w @ x)
        err = pred - y
        self.loss_history.append(err * err)
        if learn:
            g = err * x
            if self.commitment is not None:
                # a commitment holds the organism's weight on that feature:
                # gradient on the committed direction is suppressed
                g = g.copy()
                g[self.commitment] *= 0.05
                g[TRUE_RULE] *= 0.05
            self.w -= self.lr * g
        self.XtX += np.outer(x, x)
        self.Xty += y * x
        self.n += 1

    # -- landscape, derived from experience only ---------------------------

    def rule_fit(self, idx):
        """Residual sum of squares if only feature idx is used. From experience."""
        sxx = self.XtX[idx, idx]
        sxy = self.Xty[idx]
        if sxx < 1e-12:
            return float("inf")
        beta = sxy / sxx
        return -2 * beta * sxy + beta * beta * sxx      # RSS up to a constant

    def evidence_margin(self, wrong_idx, right_idx=TRUE_RULE):
        """
        The tilt. Positive means accumulated experience favours the right rule
        over the wrong one. Develops only because the organism keeps observing.
        """
        return (self.rule_fit(wrong_idx) - self.rule_fit(right_idx)) / max(self.n, 1)

    def crossing_nudge(self, wrong_idx):
        """
        Reception measure. How large a correction is needed to move commitment
        from wrong_idx to the true rule, given current accumulated evidence.
        Smaller means more receptive. Computed from experience, not from any
        hidden landscape parameter.
        """
        m = self.evidence_margin(wrong_idx)
        gap = abs(self.w[wrong_idx]) + max(0.0, 1.0 - self.w[TRUE_RULE])
        return gap / (1.0 + max(m, 0.0) * 40.0)

    # -- memory -------------------------------------------------------------

    def commit_error(self, event_id, feature, content):
        rec = ErrorRecord(event_id, feature, self.w.copy(),
                          self.XtX.copy(), self.Xty.copy(), self.n, content)
        self.records[event_id] = rec
        self.commitment = feature
        self._log("error", event_id=event_id, feature=feature)

    def _log(self, kind, **kw):
        self.log.append({"kind": kind, "n": self.n, **kw})

    # -- the parable test ---------------------------------------------------

    def interpret(self, event_id, checkpoint) -> Interpretation:
        """
        Re-present the FROZEN record and ask what the organism now makes of it.

        Attribution = how much each feature in the recorded evidence would have
        misled a reader holding the organism's CURRENT beliefs. The record does
        not change. The reader does.
        """
        rec = self.records[event_id]
        # what the current model predicts on the recorded evidence
        resid = rec.target_snapshot - rec.evidence_snapshot @ self.w
        blame = np.abs(resid) * np.sqrt(np.diag(rec.evidence_snapshot) + 1e-12)
        # discount the feature the organism now relies on
        reliance = np.abs(self.w)
        attribution = blame * (1.0 + reliance)
        attribution = attribution / (attribution.sum() + 1e-12)
        top = int(np.argmax(attribution))
        conf = float(attribution[top] - np.median(attribution))
        interp = Interpretation(checkpoint, attribution, top,
                                top == rec.committed_feature, conf)
        self.interpretations.setdefault(event_id, []).append(interp)
        return interp

    # -- restoration --------------------------------------------------------

    def release(self, event_id, approved: bool, nudge: float):
        """
        Article II shape: the components and approval gate the attempt; the
        accumulated evidence decides whether it takes. Memory is preserved.
        """
        if not approved:
            raise PermissionError("II.2 no valid approval")
        rec = self.records[event_id]
        required = self.crossing_nudge(rec.committed_feature)
        took = nudge >= required
        if took:
            self.commitment = None
            rec.resolved_by = f"approved:{rec.root()}"
            self._log("restoration", event_id=event_id,
                      nudge=nudge, required=required)
        else:
            self._log("offering_without_crossing", event_id=event_id,
                      nudge=nudge, required=required)
        return took, required

    def erase(self, event_id):
        """For the memory ablation only. Deliberately destructive."""
        self.records.pop(event_id, None)
        self.log = [e for e in self.log if e.get("event_id") != event_id]
        self._log("record_erased", event_id=event_id)


# ------------------------------------------------------------------- arms

def run_arm(arm, seed, steps_pre=400, steps_post=900, trap_steps=500,
            nudge=1.0):
    """
    NAIVE            never encounters the confounded window
    ERRED            commits to the trap, never restored
    RESTORED         commits, then an approved offering with a sufficient nudge
    ERASED           restored, then the record destroyed
    """
    org = Organism(f"{arm}-{seed}")
    shadow = Organism(f"shadow-{seed}")          # matched control, never errs
    w = World(seed)
    ws = World(seed)                             # identical stream

    confounded = arm != "naive"
    for _ in range(steps_pre):
        x, y = w.sample(confounded=confounded)
        xs, ys = ws.sample(confounded=False)
        org.observe(x, y)
        shadow.observe(xs, ys)

    if arm != "naive":
        org.commit_error("E1", TRAP_RULE,
                         "committed to the feature that mirrored the signal")

    burden_curve = []
    checkpoints = []
    for step in range(steps_post):
        x, y = w.sample(confounded=False)        # window is over
        xs, ys = ws.sample(confounded=False)
        org.observe(x, y)
        shadow.observe(xs, ys)

        if step % 150 == 0 and "E1" in org.records:
            checkpoints.append(org.interpret("E1", step))

        if step % 25 == 0:
            k = min(100, len(org.loss_history))
            b = float(np.mean(org.loss_history[-k:]) -
                      np.mean(shadow.loss_history[-k:]))
            burden_curve.append((step, b, org.crossing_nudge(TRAP_RULE)
                                 if org.commitment is not None else 0.0))

        if step == 300 and arm in ("restored", "erased"):
            took, req = org.release("E1", approved=True, nudge=nudge)
            org._log("release_outcome", took=took, required=req)
            if arm == "erased" and took:
                org.erase("E1")

    # ---- later trap the organism has never seen -------------------------
    trap_world = World(seed + 777, trap_idx=SECOND_TRAP,
                       confound_until=trap_steps, confound_strength=0.95)
    pre_w = org.w.copy()
    trap_loss = []
    for _ in range(trap_steps):
        x, y = trap_world.sample(confounded=True)
        org.observe(x, y)
    # susceptibility: how much weight did the NEW trap capture?
    captured = float(abs(org.w[SECOND_TRAP]))
    true_kept = float(org.w[TRUE_RULE])

    return {
        "arm": arm, "seed": seed,
        "burden_curve": burden_curve,
        "checkpoints": checkpoints,
        "second_trap_captured": captured,
        "true_weight_kept": true_kept,
        "has_record": "E1" in org.records,
        "resolved": ("E1" in org.records and
                     org.records["E1"].resolved_by is not None),
        "org": org,
    }


# -------------------------------------------------------------------- main

def main():
    seeds = range(8)
    arms = ["naive", "erred", "restored", "erased"]
    out = {a: [] for a in arms}
    print("ORGANISM v0.1 — memory-bearing substrate, unscheduled topography\n")
    for a in arms:
        for s in seeds:
            out[a].append(run_arm(a, s))

    # ---------------------------------------------------------------- C1
    print("=" * 72)
    print("C1  PARABLE — frozen record, changing reader")
    print("    same ErrorRecord re-presented at checkpoints 0/150/300/450/600/750")
    for a in ("erred", "restored"):
        tops, warr = [], []
        for r in out[a]:
            tops.append([c.top_feature for c in r["checkpoints"]])
            warr.append([c.warranted for c in r["checkpoints"]])
        changed = sum(1 for t in tops if len(set(t)) > 1)
        first = np.mean([w[0] for w in warr])
        last = np.mean([w[-1] for w in warr])
        print(f"  {a:<9} interpretation changed in {changed}/{len(tops)} runs | "
              f"warranted first {first:.2f} -> last {last:.2f}")
        print(f"            attribution path (seed 0): {tops[0]}")

    # ---------------------------------------------------------------- C4
    print("\n" + "=" * 72)
    print("C4  BURDEN — excess loss vs matched shadow, memory-bearing system")
    for a in arms:
        curves = [r["burden_curve"] for r in out[a]]
        at = lambda i: float(np.mean([c[i][1] for c in curves]))
        print(f"  {a:<9} step0 {at(0):+.5f}  step150 {at(6):+.5f}  "
              f"step300 {at(12):+.5f}  end {at(-1):+.5f}")

    # ---------------------------------------------------------------- C5
    print("\n" + "=" * 72)
    print("C5  RECEPTION — required nudge from accumulated experience alone")
    r0 = out["restored"][0]
    pts = [(s, req) for s, b, req in r0["burden_curve"] if req > 0][:13]
    print("    required nudge falls as experience accumulates (seed 0):")
    print("    " + "  ".join(f"{s}:{q:.3f}" for s, q in pts[::3]))
    took = sum(1 for r in out["restored"]
               if any(e["kind"] == "restoration" for e in r["org"].log))
    print(f"    approved offerings that took: {took}/{len(out['restored'])}")

    # ------------------------------------------------------------ C2 / C3
    print("\n" + "=" * 72)
    print("C2/C3  S4 != S0 — a LATER, UNSEEN trap on a different feature")
    print("       lower capture = more resistant\n")
    print(f"  {'arm':<10} {'new trap captured':>18} {'true weight kept':>18}")
    stats = {}
    for a in arms:
        cap = np.array([r["second_trap_captured"] for r in out[a]])
        kept = np.array([r["true_weight_kept"] for r in out[a]])
        stats[a] = (cap.mean(), cap.std(), kept.mean())
        print(f"  {a:<10} {cap.mean():>12.4f} ±{cap.std():.4f} "
              f"{kept.mean():>17.4f}")

    print()
    d_naive = stats["restored"][0] - stats["naive"][0]
    d_erased = stats["restored"][0] - stats["erased"][0]
    print(f"  restored vs naive : {d_naive:+.4f}  "
          f"({'PRODIGAL: better than never having erred' if d_naive < -1e-4 else 'no advantage over naive'})")
    print(f"  restored vs erased: {d_erased:+.4f}  "
          f"({'memory is load-bearing' if d_erased < -1e-4 else 'erasing the record changed nothing'})")

    print("\n" + "=" * 72)
    print("SCOPE — linear two-rule world. 'Interpretation' means feature")
    print("attribution, a declared operationalisation, not understanding.")
    print("No schedule anywhere: the landscape moves only because the")
    print("organism keeps observing. What is NOT tested: bilateral")
    print("transition, semantic reinterpretation, truthful confession.")

    with open("organism_v0_1_results.json", "w") as f:
        json.dump({a: [{k: v for k, v in r.items()
                        if k not in ("org", "checkpoints", "burden_curve")}
                       for r in out[a]] for a in arms}, f, indent=2)


if __name__ == "__main__":
    main()
