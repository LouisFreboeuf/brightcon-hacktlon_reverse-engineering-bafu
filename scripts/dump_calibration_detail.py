import json, random, time, warnings
from collections import Counter
from pathlib import Path
import numpy as np
import bw2data as bd
warnings.filterwarnings("ignore")

from reverse_bafu import db, benchmark
from reverse_bafu.benchmark import Bench, pick_cases
from reverse_bafu.lci import System, flow_agreement, contribution_breadth

N, SEED = 10, 7
SCEN = ["oracle", "bounded", "partial", "distractors"]
db.set_project("bafu-2026-bench")

rng = random.Random(SEED)                      # same stream as benchmark.run
cases = pick_cases(N, SEED)
acts = bd.Database(db.INVENTORY_DB).load()
ids = {k: bd.get_node(database=k[0], code=k[1]).id for k in acts}
used = Counter()
for key, act in acts.items():
    for e in act.get("exchanges", []):
        if e.get("type") == "technosphere" and tuple(e["input"]) != key:
            used[tuple(e["input"])] += 1
sys_ = System(bd.get_node(database=db.INVENTORY_DB, code=cases[0]["code"]))
bench = Bench(sys_, ids, used)
print(f"{len(cases)} cases, blind pool = {len(bench.blind_pool)} processes", flush=True)

meta = {}
def info(key):
    if key not in meta:
        n = bd.get_node(database=key[0], code=key[1])
        meta[key] = {"name": n["name"], "location": n.get("location", ""), "unit": n.get("unit", ""), "code": key[1]}
    return meta[key]

out = []
for case in cases:
    truth = case["inputs"]
    target = bench.sys.cumulative([bench.ids[(db.INVENTORY_DB, case["code"])]])[:, 0]
    rec = {"code": case["code"], "name": case["name"], "category": case["category"],
           "location": case["location"], "unit": bd.get_node(database=db.INVENTORY_DB, code=case["code"]).get("unit", ""),
           "n_true_inputs": len(truth), "n_target_flows": int((target != 0).sum()),
           "original": {
               "inputs": sorted([{**info(k), "amount": v} for k, v in truth.items()], key=lambda r: -abs(r["amount"])),
               "biosphere": sorted([{**info(k), "amount": v,
                                     "categories": [str(c) for c in (bd.get_node(database=k[0], code=k[1]).get("categories") or [])][:2]}
                                    for k, v in case["direct"].items()], key=lambda r: -abs(r["amount"]))},
           "scenarios": {}}

    for sc in SCEN:
        direct = np.zeros(bench.sys.n_flows) if sc == "blind" else bench.direct_vector(case["direct"])
        keys = list(truth)
        if sc in ("oracle", "bounded"):
            cand = keys
        elif sc == "partial":
            contrib = {k: contribution_breadth(target, bench.col(bench.ids[k]) * truth[k]) for k in keys}
            cand = sorted(keys, key=lambda k: -contrib[k])[: max(1, round(0.7 * len(keys)))]
        else:  # distractors  -- consumes rng exactly as benchmark.run does
            pool = [k for k in bench.blind_pool if k not in truth and k != (db.INVENTORY_DB, case["code"])]
            cand = keys + rng.sample(pool, min(10, len(pool)))
        n = len(cand)
        lo, hi = np.zeros(n), np.full(n, np.inf)
        if sc == "bounded":
            lo = np.array([0.5 * truth[k] for k in cand]); hi = np.array([2.0 * truth[k] for k in cand])
        t0 = time.time()
        x, M = bench.fit(target, cand, lo, hi, direct)
        secs = time.time() - t0
        model = M @ x + direct
        ag = flow_agreement(target, model)

        cols = {k: M[:, i] for i, k in enumerate(cand)}
        mat = lambda col, amt: contribution_breadth(target, col * amt) > 0
        true_material = {k for k in truth if k in cols and mat(cols[k], truth[k])} | {k for k in truth if k not in cols}
        chosen = {k for i, k in enumerate(cand) if mat(cols[k], x[i])}

        rows = []
        for i, k in enumerate(cand):
            t = truth.get(k)
            rows.append({**info(k),
                         "role": "true input" if k in truth else "distractor",
                         "truth": t, "fitted": float(x[i]),
                         "ratio": (float(x[i]) / t) if t else None,
                         "lo": float(lo[i]) if sc == "bounded" else None,
                         "hi": float(hi[i]) if sc == "bounded" else None,
                         "material_true": k in true_material, "material_fitted": k in chosen})
        for k in truth:                                   # true inputs never offered (partial)
            if k not in cols:
                rows.append({**info(k), "role": "withheld", "truth": truth[k], "fitted": None, "ratio": None,
                             "lo": None, "hi": None, "material_true": True, "material_fitted": False})
        rows.sort(key=lambda r: -(abs(r["truth"]) if r["truth"] else 0))

        ratios = [x[i] / truth[k] for i, k in enumerate(cand) if k in true_material and truth[k]]
        nz = np.where(target != 0)[0]
        top = sorted(nz, key=lambda r: -abs(target[r]))[:40]
        frows = []
        for r in top:
            fn = bench.sys.flow_node(int(r))
            cats = fn.get("categories") or ()
            frows.append({"name": fn["name"], "unit": fn.get("unit", ""),
                          "compartment": " / ".join(str(c) for c in cats[:2]),
                          "target": float(target[r]), "model": float(model[r]),
                          "delta": float(model[r] / target[r] - 1) if target[r] else None})

        rec["scenarios"][sc] = {
            "n_candidates": n, "n_chosen": len(chosen), "n_material_true": len(true_material),
            "true_positives": len(chosen & true_material),
            "false_positives": len(chosen - set(truth)), "false_negatives": len(true_material - chosen),
            "amounts_within_20pct": sum(1 for r in ratios if 0.8 <= r <= 1.2), "amounts_scored": len(ratios),
            "amount_ratio_median": None if not ratios else float(np.median(ratios)),
            "flows_within_10pct": ag["within_10pct"], "flows_within_20pct": ag["within_20pct"],
            "n_target_flows": ag["n_target"], "flows_missing": ag["n_missing"], "flows_extra": ag["n_extra"],
            "median_abs_delta": None if np.isnan(ag["median_abs_delta"]) else float(ag["median_abs_delta"]),
            "seconds": round(secs, 3), "candidates": rows, "top_flows": frows}
    out.append(rec)
    print("done", case["name"][:45], flush=True)

Path("results/benchmark/flow-n10-seed7-detail.json").write_text(json.dumps(out, ensure_ascii=False))
print("bytes:", Path("results/benchmark/flow-n10-seed7-detail.json").stat().st_size)
