"""Find aggregated (system) processes by STRUCTURE, not by the ecoSpold type=2 flag.

    PYTHONPATH=$PWD/src ./.venv/bin/python scripts/find_system_processes.py [--project bafu-2026]

Writes results/system_terminated_extended.csv in the same schema as results/system_terminated.csv,
with two extra columns: `detected_by` (flag | structure) and `n_flows`.

Why this exists
---------------
`results/system_terminated.csv` is built from the ecoSpold `<dataSetInformation type="2">` flag.
That flag is reliable but not complete: BAFU also carries APME / PlasticsEurope era eco-profiles
that were never marked, and they are just as aggregated.

The giveaway is not how many elementary flows a dataset has — an unflagged eco-profile carries
~143, well under the ~1,650 of a flagged one, because it was never relinked to the full EF 3.1
list. The giveaway is that it has **no production input at all**: its only technosphere exchanges
are waste-treatment services and an infrastructure unit. A real unit process making styrene
consumes benzene and ethylene and energy; one that consumes nothing but "Disposal, ..." and
"Chemical plant, organics" has had its supply chain collapsed.

So the test is:
    no technosphere input that is a real supply (not `Disposal/Treatment/Recycling/Waste ...`,
    not an infrastructure unit priced in `unit`)   AND   a non-trivial biosphere vector

Guard against false positives: genuinely emission-only datasets (tyre and brake wear, disposal
of tailings, produced-water discharge, land provision, resource corrections) also have no supply
input — by design, because they model an emission, not a production. They are excluded by name.

Measured on BAFU-2026: the structural test recovers all 93 flagged datasets that have a biosphere
vector, and finds 39 more that the flag missed — benzene, styrene, propylene, butadiene, toluene,
the nylons, ABS, polycarbonate, PMMA, polyols, MDI/TDI, naphtha APME mix, and the ethylene and
propylene pipeline-system datasets.

NOTE: this does not change db.aggregated_codes(), which still reads the flag-based CSV. Switching
the benchmark's exclusion list over to the extended set would change every published benchmark
number, so that is a separate decision (see HANDOVER-flow-agreement-metric.md).
"""

from __future__ import annotations

import argparse
import csv
import html
import re
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import bw2data as bd  # noqa: E402

from reverse_bafu import db  # noqa: E402

WASTE = re.compile(r"^(disposal|treatment|recycling|waste)\b", re.I)
# datasets whose product IS an emission or a land movement: no supply chain by design
EMISSION_ONLY = re.compile(r"emissions?$|^disposal|^discharge|^provision|resource correction", re.I)


def is_supply(node) -> bool:
    """A real production input: not a waste-treatment service, not an infrastructure unit."""
    if WASTE.search(node["name"]):
        return False
    if node.get("unit") == "unit":
        return False
    return True


def cited_pdfs(code: str, pdf_by_title: dict, ecospold: Path, reports: Path) -> list[str]:
    f = ecospold / f"process_{code}.xml"
    if not f.exists():
        return []
    s = f.read_text(encoding="utf-8", errors="replace")
    head = s[: s.find("<flowData")] if "<flowData" in s else s[:30000]
    out = []
    for t in dict.fromkeys(html.unescape(x) for x in re.findall(r'<source\b[^>]*\btitle="([^"]*)"', head)):
        p = pdf_by_title.get(t, "")
        if p and (reports / p).exists() and p not in out:
            out.append(p)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="bafu-2026")
    ap.add_argument("--min-flows", type=int, default=50)
    ap.add_argument("--ecospold", default="data/ecospold")
    ap.add_argument("--reports", default="BAFU-2026 v1_Documentation/BAFU-2026 v1_Documentation/BAFU-2026 v1 LCI Reports")
    ap.add_argument("-o", "--out", default="results/system_terminated_extended.csv")
    a = ap.parse_args()

    db.set_project(a.project)
    flagged = {r["code"]: r for r in csv.DictReader(open("results/system_terminated.csv"))}
    pdf_by_title = {r["title"]: r["pdf"] for r in csv.DictReader(open("results/sources.csv"))}
    acts = bd.Database(db.INVENTORY_DB).load()

    rows, found = [], 0
    for key, act in acts.items():
        code = key[1]
        ex = act.get("exchanges", [])
        tech = [acts.get(tuple(e["input"])) for e in ex
                if e.get("type") == "technosphere" and tuple(e["input"]) != key]
        tech = [t for t in tech if t]
        n_flows = sum(1 for e in ex if e.get("type") == "biosphere")
        supply = [t for t in tech if is_supply(t)]
        structural = (not supply) and n_flows > a.min_flows and not EMISSION_ONLY.search(act["name"])
        if code not in flagged and not structural:
            continue
        if code not in flagged:
            found += 1
        base = flagged.get(code, {})
        rows.append({
            **{k: base.get(k, "") for k in ("family", "source", "pdf")},
            "code": code,
            "name": act["name"],
            "location": act.get("location", ""),
            "unit": act.get("unit", ""),
            "n_inputs": len(tech),
            "n_flows": n_flows,
            "detected_by": "flag" if code in flagged else "structure",
            "reports": "; ".join(cited_pdfs(code, pdf_by_title, Path(a.ecospold), Path(a.reports))),
        })

    rows.sort(key=lambda r: (r["detected_by"], r["name"]))
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} aggregated datasets -> {out}")
    print(f"   {len(rows) - found} carry the ecoSpold type=2 flag")
    print(f"   {found} found only by structure (no production input, >{a.min_flows} elementary flows)")
    with_report = sum(1 for r in rows if r["detected_by"] == "structure" and r["reports"])
    print(f"   of those {found}, {with_report} cite a report that is in the bundle")


if __name__ == "__main__":
    main()
