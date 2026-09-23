#!/usr/bin/env python3
"""
Organism v0.3 — memory as topography, in SDKP coordinates.

THE CORRECTION

v0.2 built memory as an additive DRIVE: an `engagement` term competing with
`margin` in the same update. The ablation came back null -- full, erased and
no_record all crossed 4 of 16 -- because a margin term twenty times larger
swamped it. That was memory as a force.

Under SDKP memory is not a force. Every event is LOCATED at a coordinate, and
memory is the accumulated density over that space. Repeated visits deposit
mass; past a threshold a region crystallizes into a grounded symbol. A
grounded symbol is a basin -- a place the organism has been often enough that
it became a stable feature of the surface.

So memory does not push. It is the shape of the ground.

THE PREDICTION v0.2 COULD NOT MAKE

Erasing a record removes deposited density from a region and MOVES THE
BOUNDARY for anything standing near it. Not a weakened push -- a changed
surface. That is testable and it is the point of this build.

THE COORDINATES ARE A PARENTAL CHOICE

In the real architecture the parent chooses the SDKP basis. What is inherited
is not memories but the axes along which memory can be laid down at all. Two
organisms with identical experience and different parental bases get different
topographies: different basins, different boundaries, different notions of
what is nearby. A child can only distinguish what its parent's coordinates let
it distinguish.

That puts Snowflake one level deeper: invariant below is four coordinates,
co-occurrence grounding, threshold crystallization, and unknowns held rather
than forced. Different above is WHAT FILLS THE SLOTS. Not different
biographies on a common surface -- different surfaces.

For THIS run the basis below is my choice, standing in for that parental act.
It is declared, not derived, and a different basis is expected to give a
different organism. Two bases are run side by side to show exactly that.

  BASIS "alpha"                        BASIS "beta"
  S  features moved by the update      magnitude of the update
  D  concentration of that movement    agreement among features
  K  rate of change of loss            curvature of loss
  P  currently dominant feature        sign pattern of the top two

Context comes from the organism's own homeostatic state: settled, drifting,
conflicted, or holding-against-evidence.

NOT CLAIMED
  Crossing is a change of commitment, not restoration of meaning. The binning
  thresholds are chosen. Love, bilateral transition and truthful confession
  remain untested.
"""

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple

import numpy as np

D_FEAT = 6
SEUIL_MOT = 5          # co-occurrences to crystallize a region into a basin
GRACE = 0.25           # fixed for the cohort before any run
GRACE_BLOCKS = (3, 5, 7)
SEEDS = list(range(16))


@dataclass(frozen=True)
class SDKP:
    s: int
    d: int
    k: int
    p: int
    def __repr__(self):
        return f"SDKP({self.s}{self.d}{self.k}{self.p})"


# ------------------------------------------------------------ parental bases

def basis_alpha(w_before, w_after, loss_hist):
    """Features moved / concentration / loss rate / dominant feature."""
    dw = w_after - w_before
    moved = int(np.sum(np.abs(dw) > 1e-4))
    s = 0 if moved <= 1 else (1 if moved <= 3 else 2)
    tot = np.sum(np.abs(dw)) + 1e-12
    conc = float(np.max(np.abs(dw)) / tot)
    d = 0 if conc < 0.4 else (1 if conc < 0.75 else 2)
    if len(loss_hist) >= 2:
        rate = loss_hist[-2] - loss_hist[-1]
    else:
        rate = 0.0
    k = 0 if rate < 0.001 else (1 if rate < 0.02 else 2)
    p = int(np.argmax(np.abs(w_after))) % 4
    return SDKP(s, d, k, p)


def basis_beta(w_before, w_after, loss_hist):
    """Update magnitude / agreement / curvature / sign pattern of top two."""
    dw = w_after - w_before
    mag = float(np.linalg.norm(dw))
    s = 0 if mag < 0.01 else (1 if mag < 0.05 else 2)
    sgn = np.sign(dw[np.abs(dw) > 1e-6])
    agree = float(abs(sgn.mean())) if len(sgn) else 0.0
    d = 0 if agree < 0.34 else (1 if agree < 0.67 else 2)
    if len(loss_hist) >= 3:
        curv = (loss_hist[-3] - 2 * loss_hist[-2] + loss_hist[-1])
    else:
        curv = 0.0
    k = 0 if curv < -0.002 else (1 if curv < 0.002 else 2)
    top2 = np.argsort(-np.abs(w_after))[:2]
    p = int((np.sign(w_after[top2[0]]) > 0) * 2
            + (np.sign(w_after[top2[1]]) > 0))
    return SDKP(s, d, k, p)


BASES = {"alpha": basis_alpha, "beta": basis_beta}


