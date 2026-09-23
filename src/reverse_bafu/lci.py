"""One factorised technosphere; cumulative inventories and their flow-by-flow comparison.

No impact assessment anywhere: two inventories are compared flow by flow (relative deviation per
elementary flow), so the verdict does not depend on a characterisation method or on how the 25 EF
categories are weighted against each other."""

from __future__ import annotations

import numpy as np
import scipy.optimize as so
import scipy.sparse.linalg as spl
import bw2calc as bc
import bw2data as bd


class System:
    """Build the matrices once for a demand and reuse the LU factorisation for every column."""

    def __init__(self, demand_activity):
        self.lca = bc.LCA({demand_activity.id: 1})
        self.lca.lci()
        self.A = self.lca.technosphere_matrix.tocsc()
        self.B = self.lca.biosphere_matrix.tocsr()
        self.lu = spl.splu(self.A)
        self.n_flows = self.B.shape[0]
        self._groups: dict[tuple[str, str], list[int]] | None = None

    def cumulative(self, activity_ids: list[int]) -> np.ndarray:
        """B A^-1 e_j for each activity: columns of cumulative elementary flows."""
        D = np.zeros((self.A.shape[1], len(activity_ids)))
        for j, i in enumerate(activity_ids):
            D[self.lca.dicts.activity[i], j] = 1.0
        return np.asarray(self.B @ self.lu.solve(D))

    @property
    def groups(self) -> dict[tuple[str, str], list[int]]:
        """Flow rows grouped by (unit, top-level compartment): "kilogram/air", "square meter/land
        use", "kilo Becquerel/air", … About 30 groups over the ~1,900 flows."""
        if self._groups is None:
            g: dict[tuple[str, str], list[int]] = {}
            for row in range(self.n_flows):
                node = self.flow_node(row)
                cats = node.get("categories") or ()
                top = str(cats[0]).lower().replace("emissions to ", "").replace("resources from ", "") if cats else ""
                g.setdefault((node.get("unit", ""), top), []).append(row)
            self._groups = g
        return self._groups

    def fit_weights(self, target: np.ndarray, model: np.ndarray, determined: np.ndarray | None = None) -> np.ndarray:
        """Row weights for the calibration: relative error per flow (``relative_weights``), divided
        by sqrt(flows in the group), so the objective is the sum over (unit, compartment) groups of
        each group's mean squared relative error. Every flow counts equally within its group and
        every group counts equally: the ~1,200 flows of "kilogram/emissions" do not outvote land
        use, water or radioactivity. ``determined`` (``determined_flows``) gives round-off flows
        weight 0; their relative error is noise.

        Until 2026-09 the groups were normalised by the sum of their weights instead. That sum is
        set by the group's smallest flow, so a group counted in proportion to its tiniest value:
        "kilogram/emissions" (CO2 and ~1,200 others) weighed 1e-58 of a single land-use flow, and
        the fit saw ~20 of ~1,670 flows."""
        base = relative_weights(target, model)
        if determined is not None:
            base = base * determined
        w = np.zeros_like(base)
        for rows in self.groups.values():
            n = int((base[rows] > 0).sum())
            if n:
                w[rows] = base[rows] / np.sqrt(n)
        return w

    def flow_row(self, database: str, code: str) -> int | None:
        return self.lca.dicts.biosphere.get(bd.get_node(database=database, code=code).id)

    def flow_node(self, row: int):
        return bd.get_node(id=self.lca.dicts.biosphere.reversed[row])

    def flow_key(self, row: int) -> tuple[str, str]:
        node = self.flow_node(row)
        return node["database"], node["code"]

    def flow_label(self, row: int) -> str:
        node = self.flow_node(row)
        cats = node.get("categories") or ()
        return f"{node['name']} [{'/'.join(str(c) for c in cats[:2])}] ({node.get('unit', '')})"


