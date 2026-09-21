"""Step 4 - the harness: score diff, flow diff, residual share and structural checks.

Score agreement is necessary, not sufficient (a 116-input fit matched all 25 scores to 1.000),
so the structural section is not optional."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import bw2data as bd

from . import db
from .lci import System
from .spec import Spec, walk

POWER_PLANT = re.compile(r"at power plant|power plant$|at run-of-river|at reservoir", re.I)


def run(spec: Spec, out_dir: Path = Path("results/checks")) -> Path:
    target = bd.get_node(database=db.INVENTORY_DB, code=spec.target_code)
    explicit = bd.get_node(database=db.SANDBOX_DB, code=f"{spec.target_code}-disagg")
    try:
        hybrid = bd.get_node(database=db.SANDBOX_DB, code=f"{spec.target_code}-hybrid")
    except Exception:
        hybrid = None
    sys_ = System(explicit)
    ids = [target.id, explicit.id] + ([hybrid.id] if hybrid else [])
    inv = sys_.cumulative(ids)
    b_t, b_e = inv[:, 0], inv[:, 1]
    s_t, s_e = sys_.scores(b_t), sys_.scores(b_e)
    s_h = sys_.scores(inv[:, 2]) if hybrid else None
    r = b_t - b_e
    s_r = sys_.scores(r)

    st = spec.strategy
    L = [f"# Check: {spec.target_name} ({spec.target_code})", "",
         f"target `{db.INVENTORY_DB}` vs explicit model `{explicit['code']}`" + (f" and hybrid `{hybrid['code']}`" if hybrid else ""), "",
         f"**Strategy:** {st.get('code', '?')} — {st.get('label', 'not recorded in the spec')}" + (f". {st['note']}" if st.get('note') else ""),
         f"**Calibrated inputs:** " + (", ".join(f"{i.name}" + (f" [{i.bounds[0]:.3g}–{i.bounds[1]:.3g}]" if i.bounds else "") for n in walk(spec.node) for i in n.inputs if i.free) or "none")
         + (f"; mass sum {spec.node.mass_sum}" if spec.node.mass_sum is not None else ""),
         f"**Links to rebuilt nodes:** " + (", ".join(i.name for n in walk(spec.node) for i in n.inputs if i.sandbox) or "none"), "",
         "## Scores (EF 3.1)", "",
         "| category | target | explicit | Δ explicit | residual share | hybrid/target |", "|---|---|---|---|---|---|"]
    worst = []
    for k, m in enumerate(sys_.methods):
        d = (s_e[k] / s_t[k] - 1) if s_t[k] else float("nan")
        share = s_r[k] / s_t[k] if s_t[k] else float("nan")
        hyb = f"{s_h[k] / s_t[k]:.6f}" if hybrid and s_t[k] else "—"
        worst.append((abs(d), k))
        L.append(f"| {m[2]} | {s_t[k]:.4g} | {s_e[k]:.4g} | {d:+.1%} | {share:+.1%} | {hyb} |")

    L += ["", "## Flow diff — worst categories, flows driving the gap (explicit − target, characterised)", ""]
    for _, k in sorted(worst, reverse=True)[:5]:
        c = sys_.cf[k]
        contrib = c * (b_e - b_t)
        rows = np.argsort(-np.abs(contrib))[:8]
        L.append(f"### {sys_.methods[k][2]} (Δ {worst[k][0]:+.1%})")
        L.append("")
        L.append("| flow | target | explicit | Δ impact | share of target score |")
        L.append("|---|---|---|---|---|")
        for row in rows:
            if contrib[row] == 0:
                continue
            L.append(f"| {sys_.flow_label(int(row))} | {b_t[row]:.3g} | {b_e[row]:.3g} | {contrib[row]:+.3g} | {contrib[row] / s_t[k]:+.1%} |")
        L.append("")

    L += ["## Structural checks", ""]
    nodes = list(walk(spec.node))
    n_inputs = sum(len(n.inputs) for n in nodes)
    agg = db.aggregated_codes()
    deps = [i.name for n in nodes for i in n.inputs if i.code in agg]
    plants = [i.name for n in nodes for i in n.inputs if POWER_PLANT.search(i.name)]
    kg_in = sum(i.amount for i in spec.node.inputs if i.unit.startswith("kilo") and not i.name.lower().startswith(("disposal", "transport")))
    kg_res = sum(f.amount for f in spec.node.resources if f.unit.startswith("kilo"))
    checks = [
        (n_inputs <= 30, f"{n_inputs} explicit input(s) over {len(nodes)} node(s)"),
        (not plants, "no decomposed grid mixes" if not plants else f"inputs are individual power plants: {plants}"),
        (not deps, "no dependency on another aggregated dataset" if not deps else f"depends on aggregated datasets (rebuild those first): {deps}"),
        (True, f"mass in: {kg_in:.3g} kg technosphere + {kg_res:.3g} kg resources per 1 {spec.node.unit} product (informational)"),
        (all(i.code or i.node for n in nodes for i in n.inputs), "all inputs resolved"),
    ]
    for ok, msg in checks:
        L.append(f"- {'✓' if ok else '✗'} {msg}")
    n_neg = int((r < 0).sum()); n_pos = int((r > 0).sum())
    L += ["", f"residual: {n_pos} flows under-explained, {n_neg} over-explained (negative residual)", ""]
    L += ["## Evidence", ""] + [f"- {e.get('source', '')} — {e.get('where', '')} {e.get('note', '')}".rstrip() for e in spec.evidence]

    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{spec.target_code}.md"
    out.write_text("\n".join(L) + "\n")
    # console summary
    med = float(np.nanmedian([abs(w) for w, _ in worst]))
    print(f"scores: median |Δ| {med:.1%}, worst {sys_.methods[max(worst)[1]][2]} {max(worst)[0]:+.1%}; "
          f"residual share median {float(np.nanmedian(np.abs(s_r / np.where(s_t == 0, np.nan, s_t)))):.1%}")
    for ok, msg in checks:
        print(f"  {'✓' if ok else '✗'} {msg}")
    print(f"report -> {out}")
    return out
