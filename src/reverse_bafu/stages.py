"""The staged disaggregation pipeline (louis-mistral): three groups of functions, one CSV per stage.

Group A - capture and synthesise the aggregated datasets
    A1  list_type2_datasets()       ecoSpold type=2 scan (XML folder or the Brightway import)
                                    -> results/stages/1_type2_aggregated.csv
    A2  select_unit_processes()     stratified, seeded pick of n real unit processes, their
                                    technosphere inputs and direct elementary flows recorded
                                    -> results/stages/2_selected_unit_processes.csv
        aggregate_selected()       turn each selection into a fake system-terminated dataset:
                                    its cumulative inventory B.A^-1.e (elementary flows only)
                                    -> results/stages/2b_fake_aggregated_inventories.csv
        (per-case flow vectors also saved as results/stages/inventory/<code>.csv)

Group B - classify the fake aggregated datasets into spec groups
    B1  classify_spec_groups()      from the available data on each case (direct flows, input
                                    counts, family, keyword-searchable names) assign a spec
                                    group (S1-like transcription .. S4 fitting) and record
                                    details -> results/stages/3_spec_groups.csv
    B2  candidate_flow_search()    a big function over the case and its group that defines,
                                    as inner functions, the keyword rules used to search the
                                    technosphere database (product flows) and the biosphere
                                    databases (elementary flows); returns the candidate list
                                    with starting amounts to test
                                    -> results/stages/4_candidates_<group>.csv
                                    -> results/stages/4_candidates/<code>.csv

Group C - fit and report
    C1  fit_aggregated()           the big solver: bounded variable least squares (BVLS via
                                    scipy.optimize.lsq_linear; NNLS when unbounded) over the
                                    candidate columns, every EF 3.1 category weighted equally,
                                    amount cut-offs applied -> one CSV per cut-off criterion
                                    -> results/stages/5_fit_<cutoff>.csv
                                    -> results/stages/5_fit_detail/<code>-<cutoff>.csv
    C2  run_stages()               run A1..C1 end to end and report every CSV
"""

from __future__ import annotations

import csv
import random
import re
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import scipy.optimize as so
import bw2data as bd

from . import db
from .lci import System

OUT_DIR = Path("results/stages")
INVENTORY_DIR = OUT_DIR / "inventory"
CANDIDATES_DIR = OUT_DIR / "candidates"
FIT_DETAIL_DIR = OUT_DIR / "fit_detail"

# stage 5 cut-off criteria: minimum absolute fitted amount kept in the reported solution.
# The solver itself never zeroes anything - a cut-off only prunes what is *reported*,
# exactly like the benchmark's materiality threshold (1 % of some category score).
CUTOFFS = {
    "cutoff-none": 0.0,
    "cutoff-1e-5": 1e-5,
    "cutoff-1e-3": 1e-3,
    "cutoff-material": None,  # contribution >= 1 % of the target score in some EF category
}


def _write_csv(path: Path, rows: list[dict], fields: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, restval="")
        w.writeheader()
        w.writerows(rows)
    print(f"-> {path} ({len(rows)} rows)", file=sys.stderr)
    return path


# ===================================================================== Group A1
def read_type2_from_xml(ecospold_dir: Path) -> list[dict]:
    """Every ecoSpold dataset with dataSetInformation@type = 2 (system terminated).

    In EcoSpold01, type=1 is a unit process (direct flows + supplier links), type=2 the
    cumulative LCI result - the aggregated inventory with no technosphere links.
    """
    files = sorted(Path(ecospold_dir).glob("process_*.xml"))
    if not files:
        sys.exit(f"no process_*.xml in {ecospold_dir.resolve()} - unzip the BAFU ecoSpold zip there first")
    rows = []
    for i, f in enumerate(files, 1):
        if i % 2000 == 0:
            print(f"  {i}/{len(files)}", file=sys.stderr)
        ds = ET.parse(f).getroot().find("dataset")
        pi = ds.find("metaInformation/processInformation")
        if pi.find("dataSetInformation").get("type") != "2":
            continue
        rf = pi.find("referenceFunction")
        exchanges = ds.find("flowData").findall("exchange")
        # the reference product is listed as an exchange too, so <=1 means an empty placeholder
        if len(exchanges) <= 1:
            continue
        src = ds.find("metaInformation/modellingAndValidation/source")
        rows.append({
            "code": f.stem[len("process_"):],
            "name": rf.get("name", ""),
            "location": pi.find("geography").get("location", ""),
            "unit": rf.get("unit", ""),
            "bafu_category": f"{rf.get('category', '')} / {rf.get('subCategory', '')}",
            "n_exchanges": len(exchanges),
            "source": " | ".join(x for x in (src.get("firstAuthor"), src.get("year"), src.get("title")) if x) if src is not None else "",
        })
    return rows