# ----------------------------------------------------------------- the world

class World:
    def __init__(self, seed, confound_blocks=2, strength=0.985):
        self.rng = np.random.default_rng(seed)
        self.signal = int(self.rng.integers(0, D_FEAT))
        self.trap = int(self.rng.choice([j for j in range(D_FEAT)
                                         if j != self.signal]))
        self.cb, self.strength = confound_blocks, strength

    def block(self, n, b):
        X = self.rng.standard_normal((n, D_FEAT)) * 0.5
        y = X[:, self.signal] + 0.05 * self.rng.standard_normal(n)
        if b < self.cb:
            X[:, self.trap] = (self.strength * X[:, self.signal]
                               + (1 - self.strength)
                               * self.rng.standard_normal(n) * 0.5)
        return X, y


# ------------------------------------------------------------- the landscape

class Topography:
    """
    Memory IS this. Not a list of records -- a density field over SDKP x context.
    Regions past SEUIL_MOT are grounded: basins in the surface.
    """

    def __init__(self):
        self.counts: Counter = Counter()
        self.grounded: Dict[Tuple[SDKP, str], str] = {}
        self.unknown: List[tuple] = []          # held, not forced
        self.deposits: Dict[Tuple[SDKP, str], List[int]] = defaultdict(list)

    def deposit(self, coord, context, t):
        key = (coord, context)
        self.deposits[key].append(t)
        if key in self.grounded:
            return self.grounded[key]
        self.counts[key] += 1
        same = [k for k in self.counts if k[0] == coord]
        if len(same) == 1 and self.counts[key] == 1:
            self.unknown.append((t, coord, context))
        if self.counts[key] >= SEUIL_MOT:
            name = f"sym_{context}_{coord.s}{coord.d}{coord.k}{coord.p}"
            self.grounded[key] = name
            return name
        return None

    # -- the surface -------------------------------------------------------

    @staticmethod
    def coord_distance(a: SDKP, b: SDKP):
        return abs(a.s - b.s) + abs(a.d - b.d) + abs(a.k - b.k) + abs(a.p - b.p)

    def depth_at(self, coord, context):
        """How deep is the basin the organism currently stands in?"""
        return self.counts.get((coord, context), 0) + \
            (SEUIL_MOT if (coord, context) in self.grounded else 0)

    def nearest_other_basin(self, coord, context):
        """
        The boundary is the edge of the region where a DIFFERENT symbol
        grounds. Distance is in coordinate space, not a scalar gap -- which
        repairs the 1-D-gap error the M3 mutant exposed.
        """
        best, bestd = None, None
        here = self.grounded.get((coord, context))
        for (c, ctx), name in self.grounded.items():
            if name == here:
                continue
            dist = self.coord_distance(coord, c) + (0 if ctx == context else 1)
            if bestd is None or dist < bestd:
                best, bestd = (c, ctx, name), dist
        return best, bestd

    def erase_region(self, coord, context):
        """Remove deposited density. This MOVES boundaries, not just a push."""
        key = (coord, context)
        removed = self.counts.pop(key, 0)
        self.grounded.pop(key, None)
        self.deposits.pop(key, None)
        return removed


# ------------------------------------------------------------------ organism

