"""Benchmark the reconstruction on synthetic aggregated datasets with known ground truth.

Every BAFU unit process can be turned into a "system terminated" lookalike: its cumulative
inventory B·A⁻¹·e is exactly what an ecoSpold type=2 export of it would contain. The real
inputs are then the ground truth, and the pipeline's calibration step can be scored on how
much of the structure and the amounts it recovers under different evidence levels:

    oracle       the true input list is known, amounts are not (fixed-list NNLS)
    bounded      list known, amounts known to a factor of 2 (report ranges)
    partial      30 % of the inputs are missing from the list (a report that omits minor lines)
    distractors  list known plus 10 plausible wrong candidates (an LLM over-proposing inputs)
    blind        no list: every process used >= 30 times is a candidate (field-agnostic S4)

Direct elementary flows of the process are given in every scenario except ``blind``.
Output: results/benchmark/<name>.csv (one row per case and scenario) and <name>.md (summary).
"""

from __future__ import annotations

import csv
import random
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import scipy.optimize as so
import bw2data as bd

from . import db
from .lci import System

SCENARIOS = ("oracle", "bounded", "partial", "distractors", "blind")


def pick_cases(n: int, seed: int, min_inputs: int = 3, max_inputs: int = 30) -> list[dict]:
    """Stratified sample of unit processes: round-robin over BAFU top-level categories."""
    rng = random.Random(seed)
    by_cat: dict[str, list[dict]] = defaultdict(list)
    agg = db.aggregated_codes()
    for key, act in bd.Database(db.INVENTORY_DB).load().items():
        if key[1] in agg or act["name"].lower().startswith("xx"):
            continue
        ex = act.get("exchanges", [])
        techno = [e for e in ex if e.get("type") == "technosphere" and tuple(e["input"]) != key]
        bio = [e for e in ex if e.get("type") == "biosphere"]
        if not (min_inputs <= len(techno) <= max_inputs):
            continue
        m = re.search(r"BAFU category: (.+?) /", act.get("comment", ""))
        by_cat[m.group(1) if m else "?"].append(
            {"code": key[1], "name": act["name"], "location": act.get("location", ""), "category": m.group(1) if m else "?",
             "inputs": {tuple(e["input"]): e["amount"] for e in techno}, "direct": {tuple(e["input"]): e["amount"] for e in bio}})
    cats = sorted(by_cat)
    for c in cats:
        by_cat[c].sort(key=lambda x: x["code"])  # database load order is not guaranteed; sort before shuffling
        rng.shuffle(by_cat[c])
    cases: list[dict] = []
    while len(cases) < n and any(by_cat.values()):
        for c in cats:
            if by_cat[c] and len(cases) < n:
                cases.append(by_cat[c].pop())
    return cases


class Bench:
    def __init__(self, sys_: System, ids: dict[tuple, int], used: Counter):
        self.sys = sys_
        self.ids = ids
        self.used = used
        self._col: dict[int, np.ndarray] = {}
        self.blind_pool = [k for k, n in used.items() if n >= 30]

    def col(self, act_id: int) -> np.ndarray:
        if act_id not in self._col:
            self._col[act_id] = self.sys.cumulative([act_id])[:, 0]
        return self._col[act_id]

    def direct_vector(self, direct: dict) -> np.ndarray:
        v = np.zeros(self.sys.n_flows)
        for key, amt in direct.items():
            row = self.sys.lca.dicts.biosphere.get(bd.get_node(database=key[0], code=key[1]).id)
            if row is not None:
                v[row] += amt
        return v

    def fit(self, target: np.ndarray, cand: list[tuple], lo: np.ndarray, hi: np.ndarray, direct: np.ndarray) -> np.ndarray:
        M = np.column_stack([self.col(self.ids[k]) for k in cand])
        w = self.sys.flow_weights(target)
        rows = np.where(w > 0)[0]
        res = so.lsq_linear(w[rows, None] * M[rows], w[rows] * (target - direct)[rows], bounds=(lo, hi), max_iter=5000)
        return res.x, M

    def run_case(self, case: dict, scenario: str, rng: random.Random) -> dict:
        truth = case["inputs"]
        keys = list(truth)
        target = self.sys.cumulative([self.ids[(db.INVENTORY_DB, case["code"])]])[:, 0]
        direct = np.zeros(self.sys.n_flows) if scenario == "blind" else self.direct_vector(case["direct"])
        if scenario == "oracle":
            cand = keys
        elif scenario == "bounded":
            cand = keys
        elif scenario == "partial":
            # drop the 30 % of inputs with the smallest climate contribution (what a report omits)
            cc = self.sys.cf[[i for i, m in enumerate(self.sys.methods) if m[2] == "Climate change"][0]]
            contrib = {k: abs(cc @ self.col(self.ids[k]) * truth[k]) for k in keys}
            keep = sorted(keys, key=lambda k: -contrib[k])[: max(1, round(0.7 * len(keys)))]
            cand = keep
        elif scenario == "distractors":
            pool = [k for k in self.blind_pool if k not in truth and k != (db.INVENTORY_DB, case["code"])]
            cand = keys + rng.sample(pool, min(10, len(pool)))
        else:  # blind
            cand = [k for k in self.blind_pool if k != (db.INVENTORY_DB, case["code"])]
        n = len(cand)
        lo, hi = np.zeros(n), np.full(n, np.inf)
        if scenario == "bounded":
            lo = np.array([0.5 * truth[k] for k in cand]); hi = np.array([2.0 * truth[k] for k in cand])
        t0 = time.time()
        x, M = self.fit(target, cand, lo, hi, direct)
        explicit = M @ x + direct
        s_t, s_e = self.sys.scores(target), self.sys.scores(explicit)
        with np.errstate(divide="ignore", invalid="ignore"):
            delta = np.where(s_t != 0, s_e / s_t - 1, np.nan) * 100
        residual = target - explicit
        s_r = self.sys.scores(residual)
        with np.errstate(divide="ignore", invalid="ignore"):
            res_share = np.abs(np.where(s_t != 0, s_r / s_t, np.nan)) * 100
        # structure: judged by impact, not by coefficient size. An input is "material" when its true
        # contribution reaches 1 % of the target score in some category; a candidate counts as chosen
        # when its fitted contribution does.
        def material(col: np.ndarray, amount: float) -> bool:
            with np.errstate(divide="ignore", invalid="ignore"):
                share = np.abs(np.where(s_t != 0, (self.sys.cf @ (col * amount)) / s_t, 0))
            return bool(np.nanmax(share) >= 0.01)
        cols = {k: M[:, i] for i, k in enumerate(cand)}
        true_material = {k for k in truth if k in cols and material(cols[k], truth[k])} | {k for k in truth if k not in cols}
        chosen = {k for i, k in enumerate(cand) if material(cols[k], x[i])}
        tp = len(chosen & true_material); fp = len(chosen - set(truth)); fn = len(true_material - chosen)
        ratios = [x[i] / truth[k] for i, k in enumerate(cand) if k in true_material and truth[k]]
        within20 = sum(1 for r in ratios if 0.8 <= r <= 1.2)
        return {
            "code": case["code"], "name": case["name"], "category": case["category"], "n_true_inputs": len(truth), "n_material_inputs": len(true_material),
            "scenario": scenario, "n_candidates": n, "n_chosen": len(chosen), "true_positives": tp, "false_positives": fp, "false_negatives": fn,
            "amounts_within_20pct": f"{within20}/{len(ratios)}", "amount_ratio_median": float(np.median(ratios)) if ratios else float("nan"),
            "score_median_abs_delta_pct": float(np.nanmedian(np.abs(delta))), "score_max_abs_delta_pct": float(np.nanmax(np.abs(delta))),
            "categories_within_10pct": int(np.nansum(np.abs(delta) <= 10)), "climate_delta_pct": float(delta[[i for i, m in enumerate(self.sys.methods) if m[2] == "Climate change"][0]]),
            "residual_share_median_pct": float(np.nanmedian(res_share)), "seconds": round(time.time() - t0, 2),
        }


