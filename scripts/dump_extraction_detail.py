import csv, json, warnings
from pathlib import Path
import numpy as np
import bw2data as bd
warnings.filterwarnings("ignore")

from reverse_bafu import db, benchmark, spec as spec_mod
from reverse_bafu.lci import System, flow_agreement
from reverse_bafu.spec import walk, node_prefix

SRC = Path(".")   # run from the repo root
db.set_project("bafu-2026-bench")
EV = Path("results/benchmark/extraction/evidence")
SPECS = Path("results/benchmark/extraction/specs")

cases = benchmark.pick_extraction_cases(10, 7, SRC / "data/ecospold",
        SRC / "BAFU-2026 v1_Documentation/BAFU-2026 v1_Documentation/BAFU-2026 v1 LCI Reports")
metrics = {r["code"]: r for r in csv.DictReader(open("results/benchmark/extraction-n10-seed7.csv"))}

def node_info(key):
    n = bd.get_node(database=key[0], code=key[1])
    cats = n.get("categories") or ()
    return {"name": n["name"], "location": n.get("location", ""), "unit": n.get("unit", ""),
            "code": key[1], "database": key[0], "categories": [str(c) for c in cats]}

out = []
for case in cases:
    code = case["code"]
    act = bd.get_node(database=db.INVENTORY_DB, code=code)
    rec = {"code": code, "name": case["name"], "location": case["location"], "unit": act.get("unit", ""),
           "category": case["category"], "pdf": case["pdf"], "metrics": metrics.get(code, {}),
           "comment": (act.get("comment") or "")[:1200]}

    # ---------- 1. original LCI, all exchanges
    orig_in = [{**node_info(k), "amount": v} for k, v in case["inputs"].items()]
    orig_bio = [{**node_info(k), "amount": v} for k, v in case["direct"].items()]
    orig_in.sort(key=lambda r: -abs(r["amount"]))
    orig_bio.sort(key=lambda r: -abs(r["amount"]))
    rec["original"] = {"inputs": orig_in, "biosphere": orig_bio}

    # ---------- evidence / prompts
    ev = EV / code
    r0 = json.loads((ev / "response-0-locate.json").read_text()) if (ev / "response-0-locate.json").exists() else None
    rec["locate"] = r0
    r1p = ev / "response-1-extract.json"
    rec["extract"] = json.loads(r1p.read_text()) if r1p.exists() else None
    cand_p = ev / "candidates-2-map.json"
    rec["candidates"] = json.loads(cand_p.read_text()) if cand_p.exists() else None
    r2p = ev / "response-2-map.json"
    rec["mappings"] = json.loads(r2p.read_text())["mappings"] if r2p.exists() else None
    rec["prompt_bytes"] = {s: (ev / f"prompt-{s}.md").stat().st_size if (ev / f"prompt-{s}.md").exists() else 0
                           for s in ("0-locate", "1-extract", "2-map")}

    sp_path = next(SPECS.glob(f"{code[:8]}-*.bench.json"), None)
    if sp_path is None:
        rec["strategy"] = None; rec["new"] = None; rec["comparison"] = None
        out.append(rec); continue

    sp = spec_mod.load(sp_path)
    rec["strategy"] = sp.strategy
    rec["evidence"] = sp.evidence

    # ---------- 2. new LCI, all exchanges (flattened over sub-nodes)
    new_in, new_bio = [], []
    for nd in walk(sp.node):
        for i in nd.inputs:
            d = i.raw.get("derivation", {})
            new_in.append({"name": i.name, "amount": i.amount, "unit": i.unit, "location": i.location,
                           "code": i.code, "quote": d.get("quote", ""), "raw_value": d.get("raw_value"),
                           "raw_unit": d.get("raw_unit", ""), "factor": d.get("factor"),
                           "per": d.get("per", ""), "confidence": d.get("confidence", ""),
                           "search": d.get("search", ""), "mapping_reason": d.get("mapping_reason", ""),
                           "note": i.note})
        for f, kind in ((nd.emissions, "emission"), (nd.resources, "resource")):
            for fl in f:
                d = fl.raw.get("derivation", {})
                new_bio.append({"name": fl.name, "amount": fl.amount, "unit": fl.unit, "kind": kind,
                                "category": fl.category, "code": fl.code, "database": fl.database,
                                "quote": d.get("quote", ""), "raw_value": d.get("raw_value"),
                                "raw_unit": d.get("raw_unit", ""), "confidence": d.get("confidence", ""),
                                "mapping_reason": d.get("mapping_reason", ""), "note": fl.note})
    new_in.sort(key=lambda r: -abs(r["amount"]))
    new_bio.sort(key=lambda r: -abs(r["amount"]))
    rec["new"] = {"inputs": new_in, "biosphere": new_bio}

    # ---------- 3. comparison: inputs truth vs drafted
    truth_in = {k[1]: v for k, v in case["inputs"].items()}
    drafted = {}
    for nd in walk(sp.node):
        for i in nd.inputs:
            if i.code:
                base = i.code.split("-disagg")[0].split("-bench")[0]
                drafted[base] = drafted.get(base, 0.0) + i.amount
    rows = []
    for c, amt in sorted(truth_in.items(), key=lambda kv: -abs(kv[1])):
        info = node_info((db.INVENTORY_DB, c))
        d = drafted.get(c)
        rows.append({"name": info["name"], "location": info["location"], "unit": info["unit"], "code": c,
                     "truth": amt, "drafted": d,
                     "ratio": (d / amt) if (d is not None and amt) else None,
                     "status": "matched" if d is not None else "missed"})
    for c, amt in drafted.items():
        if c not in truth_in:
            try: info = node_info((db.INVENTORY_DB, c))
            except Exception: info = {"name": c, "location": "", "unit": ""}
            rows.append({"name": info["name"], "location": info["location"], "unit": info["unit"], "code": c,
                         "truth": None, "drafted": amt, "ratio": None, "status": "extra"})
    rec["comparison"] = {"inputs": rows}

    # ---------- 3b. comparison: cumulative elementary flows
    try:
        disagg = bd.get_node(database=db.SANDBOX_DB, code=f"{node_prefix(sp)}-disagg")
        sys_ = System(disagg)          # sandbox demand -> matrix covers sandbox AND bafu-2026
        cols = sys_.cumulative([act.id, disagg.id])
        target, explicit = cols[:, 0], cols[:, 1]
        ag = flow_agreement(target, explicit)
        nz = np.where(target != 0)[0]
        order = sorted(nz, key=lambda r: -abs(target[r]))[:40]
        frows = []
        for r in order:
            fn = sys_.flow_node(int(r))
            cats = fn.get("categories") or ()
            frows.append({"name": fn["name"], "unit": fn.get("unit", ""),
                          "compartment": " / ".join(str(c) for c in cats[:2]),
                          "target": float(target[r]), "rebuilt": float(explicit[r]),
                          "delta": float(explicit[r] / target[r] - 1) if target[r] else None})
        rec["comparison"]["flows"] = {
            "n_target": ag["n_target"], "within_10pct": ag["within_10pct"], "within_20pct": ag["within_20pct"],
            "within_50pct": ag["within_50pct"], "n_missing": ag["n_missing"], "n_extra": ag["n_extra"],
            "median_abs_delta": None if np.isnan(ag["median_abs_delta"]) else float(ag["median_abs_delta"]),
            "top": frows}
    except Exception as exc:
        rec["comparison"]["flows"] = {"error": str(exc)[:200]}
    out.append(rec)
    print("done", case["name"][:45], flush=True)

Path("results/benchmark/extraction-n10-seed7-detail.json").write_text(json.dumps(out, ensure_ascii=False))
print("bytes:", Path("results/benchmark/extraction-n10-seed7-detail.json").stat().st_size)