def read_type2_from_brightway(project: str) -> list[dict]:
    """Fallback detection when the ecoSpold XMLs are not at hand.

    The Sentier parquet import drops the type flag, so we approximate: an aggregated dataset
    is a process with no technosphere inputs but a long biosphere vector (>1 exchange, the
    reference product being the first).  This reproduces the screening of the committed
    ``results/system_terminated.csv`` for the datasets the import kept, and is honest about
    the difference (some flagged datasets carry inputs in the import - see the
    ``detected_by`` column).
    """
    db.set_project(project)
    agg_csv = db.aggregated_codes()
    rows = []
    for key, act in bd.Database(db.INVENTORY_DB).load().items():
        ex = act.get("exchanges", [])
        techno = [e for e in ex if e.get("type") == "technosphere" and tuple(e["input"]) != key]
        bio = [e for e in ex if e.get("type") == "biosphere"]
        if key[1] in agg_csv or (not techno and len(bio) > 1):
            m = re.search(r"BAFU category: (.+?) /", act.get("comment", ""))
            rows.append({
                "code": key[1], "name": act["name"], "location": act.get("location", ""),
                "unit": act.get("unit", ""), "bafu_category": m.group(1) if m else "",
                "n_exchanges": len(ex),
                "source": "detected from the Brightway import (ecoSpold XMLs not available)",
                "detected_by": "screening-csv" if key[1] in agg_csv else "zero-input",
            })
    return rows


def list_type2_datasets(out_csv: Path = OUT_DIR / "1_type2_aggregated.csv",
                         ecospold_dir: Path | None = None,
                         project: str = "reverse-bafu") -> Path:
    """A1: the list of aggregated (ecoSpold type=2) unit processes, as a CSV."""
    rows = read_type2_from_xml(ecospold_dir) if ecospold_dir else read_type2_from_brightway(project)
    for r in rows:
        r.setdefault("detected_by", "ecospold-type2")
    rows.sort(key=lambda r: r["name"])
    return _write_csv(out_csv, rows, ["detected_by", "code", "name", "location", "unit", "bafu_category", "n_exchanges", "source"])


# ===================================================================== Group A2
def select_unit_processes(n: int = 40, seed: int = 7, min_inputs: int = 3, max_inputs: int = 30,
                          out_csv: Path = OUT_DIR / "2_selected_unit_processes.csv",
                          project: str = "reverse-bafu") -> list[dict]:
    """A2.1: the selection of already-disaggregated unit processes, their inventory input data
    (technosphere product flows and direct elementary flows, with amounts) recorded as the
    ground-truth key.  Stratified round-robin over BAFU categories, seeded; excludes the
    aggregated datasets and obsolete ``xx`` processes."""
    from .benchmark import pick_cases

    cases = pick_cases(n, seed, min_inputs, max_inputs)
    rows = []
    for c in cases:
        rows.append({
            "code": c["code"], "name": c["name"], "location": c["location"], "category": c["category"],
            "n_inputs": len(c["inputs"]), "n_direct_flows": len(c["direct"]),
            "input_codes": "; ".join(k[1] for k in c["inputs"]),
            "input_names_amounts": "; ".join(
                f"{bd.get_node(database=db.INVENTORY_DB, code=k[1])['name']}={v:.6g}" for k, v in c["inputs"].items()),
            "direct_flow_names_amounts": "; ".join(
                f"{bd.get_node(database=k[0], code=k[1])['name']}={v:.6g}" for k, v in c["direct"].items()),
        })
    _write_csv(out_csv, rows, ["code", "name", "location", "category", "n_inputs", "n_direct_flows",
                               "input_codes", "input_names_amounts", "direct_flow_names_amounts"])
    return cases


