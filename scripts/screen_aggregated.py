"""Screen the BAFU-2026 Brightway database for aggregated (cumulative-LCI) datasets.

Aggregated datasets are the targets of hackathon issue #38: processes whose upstream chain
has been folded into one elementary-flow list instead of being modelled as technosphere
inputs. Three independent signals are combined; each one is kept as its own column so the
ranking can be re-cut later.

1. ``system_flag`` - ecoSpold ``dataSetInformation@type`` from the raw XML (1 = unit
   process, 2 = system terminated). Explicit, but only set on ~100 datasets and dropped by
   the Sentier import, so it needs the unzipped ``data/ecospold/`` folder.
2. structure - a process with no technosphere inputs but a long elementary-flow list is a
   cumulative inventory by construction.
3. ``signature_groups`` - background-chain flows that a plant-level unit process never
   emits directly: crude oil / natural gas / coal / uranium *in ground*, Radon-222 and
   Carbon-14. A cradle-to-gate LCI carries the whole energy mix, so three or more groups
   *including the nuclear chain* (uranium ore or Carbon-14) mean one was pasted in, even
   when a handful of inputs is still modelled (PlasticsEurope eco-profiles, ecoinvent-v2
   chlorinated solvents). The nuclear condition keeps mines out: "Hard coal, at mine"
   legitimately has coal ore, mine gas and radon as direct flows.

Tiers, from strongest to weakest evidence:
    system-flagged        ecoSpold type=2
    cumulative-lci        0 technosphere inputs, >= --min-elementary elementary flows and the
                          background fingerprint (emission-only unit processes such as tyre
                          wear or ash leachate have no inputs either, but no fingerprint)
    partially-aggregated  background fingerprint but still has technosphere inputs
    unit                  everything else
    empty                 no inputs and no elementary flows (placeholders, obsolete stubs)

Usage:
    uv run python scripts/screen_aggregated.py [--project bafu-2026] [--ecospold data/ecospold]
                                               [--out output/aggregated_screening.csv] [--top 40]
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

# (name regex, top-level category the flow must sit in). Categories are checked on the
# EF 3.1 biosphere ("Resources"/"Emissions") and on the BAFU residual biosphere ("resources"/
# "emissions to air"), case-insensitively.
SIGNATURE_GROUPS = {
    "crude oil in ground": (re.compile(r"^(crude oil|oil, crude)", re.I), "resources"),
    "natural gas in ground": (re.compile(r"^(natural gas|gas, natural)", re.I), "resources"),
    "coal in ground": (re.compile(r"^(hard coal|brown coal|coal, (hard|brown))", re.I), "resources"),
    "uranium in ground": (re.compile(r"^uranium$", re.I), "resources"),
    "radon-222 to air": (re.compile(r"^radon-222", re.I), "emissions"),
    "carbon-14 to air": (re.compile(r"^carbon-14", re.I), "emissions"),
}

COMMENT_KEYWORDS = re.compile(
    r"aggregated|cumulative data|confidential|not disaggregated|system process|black.?box",
    re.I,
)

TIER_ORDER = ["system-flagged", "cumulative-lci", "partially-aggregated", "unit", "empty"]


def _category_root(flow: dict) -> str:
    cats = flow.get("categories") or ()
    return str(cats[0]).lower() if cats else ""


def _signature_groups(flow: dict) -> set[str]:
    hits = set()
    root = _category_root(flow)
    for group, (rx, cat) in SIGNATURE_GROUPS.items():
        if root.startswith(cat) and rx.search(flow.get("name", "")):
            hits.add(group)
    return hits


def scan_brightway(project: str, database: str) -> dict[str, dict]:
    """Per-activity structure from the Brightway project, keyed by activity code."""
    import bw2data as bd

    if project not in bd.projects:
        sys.exit(f"Brightway project {project!r} not found - run `uv run sentier-brightway db --project {project}` first")
    bd.projects.set_current(project)
    if database not in bd.databases:
        sys.exit(f"database {database!r} not in project {project!r}: {sorted(bd.databases)}")

    # one bulk load per database is far faster than 12k activity.exchanges() queries
    flows: dict[tuple, dict] = {}
    for dep in bd.databases[database].get("depends", []):
        flows.update(bd.Database(dep).load())
    acts = bd.Database(database).load()

    # how many other processes consume each dataset: replacing a widely used aggregated
    # dataset moves many results, so this ranks the replacement work
    used_by: Counter = Counter()
    for key, act in acts.items():
        for exc in act.get("exchanges", []):
            if exc.get("type") == "technosphere" and tuple(exc["input"]) != key:
                used_by[tuple(exc["input"])] += 1

    out = {}
    for key, act in acts.items():
        techno = bio = 0
        compartments: set[str] = set()
        sig: set[str] = set()
        for exc in act.get("exchanges", []):
            kind = exc.get("type")
            if kind == "technosphere":
                techno += 1
            elif kind == "biosphere":
                bio += 1
                flow = flows.get(tuple(exc["input"]), {})
                cats = flow.get("categories") or ()
                compartments.add("/".join(str(c) for c in cats[:2]))
                sig |= _signature_groups(flow)
        comment = act.get("comment", "")
        m = re.search(r"BAFU category: (.+?)\. Source:", comment)
        out[key[1]] = {
            "code": key[1],
            "name": act.get("name", ""),
            "location": act.get("location", ""),
            "unit": act.get("unit", ""),
            "bafu_category": m.group(1) if m else "",
            "n_technosphere_inputs": techno,
            "n_elementary_flows": bio,
            "n_used_by": used_by.get(key, 0),
            "n_compartments": len(compartments),
            "signature_groups": len(sig),
            "signature_detail": "; ".join(sorted(sig)),
        }
    return out


def scan_ecospold(folder: Path) -> dict[str, dict]:
    """The metadata the Sentier import drops, keyed by dataset UUID (= file name = bw code)."""
    out = {}
    files = sorted(folder.glob("process_*.xml"))
    for i, f in enumerate(files, 1):
        if i % 2000 == 0:
            print(f"  ecospold {i}/{len(files)}", file=sys.stderr)
        ds = ET.parse(f).getroot().find("dataset")
        pi = ds.find("metaInformation/processInformation")
        rf = pi.find("referenceFunction")
        dsi = pi.find("dataSetInformation")
        src = ds.find("metaInformation/modellingAndValidation/source")
        text = f"{rf.get('includedProcesses', '')} {rf.get('generalComment', '')}"
        kw = COMMENT_KEYWORDS.search(text)
        out[f.stem[len("process_"):]] = {
            "ecospold_type": dsi.get("type", ""),
            "generator": ds.get("generator", ""),
            "source": " | ".join(x for x in (src.get("publisher"), src.get("title")) if x) if src is not None else "",
            "comment_keyword": kw.group(0) if kw else "",
        }
    return out


NUCLEAR_CHAIN = {"uranium in ground", "carbon-14 to air"}


def has_fingerprint(row: dict) -> bool:
    """Three or more background-chain groups, at least one of them nuclear."""
    groups = set(row["signature_detail"].split("; ")) if row["signature_detail"] else set()
    return len(groups) >= 3 and bool(groups & NUCLEAR_CHAIN)


def classify(row: dict, min_elementary: int) -> str:
    techno, bio = row["n_technosphere_inputs"], row["n_elementary_flows"]
    if techno == 0 and bio == 0:
        return "empty"
    if row.get("ecospold_type") == "2":
        return "system-flagged"
    if techno == 0 and bio >= min_elementary and has_fingerprint(row):
        return "cumulative-lci"
    if has_fingerprint(row):
        return "partially-aggregated"
    return "unit"


def confidence(row: dict, min_elementary: int) -> str:
    """How many independent signals agree; 'high' needs at least two."""
    signals = sum(
        [
            row.get("ecospold_type") == "2",
            row["n_technosphere_inputs"] == 0 and row["n_elementary_flows"] >= min_elementary,
            has_fingerprint(row),
        ]
    )
    return {0: "none", 1: "medium"}.get(signals, "high")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--project", default="bafu-2026")
    p.add_argument("--database", default="bafu-2026")
    p.add_argument("--ecospold", default="data/ecospold", help="unzipped BAFU XML folder; skipped if missing")
    p.add_argument("--out", default="output/aggregated_screening.csv")
    p.add_argument("--min-elementary", type=int, default=50, help="elementary flows for cumulative-lci (default 50)")
    p.add_argument("--top", type=int, default=40, help="rows to print per tier")
    args = p.parse_args()

    print(f"scanning Brightway project {args.project!r} / database {args.database!r}", file=sys.stderr)
    rows = scan_brightway(args.project, args.database)

    xml_dir = Path(args.ecospold)
    if xml_dir.is_dir() and any(xml_dir.glob("process_*.xml")):
        print(f"joining ecoSpold metadata from {xml_dir}", file=sys.stderr)
        meta = scan_ecospold(xml_dir)
        for code, row in rows.items():
            row.update(meta.get(code, {}))
    else:
        print(f"no ecoSpold XML in {xml_dir} - system_flag / generator / source columns left empty", file=sys.stderr)
    for row in rows.values():
        row.setdefault("ecospold_type", ""); row.setdefault("generator", "")
        row.setdefault("source", ""); row.setdefault("comment_keyword", "")
        row["tier"] = classify(row, args.min_elementary)
        row["confidence"] = confidence(row, args.min_elementary)

    ordered = sorted(
        rows.values(),
        key=lambda r: (TIER_ORDER.index(r["tier"]), -r["n_elementary_flows"], r["name"]),
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "tier", "confidence", "code", "name", "location", "unit", "bafu_category",
        "n_technosphere_inputs", "n_elementary_flows", "n_used_by", "n_compartments", "signature_groups",
        "signature_detail", "ecospold_type", "generator", "source", "comment_keyword",
    ]
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(ordered)

    tiers = Counter(r["tier"] for r in ordered)
    print(f"\n{len(ordered)} processes screened -> {out}\n")
    print(f"{'tier':22s} {'n':>6s}   high-confidence")
    for t in TIER_ORDER:
        hi = sum(1 for r in ordered if r["tier"] == t and r["confidence"] == "high")
        print(f"{t:22s} {tiers.get(t, 0):6d}   {hi}")

    agg = [r for r in ordered if r["tier"] in TIER_ORDER[:3]]
    by_cat = Counter(r["bafu_category"].split(" / ")[0] for r in agg)
    print(f"\naggregated candidates by BAFU category ({len(agg)} total):")
    for cat, n in by_cat.most_common():
        print(f"  {n:4d}  {cat}")

    for t in TIER_ORDER[:3]:
        sub = [r for r in ordered if r["tier"] == t]
        if not sub:
            continue
        print(f"\n== {t} ({len(sub)}), top {min(args.top, len(sub))} by number of consuming processes ==")
        print(f"{'used':>5s} {'T':>3s} {'E':>5s} {'sig':>3s} {'cf':6s} {'category':28s} name")
        for r in sorted(sub, key=lambda r: (-r["n_used_by"], -r["n_elementary_flows"]))[: args.top]:
            print(
                f"{r['n_used_by']:5d} {r['n_technosphere_inputs']:3d} {r['n_elementary_flows']:5d} "
                f"{r['signature_groups']:3d} {r['confidence']:6s} {r['bafu_category'][:28]:28s} {r['name'][:66]}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