def solve_weighted(A: np.ndarray, y: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    """min |A x - y| subject to lo <= x <= hi, for the weighted calibration system.

    Columns and right-hand side are scaled to unit norm first, and the solver is an active-set one
    (NNLS when the only bound is x >= 0, BVLS otherwise). The weighted matrix mixes "a unit of
    plant" with "a kg of material" (condition numbers up to 1e37); lsq_linear's default
    trust-region method stopped early on it with an absolute tolerance, in 14 of the 100 oracle
    benchmark cases at an objective 1e2-1e13 above that of the true amounts."""
    cs = np.linalg.norm(A, axis=0)
    cs[cs == 0] = 1.0
    rs = np.linalg.norm(y) or 1.0
    if np.all(lo == 0) and np.all(np.isinf(hi)):
        x = so.nnls(A / cs, y / rs, maxiter=50 * A.shape[1] + 1000)[0]
    else:
        x = so.lsq_linear(A / cs, y / rs, bounds=(lo * cs / rs, hi * cs / rs), method="bvls", max_iter=20000).x
    return x / cs * rs


def relative_weights(target: np.ndarray, model: np.ndarray) -> np.ndarray:
    """Row weights for a least-squares fit on flows: 1 / max(|target|, |model|) per flow, so every
    flow present in either inventory counts by its relative error and none by its unit or size
    (a kg of CO2 and a mg of a dioxin are the same equation). Flows absent from both get 0."""
    ref = np.maximum(np.abs(target), np.abs(model))
    w = np.zeros_like(ref)
    nz = ref > 0
    w[nz] = 1.0 / ref[nz]
    return w


def determined_flows(sys_: "System", activity_id: int, tol: float = 1e-2) -> np.ndarray:
    """Which flows of ``B·A⁻¹·e`` the arithmetic actually pins down.

    A cumulative inventory spans ~25 orders of magnitude, and the sparse solve carries an
    absolute error set by the largest entries of the scaling vector. Flows far below that
    floor come out of the solve as round-off: their value is not determined by the data. The
    test is direct rather than a magnitude threshold - take one step of iterative refinement
    and keep the flows that barely move. On the BAFU inventory this excludes ~120 of ~1,790
    flows per process, and the excluded ones move by 100 % under refinement while the kept
    ones move by ~1e-10. Unlike a magnitude cutoff it keeps genuine trace emissions (dioxins,
    benzo[a]pyrene, mercury), which are tiny but well determined.
    """
    D = np.zeros(sys_.A.shape[1])
    D[sys_.lca.dicts.activity[activity_id]] = 1.0
    s = sys_.lu.solve(D)
    s2 = s + sys_.lu.solve(D - sys_.A @ s)               # one refinement step
    t1, t2 = sys_.B @ s, sys_.B @ s2
    with np.errstate(divide="ignore", invalid="ignore"):
        move = np.where(np.abs(t1) > 0, np.abs(t2 - t1) / np.maximum(np.abs(t1), 1e-300), 0.0)
    return move <= tol


def flow_agreement(target: np.ndarray, model: np.ndarray, scored: np.ndarray | None = None) -> dict:
    """Flow-by-flow comparison of two cumulative inventories. ``delta`` is model/target − 1 per
    flow present in the target (NaN where the target is 0); the summary counts flows, not impact."""
    nz = target != 0
    with np.errstate(divide="ignore", invalid="ignore"):
        delta = np.where(nz, model / target - 1, np.nan)
    # ``scored``: restrict the counts to the flows the solve determines (``determined_flows``).
    # Everything the target has is still reported as n_target; n_excluded says how many of those
    # carry no information, so the two numbers can always be reconciled.
    keep = nz if scored is None else (nz & scored)
    d = np.abs(delta[keep])
    return {
        "n_scored": int(keep.sum()),
        "n_excluded": int((nz & ~keep).sum()),
        "n_target": int(nz.sum()),                                   # flows present in the target
        "n_missing": int((keep & (model == 0)).sum()),                 # in the target, not in the model
        "n_extra": int((~nz & (model != 0)).sum()),                  # in the model, not in the target
        "within_10pct": int((d <= 0.10).sum()), "within_20pct": int((d <= 0.20).sum()),
        "within_50pct": int((d <= 0.50).sum()), "beyond_100pct": int((d > 1.0).sum()),
        "median_abs_delta": float(np.median(d)) if d.size else float("nan"),
        "delta": delta,
    }


def top_flow_agreement(target: np.ndarray, model: np.ndarray, rows: list[int], k: int = 50) -> dict:
    """Agreement over the ``k`` largest flows of one unit. A rebuilt process with a handful of
    explicit inputs carries the flows the report names and misses the long tail of trace flows from
    the background chains, so the share over all flows and the share over the large ones are two
    different statements and both belong in the summary."""
    top = sorted((r for r in rows if target[r] != 0), key=lambda r: -abs(target[r]))[:k]
    if not top:
        return {"n": 0, "within_10pct": 0, "median_abs_delta": float("nan")}
    d = np.abs(np.array([model[r] / target[r] - 1 for r in top]))
    return {"n": len(top), "within_10pct": int((d <= 0.10).sum()), "median_abs_delta": float(np.median(d))}


def mass_coverage(target: np.ndarray, model: np.ndarray, rows: list[int], tol: float = 0.10) -> float:
    """Share of the target's total kilogram mass that sits in flows the model gets within ``tol``.
    A count over flows treats a kg of CO2 and a microgram of a trace metal alike; this says how much
    of the inventory, by mass, the rebuilt process actually reproduces."""
    tot = sum(abs(target[r]) for r in rows)
    if not tot:
        return float("nan")
    ok = sum(abs(target[r]) for r in rows if target[r] and abs(model[r] / target[r] - 1) <= tol)
    return ok / tot


def contribution_breadth(target: np.ndarray, contribution: np.ndarray, threshold: float = 0.01) -> float:
    """Share of the target's flows to which ``contribution`` supplies at least ``threshold`` of the
    amount — an impact-free measure of how much of an inventory an input explains."""
    nz = target != 0
    if not nz.any():
        return 0.0
    return float((np.abs(contribution[nz] / target[nz]) >= threshold).mean())