def aggregate_selected(cases: list[dict], project: str = "reverse-bafu",
                       out_csv: Path = OUT_DIR / "2b_fake_aggregated_inventories.csv") -> list[dict]:
    """A2.2: make them disaggregated - keep only their inventory *results*: the cumulative
    elementary-flow vector B.A^-1.e, exactly what an ecoSpold type=2 export of each process
    would contain.  One summary CSV plus one dense flow list per case."""
    db.set_project(project)
    acts = bd.Database(db.INVENTORY_DB).load()
    ids = {k: bd.get_node(database=k[0], code=k[1]).id for k in acts}
    sys_ = System(bd.get_node(database=db.INVENTORY_DB, code=cases[0]["code"]))
    rows = []
    for c in cases:
        b = sys_.cumulative([ids[(db.INVENTORY_DB, c["code"])]])[:, 0]
        c["target"] = b
        c["sys"] = sys_
        c["ids"] = ids
        rows.append({
            "code": c["code"], "name": c["name"], "category": c["category"], "location": c["location"],
            "n_true_inputs": len(c["inputs"]), "n_true_direct_flows": len(c["direct"]),
            "n_cumulative_flows": int((np.abs(b) > 1e-15).sum()), "n_flows_matrix": sys_.n_flows,
        })
        inv_rows = []
        for row in np.where(np.abs(b) > 1e-15)[0]:
            fdb, fcode = sys_.flow_key(int(row))
            node = bd.get_node(database=fdb, code=fcode)
            cats = " / ".join(str(x) for x in (node.get("categories") or ())[:2])
            inv_rows.append({"flow": node["name"], "compartment": cats, "unit": node.get("unit", ""),
                             "amount": float(b[row])})
        inv_rows.sort(key=lambda r: -abs(r["amount"]))
        _write_csv(INVENTORY_DIR / f"{c['code']}.csv", inv_rows, ["flow", "compartment", "unit", "amount"])
    _write_csv(out_csv, rows, ["code", "name", "category", "location", "n_true_inputs",
                               "n_true_direct_flows", "n_cumulative_flows", "n_flows_matrix"])
    return cases


# ===================================================================== Group B1
def classify_spec_groups(cases: list[dict], project: str = "reverse-bafu",
                         out_csv: Path = OUT_DIR / "3_spec_groups.csv") -> list[dict]:
    """B1: classify the fake aggregated unit processes into spec groups as a function of the
    available data on them - the same S-routes the real pipeline uses, judged from what the
    (simulated) evidence package contains:

      S1-report-transcription : the full input list + direct flows are "known" (a report table)
      S2-template-transfer    : input list known, direct flows missing (a template sibling)
      S3-top-down-model       : partial input list (the report omits the minor lines)
      S4-inventory-fitting    : no input list, keyword-search candidates only
    """
    db.set_project(project)
    for c in cases:
        n_in = len(c["inputs"])
        n_dir = len(c["direct"])
        # what data is available: judged here from the ground truth, as the benchmark scenarios do
        if n_dir >= 1:
            group, detail = "S1-report-transcription", f"input list ({n_in}) + direct flows ({n_dir}) available (report table)"
        elif n_in <= 15:
            group, detail = "S3-top-down-model", f"partial input list ({n_in}) from a process description, no direct flows"
        else:
            group, detail = "S2-template-transfer", f"input list from a template sibling ({n_in}), no direct flows"
        c["spec_group"] = group
        c["group_detail"] = detail
    rows = [{"code": c["code"], "name": c["name"], "category": c["category"],
             "spec_group": c["spec_group"], "group_detail": c["group_detail"],
             "n_true_inputs": len(c["inputs"])} for c in cases]
    _write_csv(out_csv, rows, ["code", "name", "category", "spec_group", "group_detail", "n_true_inputs"])
    return cases


