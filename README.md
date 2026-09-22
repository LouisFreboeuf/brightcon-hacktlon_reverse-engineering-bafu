# brightcon-hackathon: reverse-engineering BAFU

Brightcon 2026 hackathon project for [brightcon-2026-material#38](https://github.com/Depart-de-Sentier/brightcon-2026-material/issues/38):
replace the aggregated ("system terminated") datasets of BAFU-2026 with unit process data and check
that the results stay the same.

What is here: the BAFU-2026 v1 inventory installed into Brightway 2.5 via
[sentier-brightway](https://github.com/sentier-dev/sentier-brightway); scripts that find the 101
aggregated datasets and the reports behind them; the `reverse-bafu` pipeline that rebuilds one
aggregated dataset from a JSON *spec* (resolve → calibrate → build → check); a reproducible way to
draft such specs from report PDFs; and a benchmark on synthetic aggregated datasets with known
answers. The documentation is the set of pages under [artifacts/](artifacts/): the method
explainer, the evidence page on the 101, the rebuilt inventories, and the developer walkthrough.

Steps 1–3 below reproduce everything committed under `results/`; 4–6 are for new work.

## 1. Setup

Needs [uv](https://docs.astral.sh/uv/) and `pdftotext` (Debian/Ubuntu: `apt install poppler-utils`;
only used by `reverse-bafu evidence`). Python 3.12 is picked up automatically.

```bash
uv sync                         # sentier-brightway (pinned commit), bw2data 4, bw2calc 2, numpy, scipy, jsonschema
uv sync --extra llm             # optional: the anthropic SDK, for `reverse-bafu draft` against the API
```

### The BAFU files

Download **both** of these from openLCA Nexus, <https://nexus.openlca.org/downloads> (free account;
accept BAFU's terms of use). Both stay gitignored (citation at the end).

| Nexus download | Zip you get | Unzip to | Needed by |
|---|---|---|---|
| **BAFU:2026 Version 1 - ecoSpold1** | `BAFU-2026 v1_ecoSpold v1.zip` (11,948 `process_<uuid>.xml`) | `data/ecospold/` — the zip's inner folder is `ecoSpold files/`, rename it | steps 3 and 5 (the ecoSpold metadata, incl. the `type=2` flag the Brightway import drops) |
| **BAFU:2026 Version 1 - Documentation** | `BAFU-2026 v1_Documentation.zip` (114 LCI report PDFs) | `BAFU-2026 v1_Documentation/` next to this README, keeping the inner `BAFU-2026 v1_Documentation/BAFU-2026 v1 LCI Reports/` layout | step 3 (`pdf` column) and step 5 (`--report`) |

```bash
unzip "BAFU-2026 v1_ecoSpold v1.zip" -d data/ && mv "data/ecoSpold files" data/ecospold
unzip "BAFU-2026 v1_Documentation.zip"
```

Note that step 2, the Brightway import, reads **neither** zip: `sentier-brightway` downloads its
own copy of the BAFU inventory — parquet files in the Sentier data repos, already converted from
the ecoSpold XML, pinned by commit and SHA-256 — so the import works without the Nexus files. The
zips are needed for what that conversion does not carry: the ecoSpold metadata (the `type=2` flag,
comments, sources) and the report PDFs. Other locations: `--ecospold <folder>` on the scripts,
`--reports` / `--report` for the PDFs.

## 2. Import BAFU-2026 into Brightway 2.5

```bash
uv run sentier-brightway coverage                    # downloads ~40 MB of pinned Sentier parquet (cached in ~/.cache/sentier-brightway)
uv run sentier-brightway db --project reverse-bafu   # ~3-4 min; --overwrite replaces a previous install
```

(`./run_bafu.sh` does both.) The project `reverse-bafu` then holds database `bafu-2026`
(11,947 processes), `ef-3.1-biosphere` (EF 3.1 flows, BAFU emissions relinked: 95.8 % of flows),
`bafu-2026-residual` (113 flows without EF counterpart) and the 25 methods
`("sentier", "EF v3.1", <category>)`. Every command below takes `--project <name>` if you chose
another name.

Smoke test:

```python
import bw2data as bd, bw2calc as bc
bd.projects.set_current("reverse-bafu")
act = bd.Database("bafu-2026").get("c4a92617-9f99-3d7b-95c0-15fb110b80ad")   # Electricity, low voltage, at grid | CH
lca = bc.LCA({act: 1}, ("sentier", "EF v3.1", "Climate change")); lca.lci(); lca.lcia()
print(lca.score)   # 0.0969623 kg CO2 eq per kWh
```

`sentier-brightway backtest --out output/backtest --xlsx <BAFU LCIA results>` compares every
process with BAFU's own openLCA results — the regression check once aggregated datasets get replaced.

## 3. Find the aggregated datasets and their sources

```bash
uv run python scripts/list_system_terminated.py --project reverse-bafu   # -> results/system_terminated.csv  (~15 s)
uv run python scripts/list_sources.py                                    # -> results/sources.csv, results/dois.csv
```

`system_terminated.csv`: the **101** datasets whose ecoSpold `dataSetInformation@type` is 2
("system terminated" = the cumulative LCI, no supplier links;
[schema](https://github.com/brightway-lca/pyecospold/blob/main/pyecospold/schemas/v1/EcoSpold01MetaInformation.xsd#L26-L60)),
joined with the Brightway database (inputs, flows, consumers), grouped by data-origin `family`,
with the unit-process `unit_sibling` where one exists and the people/representativeness fields
from the metadata. A 102nd flagged dataset has no exchanges and is skipped.
`sources.csv`: the 129 distinct source citations, with the report PDF for 112 of them when the
documentation bundle is present; `dois.csv`: the 36 DOIs embedded in dataset comments.

## 4. Rebuild an aggregated dataset from a spec

A spec is one JSON file per dataset holding the evidence-derived unit process — target, strategy,
evidence, inputs (with `free`/`bounds`/`sandbox`/nested `node` flags), direct emissions and
resources. Format: docstring of [src/reverse_bafu/spec.py](src/reverse_bafu/spec.py); examples:
[specs/](specs/).

```bash
uv run reverse-bafu run specs/d8ec4be3-burnt-shale.json      # resolve → calibrate (report only) → build → check
uv run reverse-bafu run specs/c3490cfc-cement-zn-d.json      # links the rebuilt burnt shale ("sandbox" input): run burnt shale first
uv run reverse-bafu run specs/gypsum-fibre-board-de.json
```

The four steps, also available individually (`resolve`, `calibrate`, `build`, `check`):

| Step | Does | Writes |
|---|---|---|
| resolve | maps every input name to a BAFU dataset: *unit* (link), *aggregated* (link, flag as dependency), *missing* (stop, suggest names); checks units | codes into the spec; exit 2 on anything missing |
| calibrate | bounded least squares for the inputs marked `free`, input list held fixed | prints spec vs fitted amounts; `--apply` writes them into the spec |
| build | the explicit node `<code>-disagg` and the hybrid `<code>-hybrid` (explicit + residual flows = original exactly) | Brightway database `reverse-bafu-sandbox`; the original is never touched |
| check | 25-category score diff, flow diff, residual share, structural checks | `results/checks/<code>.md` |

The committed specs already carry their calibrated amounts, so `run` reproduces
`results/checks/`; `calibrate --apply` re-derives the amounts (they change only if the code or the
category weighting changes). `uv run python scripts/render_pages.py` regenerates
`artifacts/rebuilt-inventories.html` from the specs, the sandbox and the check reports.

## 5. Draft a new spec reproducibly

```bash
uv run reverse-bafu evidence <code> --report "BAFU-2026 v1_Documentation/.../<report>.pdf" --pages 19-21   # PDF page numbers
uv run reverse-bafu draft <code>                 # API route: claude-opus-5, structured output (needs an Anthropic API key or `ant auth login`)
uv run reverse-bafu draft <code> --dry-run       # writes the exact prompts + JSON schemas for any other model
uv run reverse-bafu draft <code> --from-response extract=<json> --from-response map=<json> --from-response "by=<who>"
uv run reverse-bafu assemble <code>              # -> specs/<code>-<slug>.draft.json, then step 4
```

Or, inside Claude Code with a subscription: `/draft-spec <code> --report "<pdf>" --pages <a-b>`
runs the whole chain with the session as the model ([.claude/commands/draft-spec.md](.claude/commands/draft-spec.md)).

What is deterministic and hashed: the report text, the target metadata and direct-resource
candidates (`evidence`), the candidate lists for the mapping pass, and the assembly. What is
pinned: the two prompt templates ([prompts/](prompts/)), the schemas, the model. Every ingested
response is schema-validated. Everything — rendered prompts, candidates, raw responses,
provenance — lands in `specs/evidence/<code>/`, and every input of the assembled spec carries a
`derivation` (quoted line, raw value, factor with source, chosen candidate and why, author,
`reviewed_by`). A claude.ai subscription is not an API key: the SDK route needs a key from
console.anthropic.com; the Claude Code route needs only the subscription.

## 6. Benchmark on synthetic aggregated datasets

```bash
uv run reverse-bafu benchmark --n 40 --seed 7 --scenarios oracle,bounded,partial,distractors   # ~12 min -> results/benchmark/n40-seed7.{csv,md}
uv run reverse-bafu benchmark --n 5 --seed 7 --scenarios blind --name blind-n5-seed7           # the no-list control, slow
```

BAFU unit processes are turned into system-terminated lookalikes (their cumulative inventory) and
the calibration is scored against the real inputs under five evidence packages. Results and
interpretation: `results/benchmark/n40-seed7.md` and the method explainer, §7.

## Layout

```
src/reverse_bafu/   pipeline: cli, spec, db, lci, resolve, calibrate, build, check, benchmark, draft
scripts/            list_system_terminated.py, list_sources.py, render_pages.py (+ templates/)
prompts/            the two fixed LLM prompt templates
specs/              one JSON per rebuilt dataset; specs/evidence/<code>/ = drafting records
results/            system_terminated.csv, sources.csv, dois.csv, checks/, benchmark/
artifacts/          the documentation: method-explainer, the-101, rebuilt-inventories, burnt-shale-rebuilt, code-walkthrough
.claude/commands/   /draft-spec
```

## Data licence and citation

Both BAFU files stay out of the repository (`.gitignore`: `*.zip`, `data/`,
`BAFU-2026 v1_Documentation/`). Citation required for anything derived from the installed data:

> Source: Life Cycle Inventory database of the Swiss Federal Administration, BAFU:2026.
