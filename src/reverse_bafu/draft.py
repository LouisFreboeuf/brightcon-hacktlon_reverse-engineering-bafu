"""Draft a spec from evidence, reproducibly.

Three layers, each leaving files under ``specs/evidence/<code>/``:

1. ``evidence``  deterministic: the report pages as text (pdftotext -layout), the target's
                 ecoSpold metadata, its direct-resource candidates, and a manifest with SHA-256s.
2. ``draft``     the LLM step, in two passes with fixed prompt templates (``prompts/``):
                 extraction (report excerpt -> line items with quotes) and mapping (line items +
                 keyword-search candidates -> BAFU dataset names). The rendered prompts, the raw
                 responses, model, effort and hashes are all saved. ``--dry-run`` writes the prompts
                 only, for running the model elsewhere; ``--from-response`` ingests such a response.
3. ``assemble``  deterministic: line items + mapping -> ``specs/<code>-<slug>.json`` with a
                 ``derivation`` on every input and a ``provenance`` block.

The model never returns byte-identical JSON; what is reproducible is the evidence, the exact
prompt, the pinned model, and an audit trail from every number to a quoted line.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from . import db
from .spec import slug

PROMPTS = Path("prompts")
EVIDENCE_ROOT = Path("specs/evidence")   # the benchmark re-points these two
SPEC_ROOT = Path("specs")
MODEL = "claude-opus-5"
EFFORT = "high"

# ---------------------------------------------------------------- schemas (structured output)
LINE_ITEM = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "kind": {"type": "string", "enum": ["input", "emission", "resource", "product", "co-product", "ignore"]},
        "quote": {"type": "string"},
        "raw_value": {"type": "number"},
        "raw_min": {"type": ["number", "null"]},
        "raw_max": {"type": ["number", "null"]},
        "raw_unit": {"type": "string"},
        "per": {"type": "string"},
        "factor": {"type": "number"},
        "factor_unit": {"type": "string"},
        "factor_source": {"type": "string"},
        "search": {"type": "string"},
        "compartment": {"type": "string", "enum": ["air", "water", "soil", "resources", ""]},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "note": {"type": "string"},
    },
    "required": ["name", "kind", "quote", "raw_value", "raw_min", "raw_max", "raw_unit", "per", "factor", "factor_unit",
                 "factor_source", "search", "compartment", "confidence", "note"],
    "additionalProperties": False,
}
EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "basis": {"type": "string", "description": "the excerpt's reference basis, e.g. 'per t burnt shale, 71.3 % allocation column'"},
        "basis_amount": {"type": "number", "description": "how many target units one basis corresponds to, e.g. 1000 for per-t values of a per-kg target"},
        "allocation": {"type": "string"},
        "mass_sum": {"type": ["number", "null"], "description": "if the excerpt states that the composition items add up to a mass per basis (e.g. 'adds up to 1.00 kg'), that mass; else null"},
        "items": {"type": "array", "items": LINE_ITEM},
        "gaps": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["basis", "basis_amount", "allocation", "mass_sum", "items", "gaps"],
    "additionalProperties": False,
}
MAPPING_SCHEMA = {
    "type": "object",
    "properties": {
        "mappings": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "item": {"type": "string"},
                "chosen": {"type": ["string", "null"]},
                "location": {"type": "string"},
                "compartment": {"type": "string", "description": "for emissions/resources: the chosen flow's compartment as listed"},
                "dependency": {"type": "boolean"},
                "reason": {"type": "string"},
            },
            "required": ["item", "chosen", "location", "compartment", "dependency", "reason"],
            "additionalProperties": False,
        }},
    },
    "required": ["mappings"],
    "additionalProperties": False,
}


LOCATE_SCHEMA = {
    "type": "object",
    "properties": {
        "found": {"type": "boolean"},
        "first_page": {"type": ["integer", "null"]},
        "last_page": {"type": ["integer", "null"]},
        "captions": {"type": "array", "items": {"type": "string"}},
        "reason": {"type": "string"},
    },
    "required": ["found", "first_page", "last_page", "captions", "reason"],
    "additionalProperties": False,
}
# `2.1`, `2-1`, `2.1.3` - some reports number with hyphens, and some put the label on its own line
# with the caption text on the next one (2017 - LCI wood and wood based products - Werner: 255 pages,
# zero captions before this was widened). LABEL_ONLY_RX catches that second form.
CAPTION_RX = re.compile(
    r"^\s*((?:Tab\.?|Table|Tabelle|Tableau|Fig\.?|Figure|Abb\.)\s*\d+(?:[.\-]\d+)*\s*[:.]?\s+.{6,140})", re.M)
LABEL_ONLY_RX = re.compile(
    r"^\s*((?:Tab\.?|Table|Tabelle|Tableau|Fig\.?|Figure|Abb\.)\s*\d+(?:[.\-]\d+)*\s*[:.]?)\s*$", re.M)
CACHE = Path(".cache/pdftext")


def pdf_pages(pdf: Path) -> list[str]:
    """Text of every page (pdftotext -layout), cached under .cache/pdftext/<sha256>/."""
    d = CACHE / sha256(pdf)
    if not (d / "n").exists():
        d.mkdir(parents=True, exist_ok=True)
        n = int(next(l for l in subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout.splitlines() if l.startswith("Pages:")).split()[1])
        for i in range(1, n + 1):
            subprocess.run(["pdftotext", "-layout", "-f", str(i), "-l", str(i), str(pdf), str(d / f"{i}.txt")], check=True)
        (d / "n").write_text(str(n))
    n = int((d / "n").read_text())
    return [(d / f"{i}.txt").read_text() for i in range(1, n + 1)]


def captions_index(pdf: Path) -> list[dict]:
    """Every table/figure caption with its PDF page - deterministic, language-neutral in form."""
    out, seen = [], set()
    for i, text in enumerate(pdf_pages(pdf), 1):
        # a label alone on its line: pull the next non-empty line up so it reads as one caption
        lines = text.splitlines()
        merged, skip = [], False
        for j, line in enumerate(lines):
            if skip:
                skip = False
                continue
            if LABEL_ONLY_RX.match(line):
                nxt = next((lines[k] for k in range(j + 1, min(j + 3, len(lines))) if lines[k].strip()), "")
                if nxt and not LABEL_ONLY_RX.match(nxt):
                    merged.append(f"{line.strip()} {nxt.strip()}")
                    skip = True
                    continue
            merged.append(line)
        for m in CAPTION_RX.finditer("\n".join(merged)):
            cap = re.sub(r"\s+", " ", m.group(1)).strip()
            if cap not in seen:
                seen.add(cap)
                out.append({"page": i, "caption": cap})
    return out


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------- layer 1: evidence
def evidence(code: str, report: Path, pages: str, ecospold_dir: Path, project: str) -> Path:
    """Write specs/evidence/<code>/: report text, target metadata, direct-resource candidates, manifest."""
    out = EVIDENCE_ROOT / code
    out.mkdir(parents=True, exist_ok=True)
    first, last = (pages.split("-") + [pages])[:2]
    txt = out / f"report-p{first}-{last}.txt"
    subprocess.run(["pdftotext", "-layout", "-f", first, "-l", last, str(report), str(txt)], check=True)

    xml = ecospold_dir / f"process_{code}.xml"
    ds = ET.parse(xml).getroot().find("dataset")
    pi = ds.find("metaInformation/processInformation")
    rf = pi.find("referenceFunction")
    src = ds.find("metaInformation/modellingAndValidation/source")
    tp = pi.find("timePeriod")
    meta = {
        "name": rf.get("name"), "unit": rf.get("unit"), "location": pi.find("geography").get("location"),
        "category": f"{rf.get('category')} / {rf.get('subCategory')}",
        "includedProcesses": rf.get("includedProcesses", ""), "generalComment": rf.get("generalComment", ""),
        "technology": pi.find("technology").get("text", "") if pi.find("technology") is not None else "",
        "source": " | ".join(x for x in (src.get("firstAuthor"), src.get("year"), src.get("title")) if x) if src is not None else "",
        "timePeriod": f"{tp.findtext('startYear') or tp.findtext('startDate') or ''}-{tp.findtext('endYear') or tp.findtext('endDate') or ''}" if tp is not None else "",
        "n_flows": len(ds.find("flowData").findall("exchange")),
    }
    # direct-resource candidates: resource flows of the target vector, largest first
    import bw2data as bd
    db.set_project(project)
    t = bd.get_node(database=db.INVENTORY_DB, code=code)
    res = []
    for e in t.biosphere():
        cats = " ".join(map(str, e.input.get("categories", ())))
        if "esource" in cats or cats.strip() in ("soil",):
            res.append({"name": e.input["name"], "amount": e["amount"], "unit": e.input["unit"], "categories": cats})
    res.sort(key=lambda r: -abs(r["amount"]))
    (out / "target.json").write_text(json.dumps({**meta, "direct_resource_candidates": res[:12]}, indent=1, ensure_ascii=False))
    manifest = {
        "code": code, "created": _now(),
        "report": {"file": report.name, "sha256": sha256(report), "pages": pages},
        "report_text": {"file": txt.name, "sha256": sha256(txt), "tool": subprocess.run(["pdftotext", "-v"], capture_output=True, text=True).stderr.splitlines()[0]},
        "ecospold": {"file": xml.name, "sha256": sha256(xml)},
        "brightway_project": project,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"evidence -> {out}/ ({txt.name}, target.json, manifest.json)")
    return out


# ---------------------------------------------------------------- layer 2: prompts + LLM
def render(template: Path, **kw) -> str:
    text = template.read_text()
    for k, v in kw.items():
        text = text.replace("{{" + k + "}}", str(v))
    missing = re.findall(r"\{\{(\w+)\}\}", text)
    if missing:
        raise SystemExit(f"unfilled placeholders in {template}: {missing}")
    return text


def target_meta(code: str, ecospold_dir: Path) -> dict:
    ds = ET.parse(ecospold_dir / f"process_{code}.xml").getroot().find("dataset")
    pi = ds.find("metaInformation/processInformation")
    rf = pi.find("referenceFunction")
    return {"name": rf.get("name"), "unit": rf.get("unit"), "location": pi.find("geography").get("location"),
            "category": f"{rf.get('category')} / {rf.get('subCategory')}", "includedProcesses": rf.get("includedProcesses", ""),
            "generalComment": rf.get("generalComment", ""),
            "technology": pi.find("technology").get("text", "") if pi.find("technology") is not None else ""}


def locate_prompt(code: str, pdf: Path, ecospold_dir: Path) -> tuple[str, list[dict]]:
    meta = target_meta(code, ecospold_dir)
    caps = captions_index(pdf)
    listing = "\n".join(f"- p.{c['page']}: {c['caption']}" for c in caps) or "- (no captions found)"
    n_pages = len(pdf_pages(pdf))
    return render(PROMPTS / "locate_pages.md", target_name=meta["name"], target_location=meta["location"], target_unit=meta["unit"],
                  target_category=meta["category"], included_processes=(meta["includedProcesses"] or "—")[:300],
                  technology=(meta["technology"] or "—")[:200], general_comment=(meta["generalComment"] or "—")[:300],
                  report_name=pdf.name, n_pages=n_pages, captions=listing), caps


def locate(code: str, pdf: Path, ecospold_dir: Path, dry_run: bool, from_response: Path | None, by: str) -> dict | None:
    """Pass 0: which PDF pages hold the dataset's inventory. Returns the validated response or None (dry run)."""
    ev = EVIDENCE_ROOT / code
    ev.mkdir(parents=True, exist_ok=True)
    prompt, caps = locate_prompt(code, pdf, ecospold_dir)
    (ev / "prompt-0-locate.md").write_text(prompt)
    (ev / "schema-0-locate.json").write_text(json.dumps(LOCATE_SCHEMA, indent=1))
    (ev / "captions-0-locate.json").write_text(json.dumps({"pdf": pdf.name, "sha256": sha256(pdf), "captions": caps}, indent=1, ensure_ascii=False))
    if from_response:
        resp = _load_response(from_response, LOCATE_SCHEMA, "locate")
        prov = {"model": "manual", "by": by, "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "at": _now()}
    elif dry_run:
        return None
    else:
        resp, prov = call_model(prompt, LOCATE_SCHEMA, "locate")
    (ev / "response-0-locate.json").write_text(json.dumps(resp, indent=1, ensure_ascii=False))
    (ev / "provenance-0-locate.json").write_text(json.dumps(prov, indent=1))
    return resp


def extraction_prompt(ev: Path) -> str:
    man = json.loads((ev / "manifest.json").read_text())
    meta = json.loads((ev / "target.json").read_text())
    cands = "\n".join(f"- {r['name']}: {r['amount']:.4g} {r['unit']} ({r['categories']})" for r in meta["direct_resource_candidates"]) or "- none"
    return render(PROMPTS / "draft_spec.md",
                  target_name=meta["name"], target_location=meta["location"], target_unit=meta["unit"], n_flows=meta["n_flows"],
                  target_category=meta["category"], included_processes=meta["includedProcesses"] or "—", technology=meta["technology"] or "—",
                  general_comment=meta["generalComment"] or "—", source=meta["source"] or "—", time_period=meta["timePeriod"] or "—",
                  direct_candidates=cands, evidence_file=man["report_text"]["file"], evidence_sha256=man["report_text"]["sha256"],
                  evidence_pages=man["report"]["pages"], report_name=man["report"]["file"],
                  evidence_text=(ev / man["report_text"]["file"]).read_text().strip())


def _matched(words: list[str], name: str) -> int:
    """Words matched at a word start ('particulate' matches 'particulates', 'dust' not 'industrial')."""
    return sum(1 for w in words if re.search(r"(?<![a-z0-9])" + re.escape(w), name))


def candidates_for(search: str, prefer_location: str = "", k: int = 8) -> list[dict]:
    """Deterministic keyword search over the BAFU name index. Rank: number of search words in the
    name (desc), then location preference (the target's, then RER/CH/DE/GLO), then name length."""
    words = [w for w in re.findall(r"[a-z0-9%]+", search.lower()) if len(w) > 2]
    order: dict[str, int] = {}
    for loc in [prefer_location, *db.LOCATION_PREFERENCE]:
        order.setdefault(loc, len(order))  # the target's location first, without being overwritten
    need = max(1, len(words) - 1)  # all words, or all but one
    hits = []
    for norm, entries in db.activity_index().items():
        n = _matched(words, norm)
        if n < need:
            continue
        for e in entries:
            hits.append((-n, order.get(e["location"], 99), len(e["name"]), e["name"], e["location"], e["code"], e))
    hits.sort(key=lambda t: t[:6])  # full key: ties never fall back to database iteration order
    return [t[6] for t in hits[:k]]


def flow_candidates_for(name: str, compartment: str, search: str = "", k: int = 8) -> list[dict]:
    """Deterministic search over the two biosphere databases: every word of the search phrase (or
    the name) matched at a word start; the hinted compartment first; one entry per (name, top-2
    categories)."""
    words = [w for w in re.findall(r"[a-z0-9]+", (search or name).lower()) if len(w) > 1 and w not in ("fossil", "geogenic", "carbonate", "to")]
    need = max(1, len(words) - 1)
    hits = []
    for norm, entries in db.flow_index().items():
        n = _matched(words, norm)
        if n < need:
            continue
        for e in entries:
            cats = " / ".join(e["categories"][:2])
            hits.append((-n, 0 if compartment and compartment in cats.lower() else 1, 0 if "unspecified" in cats.lower() else 1,
                         len(e["name"]), e["name"], cats, " / ".join(e["categories"]), e["database"], e["code"], {**e, "cats": cats}))
    hits.sort(key=lambda t: t[:9])  # full key, then dedupe: the representative of a (name, compartment) is fixed
    seen, out = set(), []
    for t in hits:
        key = (t[4], t[5])
        if key in seen:
            continue
        seen.add(key)
        out.append(t[9])
        if len(out) == k:
            break
    return out


def mapping_prompt(extraction: dict, target_location: str) -> tuple[str, dict]:
    lines, cand_record = [], {}
    for it in extraction["items"]:
        if it["kind"] == "input":
            cands = candidates_for(it["search"], target_location)
            cand_record[it["name"]] = cands
            c = "\n".join(f"    - {e['name']} [{e['location']}] ({e['unit']}, {e['n_inputs']} inputs{', aggregated' if e['aggregated'] else ''})" for e in cands) or "    - (no candidate found)"
            lines.append(f"- item: {it['name']}  (input)\n  quote: {it['quote']}\n  search: {it['search']}\n  candidates:\n{c}")
        elif it["kind"] in ("emission", "resource"):
            cands = flow_candidates_for(it["name"], it["compartment"], it["search"])
            cand_record[it["name"]] = cands
            c = "\n".join(f"    - {e['name']}  [{e['cats']}] ({e['unit']}, {e['database']})" for e in cands) or "    - (no candidate found)"
            lines.append(f"- item: {it['name']}  ({it['kind']} to {it['compartment'] or '?'})\n  quote: {it['quote']}\n  candidates (flow name [compartment]):\n{c}")
    return render(PROMPTS / "map_inputs.md", target_location=target_location, items="\n".join(lines)), cand_record


def call_model(prompt: str, schema: dict, label: str) -> tuple[dict, dict]:
    """One structured-output call; returns (parsed JSON, provenance)."""
    try:
        import anthropic
    except ImportError:
        raise SystemExit("the anthropic SDK is not installed: uv sync --extra llm   (or use --dry-run / --from-response)")
    client = anthropic.Anthropic()
    with client.messages.stream(
        model=MODEL, max_tokens=32000,
        thinking={"type": "adaptive"}, output_config={"effort": EFFORT, "format": {"type": "json_schema", "schema": schema}},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        msg = stream.get_final_message()
    if msg.stop_reason == "refusal":
        raise SystemExit(f"{label}: the model declined ({msg.stop_details})")
    text = next(b.text for b in msg.content if b.type == "text")
    prov = {"model": msg.model, "requested_model": MODEL, "effort": EFFORT, "message_id": msg.id, "stop_reason": msg.stop_reason,
            "usage": {"input_tokens": msg.usage.input_tokens, "output_tokens": msg.usage.output_tokens},
            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "at": _now(), "by": f"llm:{msg.model}"}
    return json.loads(text), prov


def _load_response(path: Path, schema: dict, label: str) -> dict:
    """A response obtained outside the API (Claude Code, claude.ai, by hand) is validated against
    the same schema the API would have enforced."""
    import jsonschema

    data = json.loads(path.read_text())
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as exc:
        raise SystemExit(f"{label}: {path} does not match the schema: {exc.message} (at {'/'.join(map(str, exc.absolute_path))})")
    return data


def draft(code: str, dry_run: bool, from_response: dict[str, Path] | None, project: str, variant: str = "draft") -> None:
    ev = EVIDENCE_ROOT / code
    if not (ev / "manifest.json").exists():
        raise SystemExit(f"no evidence for {code}: run `reverse-bafu evidence` first")
    meta = json.loads((ev / "target.json").read_text())
    db.set_project(project)

    # pass 1 — extraction
    p1 = extraction_prompt(ev)
    (ev / "prompt-1-extract.md").write_text(p1)
    (ev / "schema-1-extract.json").write_text(json.dumps(EXTRACTION_SCHEMA, indent=1))
    if from_response and "extract" in from_response:
        ext = _load_response(from_response["extract"], EXTRACTION_SCHEMA, "extraction")
        prov1 = {"model": "manual", "by": from_response.get("by", "manual"), "prompt_sha256": hashlib.sha256(p1.encode()).hexdigest(), "at": _now()}
    elif dry_run:
        print(f"dry run: extraction prompt -> {ev}/prompt-1-extract.md (schema beside it). Run it, save the JSON as response-1-extract.json, then rerun with --from-response")
        return
    else:
        ext, prov1 = call_model(p1, EXTRACTION_SCHEMA, "extraction")
    (ev / "response-1-extract.json").write_text(json.dumps(ext, indent=1, ensure_ascii=False))
    (ev / "provenance-1-extract.json").write_text(json.dumps(prov1, indent=1))

    # pass 2 — mapping (deterministic candidates + one call)
    p2, cands = mapping_prompt(ext, meta["location"])
    (ev / "prompt-2-map.md").write_text(p2)
    (ev / "candidates-2-map.json").write_text(json.dumps(cands, indent=1, ensure_ascii=False))
    (ev / "schema-2-map.json").write_text(json.dumps(MAPPING_SCHEMA, indent=1))
    if from_response and "map" in from_response:
        mp = _load_response(from_response["map"], MAPPING_SCHEMA, "mapping")
        prov2 = {"model": "manual", "by": from_response.get("by", "manual"), "prompt_sha256": hashlib.sha256(p2.encode()).hexdigest(), "at": _now()}
    elif dry_run or (from_response and "map" not in from_response):
        print(f"mapping prompt -> {ev}/prompt-2-map.md (candidates from a deterministic name search beside it). Run it, save as response-2-map.json, rerun with --from-response")
        return
    else:
        mp, prov2 = call_model(p2, MAPPING_SCHEMA, "mapping")
    (ev / "response-2-map.json").write_text(json.dumps(mp, indent=1, ensure_ascii=False))
    (ev / "provenance-2-map.json").write_text(json.dumps(prov2, indent=1))
    assemble(code, project, variant)


# ---------------------------------------------------------------- batch: every row of the CSV
def advance(code: str, name: str, pdf: Path, ecospold_dir: Path, project: str, dry_run: bool, by: str,
            rec: dict, variant: str = "draft") -> None:
    """Take one dataset as far as its on-disk state allows: locate -> evidence -> extract -> map ->
    assemble. Fills rec["status"] / rec["note"] / rec["pages"]; never overwrites an existing spec."""
    existing = SPEC_ROOT / f"{code[:8]}-{slug(name)}.{variant}.json"
    ev = EVIDENCE_ROOT / code
    if existing.exists():
        rec["status"], rec["note"] = "drafted", f"{existing} exists (kept; delete it to re-assemble)"
        ev0 = ev / "response-0-locate.json"
        if ev0.exists():
            r0 = json.loads(ev0.read_text())
            rec["pages"] = f"{r0.get('first_page')}-{r0.get('last_page')}" if r0.get("found") else ""
        return
    try:
        if (ev / "response-0-locate.json").exists():
            resp0 = json.loads((ev / "response-0-locate.json").read_text())
        else:
            resp0 = locate(code, pdf, ecospold_dir, dry_run, None, by)
        if resp0 is None:
            rec["status"], rec["note"] = "prompt-0-written", "answer prompt-0-locate.md, save as response-0-locate.json, rerun"
            return
        if not resp0["found"]:
            rec["status"], rec["note"] = "pages-not-found", resp0["reason"]
            return
        pages = f"{resp0['first_page']}-{resp0['last_page']}"
        rec["pages"] = pages
        if not (ev / "manifest.json").exists():
            evidence(code, pdf, pages, ecospold_dir, project)
        fr = {}
        if (ev / "response-1-extract.json").exists():
            fr["extract"] = ev / "response-1-extract.json"
        if (ev / "response-2-map.json").exists():
            fr["map"] = ev / "response-2-map.json"
        fr["by"] = by
        if dry_run and "extract" not in fr:
            draft(code, True, None, project, variant)
            rec["status"], rec["note"] = "prompt-1-written", "answer prompt-1-extract.md, save as response-1-extract.json, rerun"
            return
        if dry_run and "map" not in fr:
            draft(code, False, fr, project, variant)  # renders prompt 2 from the extract response, stops
            rec["status"], rec["note"] = "prompt-2-written", "answer prompt-2-map.md, save as response-2-map.json, rerun"
            return
        draft(code, False, fr if len(fr) > 1 else None, project, variant)
        rec["status"], rec["note"] = "drafted", str(existing)
    except SystemExit as exc:
        rec["status"], rec["note"] = "error", str(exc)[:200]


def cited_reports(code: str, csv_source: str, pdf_by_title: dict, ecospold_dir: Path) -> list[str]:
    """Every report PDF this dataset cites that is present in the bundle.

    A dataset can cite more than one source, and the extra ones are only in the ecoSpold XML -
    results/system_terminated.csv carries a single "author | year | title" string. Taking just
    that one hid the 2025 plastics report behind all 14 PlasticsEurope datasets, the family with
    the largest downstream reach, which were recorded as having no report at all.
    """
    titles: list[str] = []
    if csv_source:
        titles.append(csv_source.split(" | ")[-1])
    xml = ecospold_dir / f"process_{code}.xml"
    if xml.exists():
        text = xml.read_text(encoding="utf-8", errors="replace")
        head = text[: text.find("<flowData")] if "<flowData" in text else text[:30000]
        titles += [html.unescape(t) for t in re.findall(r'<source\b[^>]*\btitle="([^"]*)"', head)]
    out: list[str] = []
    for t in dict.fromkeys(x for x in titles if x):
        pdf = pdf_by_title.get(t, "")
        if pdf and pdf not in out:
            out.append(pdf)
    return out


def draft_all(project: str, ecospold_dir: Path, reports: Path, dry_run: bool, only: set[str] | None, by: str,
              status_path: Path = Path("results/drafting_status.csv"),
              datasets: Path = Path("results/system_terminated.csv")) -> None:
    """One entry point for all system-terminated datasets: find the report, locate the pages, extract,
    map, assemble - recording per dataset how far it got and why it stopped."""
    import csv

    rows = list(csv.DictReader(open(datasets)))
    pdf_by_title = {r["title"]: r["pdf"] for r in csv.DictReader(open("results/sources.csv"))}
    status: list[dict] = []
    for r in rows:
        code, name = r["code"], r["name"]
        if only and code not in only and code[:8] not in only:
            continue
        rec = {"code": code, "name": name, "family": r.get("family", "") or r.get("detected_by", ""), "pdf": "", "pages": "", "status": "", "note": ""}
        status.append(rec)
        title = r["source"].split(" | ")[-1] if r["source"] else ""
        candidates = [p for p in cited_reports(code, r["source"], pdf_by_title, ecospold_dir) if (reports / p).exists()]
        pdf_name = candidates[0] if candidates else ""
        if not pdf_name and not (SPEC_ROOT / f"{code[:8]}-{slug(name)}.draft.json").exists():
            rec["status"], rec["note"] = "no-pdf", f"family {r.get('family','') or r.get('detected_by','')}: no report in the documentation bundle for '{title or 'no source'}'"
            continue
        rec["pdf"] = pdf_name
        advance(code, name, reports / pdf_name, ecospold_dir, project, dry_run, by, rec)
    status_path.parent.mkdir(parents=True, exist_ok=True)
    with status_path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(status[0]))
        w.writeheader(); w.writerows(status)
    from collections import Counter
    print(f"\n{len(status)} datasets -> {status_path}")
    for k, n in Counter(x["status"] for x in status).most_common():
        print(f"  {n:3d}  {k}")


# ---------------------------------------------------------------- layer 3: assemble the spec
UNITS = {"kg": "kilogram", "MJ": "megajoule", "kWh": "kilowatt hour", "m3": "cubic meter", "tkm": "ton kilometer", "l": "litre",
         "unit": "unit", "m2": "square meter", "m": "meter", "t": "ton", "kBq": "kilo Becquerel"}


def assemble(code: str, project: str, variant: str = "draft") -> Path:
    db.set_project(project)
    ev = EVIDENCE_ROOT / code
    meta = json.loads((ev / "target.json").read_text())
    man = json.loads((ev / "manifest.json").read_text())
    ext = json.loads((ev / "response-1-extract.json").read_text())
    mp = json.loads((ev / "response-2-map.json").read_text())
    prov1 = json.loads((ev / "provenance-1-extract.json").read_text())
    prov2 = json.loads((ev / "provenance-2-map.json").read_text())
    chosen = {m["item"]: m for m in mp["mappings"]}
    cands = json.loads((ev / "candidates-2-map.json").read_text()) if (ev / "candidates-2-map.json").exists() else {}
    scale = 1.0 / float(ext["basis_amount"] or 1.0)  # per basis -> per 1 target unit

    def rebuilt_node(item: str, name: str, location: str) -> str:
        """If the chosen dataset is itself aggregated and a rebuilt node of it exists in the sandbox,
        link that node ("terminate on the database" prefers a unit process over a sealed one)."""
        import bw2data as bd
        for e in cands.get(item, []):
            if e.get("name") == name and e.get("aggregated") and (not location or e.get("location") == location):
                for suffix in ("-disagg", "-draft-disagg"):
                    try:
                        bd.get_node(database=db.SANDBOX_DB, code=e["code"] + suffix)
                        return e["code"] + suffix
                    except Exception:
                        continue
        return ""

    inputs, emissions, resources, skipped = [], [], [], []
    for it in ext["items"]:
        amount = it["raw_value"] * it["factor"] * scale
        deriv = {"evidence": man["report_text"]["file"], "quote": it["quote"], "raw_value": it["raw_value"], "raw_unit": it["raw_unit"],
                 "per": it["per"], "factor": it["factor"], "factor_unit": it["factor_unit"], "factor_source": it["factor_source"],
                 "scale_to_unit": scale, "confidence": it["confidence"], "by": prov1.get("by", "llm"), "reviewed_by": None}
        unit = UNITS.get(it["factor_unit"] or it["raw_unit"], it["factor_unit"] or it["raw_unit"])
        if it["kind"] == "input":
            m = chosen.get(it["name"])
            if not m or not m["chosen"]:
                skipped.append(f"{it['name']}: no dataset chosen ({m['reason'] if m else 'not mapped'})")
                continue
            entry = {"name": m["chosen"], "amount": amount, "unit": unit, "location": m["location"], "note": it["note"],
                     "derivation": {**deriv, "search": it["search"], "mapping_reason": m["reason"], "mapping_by": prov2.get("by", "llm")}}
            sb = rebuilt_node(it["name"], m["chosen"], m["location"]) if m.get("dependency") else ""
            if sb:
                entry["sandbox"] = sb
                entry["derivation"]["linked_rebuilt_node"] = sb
            if it["raw_min"] is not None and it["raw_max"] is not None and it["raw_min"] != it["raw_max"]:
                entry["free"] = True
                entry["bounds"] = [it["raw_min"] * it["factor"] * scale, it["raw_max"] * it["factor"] * scale]
            inputs.append(entry)
        elif it["kind"] in ("emission", "resource"):
            m = chosen.get(it["name"])
            if not m or not m["chosen"]:
                skipped.append(f"{it['name']}: no flow chosen ({m['reason'] if m else 'not mapped'})")
                continue
            entry = {"name": m["chosen"], "category": (m.get("compartment") or it["compartment"] or "air").split("/")[0].strip().lower().replace("emissions to ", ""),
                     "amount": amount, "unit": unit, "note": it["note"],
                     "derivation": {**deriv, "mapping_reason": m["reason"], "mapping_by": prov2.get("by", "llm")}}
            (emissions if it["kind"] == "emission" else resources).append(entry)
        else:
            skipped.append(f"{it['name']}: {it['kind']} — {it['note']}")
    spec = {
        "target": {"code": code, "name": meta["name"], "location": meta["location"]},
        "variant": variant,  # sandbox nodes get <code>-<variant>-disagg so a hand-written rebuild of the same target is kept
        "strategy": {"code": "S1", "label": "transcription drafted from the report excerpt by the LLM pipeline (reverse-bafu draft)",
                     "note": f"basis: {ext['basis']}; allocation: {ext['allocation'] or 'none stated'}. Review every derivation; unreviewed entries have reviewed_by = null."},
        "evidence": [{"source": man["report"]["file"], "where": f"pages {man['report']['pages']} -> {man['report_text']['file']}",
                      "note": f"report sha256 {man['report']['sha256'][:16]}…, text sha256 {man['report_text']['sha256'][:16]}…"}],
        "provenance": {"pipeline": "reverse-bafu draft", "evidence_manifest": str(ev / "manifest.json"), "extraction": prov1, "mapping": prov2,
                       "gaps_reported_by_model": ext["gaps"], "skipped_items": skipped, "assembled_at": _now()},
        "node": {"name": f"{meta['name']}, disaggregated", "unit": meta["unit"], "location": meta["location"],
                 "comment": f"drafted from {man['report']['file']} pp. {man['report']['pages']}",
                 **({"mass_sum": ext["mass_sum"] * scale} if ext.get("mass_sum") else {}),
                 "inputs": inputs, "emissions": emissions, "resources": resources},
    }
    SPEC_ROOT.mkdir(parents=True, exist_ok=True)
    out = SPEC_ROOT / f"{code[:8]}-{slug(meta['name'])}.{variant}.json"
    out.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n")
    print(f"assembled -> {out}: {len(inputs)} inputs, {len(emissions)} emissions, {len(resources)} resources; skipped {len(skipped)}; gaps: {len(ext['gaps'])}")
    for s in skipped:
        print("  skipped:", s)
    return out