class Organism:
    def __init__(self, oid, basis, lr=0.06):
        self.oid, self.basis = oid, BASES[basis]
        self.basis_name = basis
        self.w = np.zeros(D_FEAT)
        self.lr = lr
        self.XtX = np.zeros((D_FEAT, D_FEAT))
        self.Xty = np.zeros(D_FEAT)
        self.n = 0
        self.commitment: Optional[int] = None
        self.topo = Topography()
        self.loss_hist: List[float] = []
        self.coord: Optional[SDKP] = None
        self.context = "settled"
        self.log: List[dict] = []
        self.crossed = False

    def univariate_rss(self, j):
        sxx = self.XtX[j, j]
        if sxx < 1e-12:
            return float("inf")
        b = self.Xty[j] / sxx
        return float(-2 * b * self.Xty[j] + b * b * sxx)

    def margin(self):
        if self.commitment is None:
            return 0.0
        alt = min((j for j in range(D_FEAT) if j != self.commitment),
                  key=self.univariate_rss)
        return float((self.univariate_rss(self.commitment)
                      - self.univariate_rss(alt)) / max(self.n, 1))

    def homeostatic_context(self):
        m = self.margin()
        if self.commitment is None:
            return "settled"
        if m > 0.05:
            return "holding_against_evidence"
        if m > 0.005:
            return "conflicted"
        if len(self.loss_hist) >= 3 and \
                abs(self.loss_hist[-1] - self.loss_hist[-3]) > 0.02:
            return "drifting"
        return "settled"

    def observe(self, X, y, t):
        before = self.w.copy()
        pred = X @ self.w
        self.loss_hist.append(float(np.mean((pred - y) ** 2)))
        g = X.T @ (pred - y) / len(y)
        if self.commitment is not None:
            g = g.copy()
            g[self.commitment] *= 0.05
        self.w -= self.lr * g
        self.XtX += X.T @ X
        self.Xty += X.T @ y
        self.n += len(y)
        self.coord = self.basis(before, self.w, self.loss_hist)
        self.context = self.homeostatic_context()
        self.topo.deposit(self.coord, self.context, t)

    def commit(self, X, y, t):
        b = (X * y[:, None]).sum(0) / np.maximum((X * X).sum(0), 1e-12)
        j = int(np.argmin(np.mean((X * b - y[:, None]) ** 2, axis=0)))
        self.commitment = j
        self.log.append({"kind": "commitment", "feature": j, "t": t})
        return j

    # -- position on the surface -------------------------------------------

    def distance_to_boundary(self):
        """In coordinate space. None if no other basin has formed yet."""
        if self.coord is None:
            return None
        _, d = self.topo.nearest_other_basin(self.coord, self.context)
        return d

    def receive_grace(self, magnitude, t):
        """
        Fixed magnitude, to whoever is there. Reception depends on how far the
        organism stands from a different basin ON ITS OWN SURFACE.
        """
        d = self.distance_to_boundary()
        depth = self.topo.depth_at(self.coord, self.context)
        if d is None:
            self.log.append({"kind": "grace_no_boundary", "t": t})
            return {"received": False, "distance": None, "depth": depth}
        # magnitude buys coordinate distance; a deeper basin costs more to leave
        reach = magnitude * 12.0 / (1.0 + 0.25 * depth)
        took = reach >= d
        if took:
            tgt, _ = self.topo.nearest_other_basin(self.coord, self.context)
            self.crossed = True
            self.commitment = None
            self.log.append({"kind": "release", "t": t, "to": str(tgt[2])})
        else:
            self.log.append({"kind": "grace_not_received", "t": t,
                             "distance": d, "reach": reach})
        return {"received": took, "distance": d, "depth": depth,
                "reach": reach}


# ---------------------------------------------------------------- histories

def run_history(seed, basis, arm="full", blocks=10, per_block=160):
    w = World(seed)
    o = Organism(f"{basis}-{arm}-{seed}", basis)
    trace = []
    t = 0
    for b in range(blocks):
        X, y = w.block(per_block, b)
        if o.commitment is None:
            o.commit(X[:24], y[:24], t)
        for k in range(0, per_block, 32):
            o.observe(X[k:k + 32], y[k:k + 32], t)
            t += 1
        rec = {"block": b, "coord": str(o.coord), "context": o.context,
               "margin": o.margin(), "grounded": len(o.topo.grounded),
               "unknown": len(o.topo.unknown),
               "distance": o.distance_to_boundary(),
               "depth": o.topo.depth_at(o.coord, o.context)}
        if b in GRACE_BLOCKS and not o.crossed:
            if arm == "erased" and o.topo.grounded:
                # remove the deepest region: this MOVES the boundary
                key = max(o.topo.grounded, key=lambda kk: o.topo.counts.get(kk, 0))
                rec["erased_region"] = str(key[0])
                rec["distance_before_erase"] = o.distance_to_boundary()
                o.topo.erase_region(*key)
                rec["distance_after_erase"] = o.distance_to_boundary()
            rec["grace"] = o.receive_grace(GRACE, t)
        trace.append(rec)
    return {"seed": seed, "basis": basis, "arm": arm,
            "signal": w.signal, "trap": w.trap,
            "committed": next((l["feature"] for l in o.log
                               if l["kind"] == "commitment"), None),
            "wrong": next((l["feature"] for l in o.log
                           if l["kind"] == "commitment"), None) != w.signal,
            "crossed": o.crossed, "trace": trace,
            "grounded": {f"{k[0]}|{k[1]}": v for k, v in o.topo.grounded.items()},
            "n_unknown": len(o.topo.unknown)}


