"""Regenerate the artifact pages under artifacts/ from the specs, the sandbox and the check reports.

    uv run python scripts/render_pages.py [--project reverse-bafu]

Writes artifacts/rebuilt-inventories.html (one tab per spec). The page is static HTML; publish it
with the Artifact tool or open it locally.
"""

from __future__ import annotations

import argparse
import glob
import html
import json
import re
import warnings
from pathlib import Path

import bw2calc as bc
import bw2data as bd

from reverse_bafu import db

esc = html.escape


def fmt(x: float) -> str:
    ax = abs(x)
    if ax == 0:
        return "0"
    if ax >= 100:
        return f"{x:,.0f}"
    if ax >= 1e-3:
        return f"{x:.3g}"
    return f"{x:.2e}"


def collect(project: str) -> list[dict]:
    db.set_project(project)
    methods = db.methods()
    units = {m[2]: bd.Method(m).metadata.get("unit", "") for m in methods}
    cc = next(m for m in methods if m[2] == "Climate change")
    agg = db.aggregated_codes()
    out = []
    for path in sorted(glob.glob("specs/*.json")):
        sp = json.load(open(path))
        code = sp["target"]["code"]
        t = bd.get_node(database=db.INVENTORY_DB, code=code)
        e = bd.get_node(database=db.SANDBOX_DB, code=code + "-disagg")
        h = bd.get_node(database=db.SANDBOX_DB, code=code + "-hybrid")
        md = Path(f"results/checks/{code}.md").read_text()
        scores = []
        for line in md.splitlines():
            m = re.match(r"\| (.+?) \| ([-\d.e+]+) \| ([-\d.e+]+) \| ([-+\d.]+)% \| ([-+\d.]+)% \| ([-\d.—]+) \|", line)
            if m:
                scores.append(dict(cat=m.group(1), unit=units.get(m.group(1), ""), target=float(m.group(2)),
                                   explicit=float(m.group(3)), delta=float(m.group(4))))
        checks = [dict(ok=c[0] == "✓", msg=c[1]) for c in re.findall(r"^- ([✓✗]) (.+)$", md, re.M)]
        tb = sorted(t.biosphere(), key=lambda x: -abs(x["amount"]))
        inputs = []
        for x, si in zip(e.technosphere(), sp["node"]["inputs"]):
            l = bc.LCA({x.input: x["amount"]}, cc); l.lci(); l.lcia()
            inputs.append(dict(name=x.input["name"], loc=x.input["location"], amount=x["amount"], unit=x.input["unit"],
                               climate=l.score, free=si.get("free", False), bounds=si.get("bounds"), note=si.get("note", ""),
                               sandbox=bool(si.get("sandbox")), aggregated=x.input["database"] == db.INVENTORY_DB and x.input["code"] in agg))
        direct = [dict(name=x.input["name"], amount=x["amount"], unit=x.input["unit"],
                       cat="/".join(map(str, x.input["categories"][:2]))) for x in e.biosphere()]
        lt = bc.LCA({t: 1}, cc); lt.lci(); lt.lcia()
        hb = [x for x in h.biosphere() if "residual" in (x.get("comment") or "")]
        st = sp.get("strategy", {})
        out.append(dict(code=code, key=code[:8], name=t["name"], loc=t["location"], unit=t["unit"], n_bio=len(tb),
                        n_techno=len(list(t.technosphere())),
                        top_flows=[dict(name=x.input["name"], amount=x["amount"], unit=x.input["unit"],
                                        cat="/".join(map(str, x.input["categories"][:2]))) for x in tb[:6]],
                        strategy=f"{st.get('code', '?')} · {st.get('label', '')}", strategy_note=st.get("note", ""),
                        climate_target=lt.score, inputs=inputs, direct=direct, scores=scores, checks=checks,
                        n_residual=len(hb), n_residual_neg=sum(1 for x in hb if x["amount"] < 0),
                        evidence=sp.get("evidence", []), within10=sum(1 for s in scores if abs(s["delta"]) <= 10)))
    return out