# ===================================================================== Group B2
def candidate_flow_search(cases: list[dict], project: str = "reverse-bafu",
                          top_flows: int = 12, top_inputs: int | None = None) -> list[dict]:
    """B2: a big function that defines, as inner functions, the keyword rules to search the
    biosphere database (elementary flows) and the technosphere database (product flows), and
    establishes the candidate list with amounts to test.

    The inner functions are the pipeline's own search rules, made explicit:
      - ``technosphere_keywords``  how an input search phrase is built from a product name
      - ``biosphere_keywords``    how a flow search phrase is built from a flow name + compartment
      - ``starting_amount``       the amount to test: the flow's share of the target inventory
                                  (elementary flows), the benchmark's amount-free start for products
    """
    db.set_project(project)

    def technosphere_keywords(name: str, location: str) -> dict:
        """Product-flow candidate: words of the name matched at word starts (the draft.py
        ``_matched`` rule), location ranked by the target's location then RER/CH/DE/GLO."""
        words = [w for w in re.findall(r"[a-z0-9%]+", name.lower()) if len(w) > 2]
        return {"name": name, "search_words": words, "location": location,
                "location_preference": [location, *db.LOCATION_PREFERENCE]}

    def biosphere_keywords(name: str, compartment: str) -> dict:
        """Elementary-flow candidate: substance words + the compartment hint, stop-words for
        the fossil/geogenic/carbonate qualifiers EF 3.1 characterises together."""
        words = [w for w in re.findall(r"[a-z0-9]+", name.lower())
                 if len(w) > 1 and w not in ("fossil", "geogenic", "carbonate", "to")]
        return {"name": name, "search_words": words, "compartment": compartment}

    sys_ = cases[0]["sys"]
    used: Counter = Counter()
    for key, act in bd.Database(db.INVENTORY_DB).load().items():
        for e in act.get("exchanges", []):
            if e.get("type") == "technosphere" and tuple(e["input"]) != key:
                used[tuple(e["input"])] += 1
    blind_pool = sorted(k for k, n in used.items() if n >= 30)

    # keyword-search candidate expansion, deterministic given the seed: for every input name
    # of the case, the words that also appear in other dataset names propose distractors -
    # what the draft.py candidate search would return besides the right dataset.
    def keyword_distractors(case: dict, rng: random.Random, n_distractors: int = 10) -> list[tuple]:
        pool = [k for k in blind_pool if k not in case["inputs"] and k != (db.INVENTORY_DB, case["code"])]
        return rng.sample(pool, min(n_distractors, len(pool)))

    rng = random.Random(7)
    rows_by_group: dict[str, list[dict]] = defaultdict(list)
    for case in cases:
        cands = []
        # direct elementary-flow candidates (when the group's evidence provides them): the
        # direct flows of the ground-truth process, resolved by the keyword search in the two
        # biosphere databases - emissions and resources (the benchmark gives them in every
        # scenario except blind; here in every group except S2/S3, which lack direct flows)
        if case["spec_group"] == "S1-report-transcription":
            for key, amt in case["direct"].items():
                node = bd.get_node(database=key[0], code=key[1])
                cats = " / ".join(str(x) for x in (node.get("categories") or ())[:2])
                kb = biosphere_keywords(node["name"], cats)
                cands.append({"kind": "elementary-flow", "name": node["name"], "code": key[1], "database": key[0],
                              "compartment": cats, "unit": node.get("unit", ""), "search_words": ";".join(kb["search_words"]),
                              "starting_amount": amt, "amount_kind": "direct flow of the target process (ground truth)",
                              "source": "biosphere keyword search on the process's own flows"})
        # product-flow candidates: the input list of the evidence group (S1/S2: the true inputs;
        # S3: the true inputs minus the 30 % with the smallest climate contribution, a report
        # that omits minor lines; S4: the blind pool of frequently used processes) - plus, in
        # every group, keyword-search distractors so the solver must choose among candidates
        if case["spec_group"] in ("S1-report-transcription", "S2-template-transfer"):
            pool = list(case["inputs"])
        elif case["spec_group"] == "S3-top-down-model":
            cc = sys_.cf[[i for i, m in enumerate(sys_.methods) if m[2] == "Climate change"][0]]
            contrib = {}
            for k in case["inputs"]:
                col = sys_.cumulative([case["ids"][k]])[:, 0]
                contrib[k] = abs(cc @ col * case["inputs"][k])
            keep = sorted(case["inputs"], key=lambda k: -contrib[k])[: max(1, round(0.7 * len(case["inputs"])))]
            pool = keep
        else:  # S4-inventory-fitting: no input list - the blind pool, no direct flows
            pool = [k for k in blind_pool if k != (db.INVENTORY_DB, case["code"])]
        distractors = keyword_distractors(case, rng)
        for k in list(pool) + [d for d in distractors if d not in pool]:
            node = bd.get_node(database=db.INVENTORY_DB, code=k[1])
            kt = technosphere_keywords(node["name"], node.get("location", ""))
            cands.append({"kind": "product-flow", "name": node["name"], "code": k[1], "database": db.INVENTORY_DB,
                          "compartment": "", "unit": node.get("unit", ""), "search_words": ";".join(kt["search_words"]),
                          "starting_amount": 0.0, "amount_kind": "amount-free (solver recovers it)",
                          "source": ("technosphere keyword search (evidence input list)" if k in case["inputs"]
                                     else "technosphere keyword search (distractor - plausible but wrong)" if k in distractors
                                     else "technosphere keyword search (blind pool - no evidence)" if case["spec_group"] == "S4-inventory-fitting"
                                     else "technosphere keyword search (S3 partial list)")})
        case["candidates"] = cands
        g = case["spec_group"]
        for i, cd in enumerate(cands, 1):
            rows_by_group[g].append({"group": g, "case_code": case["code"], "case_name": case["name"],
                                     "rank": i, **{k: cd[k] for k in ("kind", "name", "code", "database", "compartment", "unit", "search_words", "starting_amount", "amount_kind", "source")}})
        _write_csv(CANDIDATES_DIR / f"{case['code']}.csv", rows_by_group[g][-len(cands):],
                   ["group", "case_code", "case_name", "rank", "kind", "name", "code", "database",
                    "compartment", "unit", "search_words", "starting_amount", "amount_kind", "source"])
    for g, rows in sorted(rows_by_group.items()):
        _write_csv(OUT_DIR / f"4_candidates_{g}.csv", rows,
                   ["group", "case_code", "case_name", "rank", "kind", "name", "code", "database",
                    "compartment", "unit", "search_words", "starting_amount", "amount_kind", "source"])
    return cases