def run(n: int, seed: int, scenarios: list[str], name: str, out_dir: Path = Path("results/benchmark")) -> Path:
    rng = random.Random(seed)
    cases = pick_cases(n, seed)
    print(f"{len(cases)} cases over {len(set(c['category'] for c in cases))} categories", file=sys.stderr)
    acts = bd.Database(db.INVENTORY_DB).load()
    ids = {k: bd.get_node(database=k[0], code=k[1]).id for k in acts}
    used: Counter = Counter()
    for key, act in acts.items():
        for e in act.get("exchanges", []):
            if e.get("type") == "technosphere" and tuple(e["input"]) != key:
                used[tuple(e["input"])] += 1
    sys_ = System(bd.get_node(database=db.INVENTORY_DB, code=cases[0]["code"]))
    bench = Bench(sys_, ids, used)
    rows = []
    for i, case in enumerate(cases, 1):
        for sc in scenarios:
            rows.append(bench.run_case(case, sc, rng))
        print(f"  {i}/{len(cases)} {case['name'][:50]} [{case['category']}]", file=sys.stderr)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"{name}.csv"
    with csv_path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    # summary
    L = [f"# Benchmark `{name}`: {len(cases)} synthetic aggregated datasets, seed {seed}", "",
         "Ground truth = BAFU unit processes (3-30 inputs, stratified over categories); target = their cumulative inventory.", "",
         "| scenario | median \\|Δ score\\| | categories within ±10 % (of 25) | climate \\|Δ\\| median | material amounts within ±20 % | material inputs chosen / true | false pos. | false neg. | residual share median |",
         "|---|---|---|---|---|---|---|---|---|"]
    for sc in scenarios:
        R = [r for r in rows if r["scenario"] == sc]
        w20 = [tuple(map(int, r["amounts_within_20pct"].split("/"))) for r in R]
        L.append(f"| {sc} | {np.median([r['score_median_abs_delta_pct'] for r in R]):.1f} % | {np.median([r['categories_within_10pct'] for r in R]):.0f} | "
                 f"{np.median([abs(r['climate_delta_pct']) for r in R]):.1f} % | {sum(a for a, _ in w20)}/{sum(b for _, b in w20)} | "
                 f"{np.median([r['n_chosen'] for r in R]):.0f} / {np.median([r['n_material_inputs'] for r in R]):.0f} | {np.median([r['false_positives'] for r in R]):.0f} | "
                 f"{np.median([r['false_negatives'] for r in R]):.0f} | {np.median([r['residual_share_median_pct'] for r in R]):.1f} % |")
    L += ["", "Medians over cases. 'Material' inputs are those whose true contribution reaches 1 % of the target score in some category. `partial` removes the 30 % of inputs with the smallest climate contribution before fitting; "
          "`distractors` adds 10 random frequently-used processes; `blind` offers every process used ≥ 30 times and no direct flows.", ""]
    md_path = out_dir / f"{name}.md"
    md_path.write_text("\n".join(L) + "\n")
    print("\n".join(L[4:4 + 2 + len(scenarios)]))
    print(f"\n-> {csv_path}, {md_path}")
    return md_path
