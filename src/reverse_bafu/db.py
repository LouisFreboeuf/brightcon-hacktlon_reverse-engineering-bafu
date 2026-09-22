"""Brightway access: the BAFU database, the sandbox, and name resolution."""

from __future__ import annotations

import csv
import difflib
import re
from functools import lru_cache
from pathlib import Path

import bw2data as bd

INVENTORY_DB = "bafu-2026"
BIOSPHERE_DBS = ("ef-3.1-biosphere", "bafu-2026-residual")
SANDBOX_DB = "reverse-bafu-sandbox"
SYSTEM_TERMINATED_CSV = Path("results/system_terminated.csv")

# when a name matches in several locations and the spec does not say which
LOCATION_PREFERENCE = ("RER", "CH", "DE", "GLO", "Europe")


def set_project(project: str) -> None:
    if project not in bd.projects:
        raise SystemExit(f"Brightway project {project!r} not found; run `uv run sentier-brightway db --project {project}`")
    bd.projects.set_current(project)



@lru_cache(maxsize=1)
def aggregated_codes() -> frozenset[str]:
    """Codes of the ecoSpold type=2 datasets, from the screening CSV (empty set if absent)."""
    if not SYSTEM_TERMINATED_CSV.exists():
        return frozenset()
    return frozenset(r["code"] for r in csv.DictReader(SYSTEM_TERMINATED_CSV.open()))


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


@lru_cache(maxsize=1)
def activity_index() -> dict[str, list[dict]]:
    """normalised name -> [{code, location, unit, n_inputs, aggregated}] for the BAFU database."""
    idx: dict[str, list[dict]] = {}
    agg = aggregated_codes()
    for key, act in bd.Database(INVENTORY_DB).load().items():
        n_in = sum(1 for e in act.get("exchanges", []) if e.get("type") == "technosphere")
        idx.setdefault(_norm(act["name"]), []).append(
            {"name": act["name"], "code": key[1], "location": act.get("location", ""), "unit": act.get("unit", ""),
             "n_inputs": n_in, "aggregated": key[1] in agg})
    return idx


@lru_cache(maxsize=1)
def flow_index() -> dict[str, list[dict]]:
    """normalised name -> [{database, code, categories, unit}] over both biosphere databases."""
    idx: dict[str, list[dict]] = {}
    for dbname in BIOSPHERE_DBS:
        for key, flow in bd.Database(dbname).load().items():
            idx.setdefault(_norm(flow["name"]), []).append(
                {"name": flow["name"], "database": dbname, "code": key[1],
                 "categories": tuple(str(c) for c in flow.get("categories", ())), "unit": flow.get("unit", "")})
    return idx


def resolve_activity(name: str, location: str = "", prefer: str = "") -> tuple[dict | None, list[str]]:
    """Best BAFU activity for a name (+ optional location); (None, suggestions) if nothing matches."""
    idx = activity_index()
    cands = idx.get(_norm(name), [])
    if not cands:
        close = difflib.get_close_matches(_norm(name), idx.keys(), n=5, cutoff=0.6)
        return None, [idx[c][0]["name"] for c in close]
    if location:
        exact = [c for c in cands if c["location"] == location]
        if exact:
            return exact[0], []
    for loc in (prefer, *LOCATION_PREFERENCE):
        for c in cands:
            if c["location"] == loc:
                return c, []
    return cands[0], []


def resolve_flow(name: str, category: str = "") -> tuple[dict | None, list[str]]:
    """Best biosphere flow for a name and a top-level category hint ('air', 'water', 'soil', 'resources').
    EF 3.1 flows exist in several sub-compartments; prefer the 'unspecified' one."""
    idx = flow_index()
    cands = idx.get(_norm(name), [])
    if not cands:
        close = difflib.get_close_matches(_norm(name), idx.keys(), n=5, cutoff=0.6)
        return None, [idx[c][0]["name"] for c in close]
    hint = category.lower()
    def score(c: dict) -> tuple:
        cats = " / ".join(c["categories"]).lower()
        return (hint in cats, "unspecified" in cats and "long-term" not in cats, c["database"] == BIOSPHERE_DBS[0])
    best = max(cands, key=score)
    return best, []


def sandbox() -> bd.Database:
    if SANDBOX_DB not in bd.databases:
        db = bd.Database(SANDBOX_DB)
        db.register(depends=[INVENTORY_DB, *BIOSPHERE_DBS], comment="reverse-bafu: rebuilt unit processes")
    return bd.Database(SANDBOX_DB)