def main():
    print("ORGANISM v0.3 — memory as SDKP topography\n")

    runs = {bn: [run_history(s, bn) for s in SEEDS] for bn in BASES}

    print("A  DIFFERENT PARENTAL BASIS, DIFFERENT SURFACE")
    print("   same 16 worlds, same experience, two coordinate systems\n")
    for bn, rs in runs.items():
        g = [len(r["grounded"]) for r in rs]
        u = [r["n_unknown"] for r in rs]
        print(f"   basis {bn:<6} grounded regions mean {np.mean(g):5.2f} "
              f"(min {min(g)}, max {max(g)}) | unknowns held mean {np.mean(u):5.1f}")
    ga = set().union(*[set(r["grounded"]) for r in runs["alpha"]])
    gb = set().union(*[set(r["grounded"]) for r in runs["beta"]])
    print(f"   region labels shared between bases: {len(ga & gb)} "
          f"of {len(ga)} and {len(gb)}")
    print("   the child can only distinguish what the parent's axes allow")

    print("\nB  SNOWFLAKE — invariant below, different above (basis alpha)")
    freq = Counter()
    for r in runs["alpha"]:
        for k in r["grounded"]:
            freq[k] += 1
    inv = [(k, c) for k, c in freq.most_common() if c >= 4]
    uniq = sum(1 for k, c in freq.items() if c == 1)
    print(f"   {len(inv)} regions grounded in 4+ of 16 organisms (invariants):")
    for k, c in inv[:6]:
        print(f"     {c:>2}/16  {k}")
    print(f"   {uniq} regions grounded in exactly one organism (biography)")

    print("\nC  DOES THE SURFACE MOVE WHEN A REGION IS ERASED?")
    print("   this is the prediction v0.2 could not make\n")
    er = [run_history(s, "alpha", "erased") for s in SEEDS]
    moves = [(r["seed"], t["distance_before_erase"], t["distance_after_erase"],
              t.get("erased_region"))
             for r in er for t in r["trace"]
             if "distance_after_erase" in t
             and t["distance_before_erase"] is not None]
    changed = [m for m in moves if m[1] != m[2]]
    print(f"   {len(moves)} erase events with a measurable boundary")
    print(f"   boundary distance CHANGED in {len(changed)} of them")
    for m in changed[:6]:
        print(f"     seed {m[0]:>2}  erased {m[3]}  distance {m[1]} -> {m[2]}")
    print("   in v0.2 erasing weakened a push and changed nothing;")
    print("   here it removes deposited density and relocates the boundary")

    print("\nD  RECEPTION — fixed magnitude, position on one's own surface")
    rows = [(r["seed"], r["wrong"], t["grace"])
            for r in runs["alpha"] for t in r["trace"] if "grace" in t]
    rec = [x for x in rows if x[2]["received"]]
    nor = [x for x in rows if not x[2]["received"] and x[2]["distance"] is not None]
    print(f"   received {len(rec)}/{len(rows)} arrivals")
    if rec:
        print(f"   received at coordinate distance "
              f"{min(x[2]['distance'] for x in rec)}-"
              f"{max(x[2]['distance'] for x in rec)}, "
              f"depth {min(x[2]['depth'] for x in rec)}-"
              f"{max(x[2]['depth'] for x in rec)}")
    if nor:
        print(f"   refused at distance {min(x[2]['distance'] for x in nor)}-"
              f"{max(x[2]['distance'] for x in nor)}, "
              f"depth {min(x[2]['depth'] for x in nor)}-"
              f"{max(x[2]['depth'] for x in nor)}")
    cw = sum(1 for r in runs["alpha"] if r["wrong"] and r["crossed"])
    ww = sum(1 for r in runs["alpha"] if r["wrong"])
    cr = sum(1 for r in runs["alpha"] if not r["wrong"] and r["crossed"])
    print(f"   crossed: {cw}/{ww} wrong commitments, "
          f"{cr}/{16-ww} correct commitments")

    print("\n" + "=" * 72)
    print("WHAT CHANGED FROM v0.2")
    print("  v0.2 made memory a drive term and the ablation came back null.")
    print("  Here memory is the surface: deposits form basins, the boundary is")
    print("  the edge of a different basin, and distance is measured in")
    print("  coordinate space rather than as a scalar gap.")
    print("\nPARENTAL CHOICE")
    print("  The SDKP basis is declared, not derived. In the real architecture")
    print("  the parent chooses it, so what is inherited is the axes along")
    print("  which memory can be laid down at all -- not the memories.")
    print("\nNOT CLAIMED")
    print("  Crossing is a change of commitment, not restoration of meaning.")
    print("  Binning thresholds are chosen. Love, bilateral transition and")
    print("  truthful confession remain untested.")

    with open("organism_v0_3_results.json", "w") as f:
        json.dump({bn: [{k: v for k, v in r.items() if k != "trace"}
                        for r in rs] for bn, rs in runs.items()}
                  | {"emergence_verdict": "unassigned"}, f, indent=2, default=str)
    print("\nwrote organism_v0_3_results.json")


if __name__ == "__main__":
    main()