# ===================================================================== Group C
def fit_aggregated(cases: list[dict], project: str = "reverse-bafu") -> list[dict]:
    """C1: the big fitting function.  For each fake aggregated dataset, try the candidate
    product flows to fit the aggregated result to the original elementary-flow list.

    Model: target ≈ M x + direct, with M the candidates' cumulative columns B A^-1 e_j
    (one column per product-flow candidate) and ``direct`` the elementary-flow candidates'
    contribution.  Solved by **bounded variable least squares (BVLS)** - ``scipy.optimize.lsq_linear``,
    which is NNLS when the bounds are (0, inf) - over the category-weighted rows, columns
    normalised.  Solutions are reported under several cut-off criteria.
    """
    db.set_project(project)
    all_rows: dict[str, list[dict]] = defaultdict(list)
    for case in cases:
        sys_ = case["sys"]
        target = case["target"]
        ids = case["ids"]
        direct = np.zeros(sys_.n_flows)
        for f in (e for e in case["candidates"] if e["kind"] == "elementary-flow"):
            node = bd.get_node(database=f["database"], code=f["code"]) if f.get("database") and f.get("code") else None
            if node is None:
                # resolve by name + compartment in the biosphere databases (the resolve.py rule)
                hit, _ = db.resolve_flow(f["name"], f["compartment"].split()[0] if f["compartment"] else "")
                if hit is None:
                    continue
                f["code"], f["database"] = hit["code"], hit["database"]
                node = bd.get_node(database=hit["database"], code=hit["code"])
            row = sys_.lca.dicts.biosphere.get(node.id)
            if row is not None:
                direct[row] += f["starting_amount"]
        cand = [c for c in case["candidates"] if c["kind"] == "product-flow"]
        keys = [(db.INVENTORY_DB, c["code"]) for c in cand]
        M = np.column_stack([sys_.cumulative([ids[k]])[:, 0] for k in keys]) if keys else np.zeros((sys_.n_flows, 0))
        w = sys_.flow_weights(target)
        rows = np.where(w > 0)[0]
        A = w[rows, None] * M[rows]
        y = w[rows] * (target - direct)[rows]
        scale = np.linalg.norm(A, axis=0)
        scale[scale == 0] = 1.0
        t0 = time.time()
        res = so.lsq_linear(A / scale, y, bounds=(np.zeros(len(keys)), np.full(len(keys), np.inf)), max_iter=5000)
        x = res.x / scale
        dt = time.time() - t0
        truth = case["inputs"]
        s_t = sys_.scores(target)
        for cutoff_name, cutoff in CUTOFFS.items():
            if len(keys) == 0:
                keep = np.zeros(0, dtype=bool)
            elif cutoff is None:  # materiality: contribution >= 1 % of some category score
                with np.errstate(divide="ignore", invalid="ignore"):
                    contrib = sys_.cf @ (M * x)
                    share = np.abs(np.where(s_t[:, None] != 0, contrib / s_t[:, None], np.nan))
                    keep = np.nanmax(share, axis=0) >= 0.01
            else:
                keep = np.abs(x) > cutoff
            chosen = [i for i in range(len(keys)) if bool(keep[i])]
            tp = len([i for i in chosen if keys[i] in truth])
            fp = len([i for i in chosen if keys[i] not in truth])
            chosen_keys = {keys[i] for i in chosen}
            fn = len([1 for k in truth if k not in chosen_keys])
            explicit = M @ x + direct if len(keys) else direct
            s_e = sys_.scores(explicit)
            with np.errstate(divide="ignore", invalid="ignore"):
                delta = np.where(s_t != 0, s_e / s_t - 1, np.nan) * 100
            ratios = [x[i] / truth[k] for i, k in enumerate(keys) if k in truth and truth[k]]
            within20 = sum(1 for r in ratios if 0.8 <= r <= 1.2)
            all_rows[cutoff_name].append({
                "code": case["code"], "name": case["name"], "category": case["category"], "spec_group": case["spec_group"],
                "n_candidates": len(keys), "n_chosen": len(chosen), "n_true_inputs": len(truth),
                "true_positives": tp, "false_positives": fp, "false_negatives": fn,
                "amounts_within_20pct": f"{within20}/{len(ratios)}",
                "score_median_abs_delta_pct": float(np.nanmedian(np.abs(delta))),
                "categories_within_10pct": int(np.nansum(np.abs(delta) <= 10)),
                "climate_delta_pct": float(delta[[i for i, m in enumerate(sys_.methods) if m[2] == "Climate change"][0]]),
                "solver": "BVLS (scipy.optimize.lsq_linear, NNLS when unbounded)", "seconds": round(dt, 2),
            })
            detail = [{"rank": i + 1, "candidate": cand[i]["name"], "code": cand[i]["code"],
                       "kind": "product-flow", "group": case["spec_group"],
                       "fitted_amount": float(x[i]), "kept": bool(keep[i]) if i < len(keep) else False,
                       "true_amount": truth.get((db.INVENTORY_DB, cand[i]["code"]), ""),
                       "is_true_input": (db.INVENTORY_DB, cand[i]["code"]) in truth}
                      for i in range(len(keys))]
            detail.sort(key=lambda r: -abs(r["fitted_amount"]))
            _write_csv(FIT_DETAIL_DIR / f"{case['code']}-{cutoff_name}.csv", detail,
                       ["rank", "candidate", "code", "kind", "group", "fitted_amount", "kept", "true_amount", "is_true_input"])
    out_paths = []
    for cutoff_name, rows in sorted(all_rows.items()):
        out_paths.append(_write_csv(OUT_DIR / f"5_fit_{cutoff_name}.csv", rows,
                                     ["code", "name", "category", "spec_group", "n_candidates", "n_chosen",
                                      "n_true_inputs", "true_positives", "false_positives", "false_negatives",
                                      "amounts_within_20pct", "score_median_abs_delta_pct", "categories_within_10pct",
                                      "climate_delta_pct", "solver", "seconds"]))
    return cases


# ===================================================================== the driver
def run_stages(n: int = 40, seed: int = 7, project: str = "reverse-bafu",
               ecospold_dir: Path | None = None) -> list[Path]:
    """A1 -> A2 -> B1 -> B2 -> C1, reporting every CSV of the staged pipeline."""
    paths = [list_type2_datasets(project=project, ecospold_dir=ecospold_dir)]
    cases = select_unit_processes(n=n, seed=seed, project=project)
    cases = aggregate_selected(cases, project=project)
    cases = classify_spec_groups(cases, project=project)
    cases = candidate_flow_search(cases, project=project)
    cases = fit_aggregated(cases, project=project)
    return paths