def render(inv: list[dict]) -> str:
    tabs = "".join(f'<button class="tab" data-k="{o["key"]}" id="tab-{o["key"]}" aria-selected="{"true" if i == 0 else "false"}">{esc(o["name"])}<span class="loc">{o["loc"]}</span></button>' for i, o in enumerate(inv))
    ov = ""
    for o in inv:
        cc = next(s for s in o["scores"] if s["cat"] == "Climate change")
        n_free = sum(1 for i in o["inputs"] if i["free"])
        deps = [i["name"] for i in o["inputs"] if i["aggregated"]]
        ov += (f'<tr><td class="n"><b>{esc(o["name"])}</b><span class="loc">{o["loc"]}</span><br><span class="muted">{esc(o["strategy"])}</span></td>'
               f'<td class="num">{o["n_techno"]} → {len(o["inputs"])}</td><td class="num">{o["n_bio"]:,} → {len(o["direct"])}</td><td class="num">{n_free}</td>'
               f'<td class="num">{cc["delta"]:+.1f} %</td><td class="num">{o["within10"]} / 25</td><td class="num">{o["n_residual_neg"]} / {o["n_residual"]}</td>'
               f'<td>{"—" if not deps else "depends on aggregated: " + esc(", ".join(deps))}</td></tr>')
    panels = ""
    for i, o in enumerate(inv):
        mx = max(x["climate"] for x in o["inputs"]) or 1
        rows = ""
        for x in sorted(o["inputs"], key=lambda x: -x["climate"]):
            flags = ""
            if x["sandbox"]:
                flags += '<span class="tag blue">rebuilt node</span>'
            if x["aggregated"]:
                flags += '<span class="tag warn">aggregated dataset</span>'
            if x["free"]:
                b = x["bounds"]; at = ""
                if b:
                    if abs(x["amount"] - b[0]) <= 1e-6 * max(1, abs(b[0])):
                        at = " · at lower bound"
                    elif abs(x["amount"] - b[1]) <= 1e-6 * max(1, abs(b[1])):
                        at = " · at upper bound"
                flags += f'<span class="tag">calibrated{esc(at)}</span>'
            note = f'<div class="note">{esc(x["note"])}</div>' if x["note"] else ""
            rows += (f'<tr><td class="n">{esc(x["name"])}<span class="loc">{esc(x["loc"] or "sandbox")}</span>{flags}{note}</td>'
                     f'<td class="num">{fmt(x["amount"])}</td><td class="u">{esc(x["unit"])}</td>'
                     f'<td class="bar"><span class="fill" style="width:{max(0.5, 100 * x["climate"] / mx):.1f}%"></span><span class="v">{fmt(x["climate"])}</span></td></tr>')
        drows = "".join(f'<tr><td class="n">{esc(f["name"])}<span class="loc">{esc(f["cat"])}</span></td><td class="num">{fmt(f["amount"])}</td><td class="u">{esc(f["unit"])}</td></tr>' for f in o["direct"]) or '<tr><td colspan="3" class="muted">none — the report prints no direct emissions for this step</td></tr>'
        top = "".join(f'<li><span class="num">{fmt(f["amount"])}</span> <span class="u">{esc(f["unit"])}</span> {esc(f["name"])} <span class="loc">{esc(f["cat"].split("/")[-1])}</span></li>' for f in o["top_flows"])
        checks = "".join(f'<li><span class="{"ok" if c["ok"] else "bad"}">{"✓" if c["ok"] else "✗"}</span><span>{esc(c["msg"])}</span></li>' for c in o["checks"])
        ev = "".join(f'<li><b>{esc(e["source"])}</b> — {esc(e["where"])}<br><span class="muted">{esc(e.get("note", ""))}</span></li>' for e in o["evidence"])
        sum_clim = sum(x["climate"] for x in o["inputs"]); direct_co2 = sum(f["amount"] for f in o["direct"] if f["name"].startswith("Carbon Dioxide (fossil)"))
        panels += f'''<section class="panel" id="panel-{o["key"]}" {"" if i == 0 else "hidden"}>
<div class="flow">
 <div class="box orig"><div class="eyebrow">Original · bafu‑2026</div><div class="big">{o["n_techno"]} inputs<br>{o["n_bio"]:,} flows</div><div class="muted">{esc(o["name"])} · {o["loc"]} · per 1 {esc(o["unit"])}</div><ul>{top}</ul></div>
 <div class="arrow">→</div>
 <div class="box new"><div class="eyebrow">Rebuilt · {esc(o["strategy"].split(" ")[0])}</div><div class="big">{len(o["inputs"])} inputs<br>{len(o["direct"])} direct flows</div><div class="muted">{esc(o["strategy_note"])}</div></div>
 <div class="arrow">→</div>
 <div class="box"><div class="eyebrow">Hybrid · S5</div><div class="big">+ {o["n_residual"]:,} residual</div><div class="muted">{o["n_residual_neg"]} negative (over‑explained), {o["n_residual"] - o["n_residual_neg"]} positive; scores equal the original by construction</div></div>
</div>
<h3>Technosphere inputs <span class="muted">· per 1 {esc(o["unit"])} · bar = climate contribution, scaled to the largest input</span></h3>
<div class="tbl"><table><thead><tr><th>Input</th><th style="text-align:right">Amount</th><th>Unit</th><th>kg CO₂‑eq</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="muted small">Inputs together: {fmt(sum_clim)} kg CO₂‑eq{f" · direct CO₂: {fmt(direct_co2)} kg" if direct_co2 else ""} · original: {fmt(o["climate_target"])} kg CO₂‑eq per {esc(o["unit"])}.</p>
<h3>Direct elementary flows</h3>
<div class="tbl"><table><thead><tr><th>Flow</th><th style="text-align:right">Amount</th><th>Unit</th></tr></thead><tbody>{drows}</tbody></table></div>
<h3>Deviation from the original <span class="muted">· explicit model, per EF 3.1 category · symmetric‑log axis · band ±10 %</span></h3>
<div class="chart" data-k="{o["key"]}"></div>
<h3>Structural checks</h3><ul class="checks">{checks}</ul>
<h3>Evidence</h3><ul class="ev">{ev}</ul>
</section>'''
    tmpl = Path("scripts/templates/rebuilt-inventories.tmpl.html").read_text()
    data = json.dumps({o["key"]: [dict(cat=s["cat"], unit=s["unit"], target=s["target"], explicit=s["explicit"], delta=s["delta"]) for s in o["scores"]] for o in inv})
    return (tmpl.replace("{{N}}", str(len(inv))).replace("{{OVERVIEW}}", ov).replace("{{TABS}}", tabs)
                .replace("{{PANELS}}", panels).replace("{{DATA}}", data))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--project", default="reverse-bafu")
    args = p.parse_args()
    warnings.filterwarnings("ignore")
    inv = collect(args.project)
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/rebuilt-inventories.html").write_text(render(inv))
    for o in inv:
        cc = next(s for s in o["scores"] if s["cat"] == "Climate change")
        print(f"{o['name'][:40]:40s} {o['strategy'][:4]}  inputs {o['n_techno']}→{len(o['inputs'])}  climate {cc['delta']:+.1f}%  within±10% {o['within10']}/25")
    print("-> artifacts/rebuilt-inventories.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
