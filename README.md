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

Steps 1–3 reproduce `results/system_terminated.csv`, `sources.csv` and `dois.csv`; step 4 makes the specs
(`results/drafting_status.csv` records where each of the 101 stands); step 5 reproduces `results/checks/`
from the committed specs; step 6 is the benchmark.

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
| **BAFU:2026 Version 1 - ecoSpold1** | `BAFU-2026 v1_ecoSpold v1.zip` (11,948 `process_<uuid>.xml`) | `data/ecospold/` — the zip's inner folder is `ecoSpold files/`, rename it | steps 3 and 4 (the ecoSpold metadata, incl. the `type=2` flag the Brightway import drops) |
| **BAFU:2026 Version 1 - Documentation** | `BAFU-2026 v1_Documentation.zip` (114 LCI report PDFs) | `BAFU-2026 v1_Documentation/` next to this README, keeping the inner `BAFU-2026 v1_Documentation/BAFU-2026 v1 LCI Reports/` layout | step 3 (`pdf` column) and step 4 (`--report`) |

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

## 4. Make the specs

A spec is one JSON file per dataset holding the evidence-derived unit process — target, strategy,
evidence, inputs (with `free`/`bounds`/`sandbox`/nested `node` flags), direct emissions and
resources. Format: docstring of [src/reverse_bafu/spec.py](src/reverse_bafu/spec.py); examples in
[specs/](specs/). One entry point makes them for every row of `results/system_terminated.csv`:

```bash
uv run reverse-bafu draft-all                     # API route (uv sync --extra llm + an Anthropic API key or `ant auth login`)
uv run reverse-bafu draft-all --dry-run           # no model: writes the pending prompts, records where each dataset stands
```

or, inside Claude Code with a subscription, `/draft-all` — the session answers the prompts itself
and loops until nothing is pending ([.claude/commands/draft-all.md](.claude/commands/draft-all.md)).
`--only <codes>` restricts the run. Nothing else is typed by hand: the report comes from the `pdf`
column of `results/sources.csv`, the pages are located by the pipeline. The result is
`results/drafting_status.csv` — one row per dataset with `status` = `drafted` (spec written),
`pages-not-found` (the report has no inventory table for it, with the reason), `no-pdf` (no report
in the bundle: the French, manufacturer and PlasticsEurope families) or `error` — and one
`specs/<code>-<slug>.draft.json` per drafted dataset. Reruns are incremental: every response
already on disk is reused, so a batch can be continued after an interruption or a fix.

### How a spec is extracted, step by step

For each dataset the batch runs four stages; every stage leaves its files under
`specs/evidence/<code>/`, so each number in the spec can be traced back to a quoted line.

1. **Locate** (one model prompt). Every table and figure caption of the report PDF is extracted
   with its PDF page number — deterministic, cached in `.cache/pdftext/` — and listed in
   `prompt-0-locate.md` ([prompts/locate_pages.md](prompts/locate_pages.md)) together with the
   dataset's name, category and metadata. The model names the caption(s) holding the dataset's
   inventory table and returns the PDF page range (at most four pages), or `found: false` with the
   reason (e.g. the production data sit in a confidential annex). Reports may be in German or French;
   the dataset names are English, so this match is by meaning — which is why it is a model step and
   not a text search.
2. **Evidence** (deterministic). `pdftotext -layout` of those pages → `report-p<a>-<b>.txt`; the
   dataset's ecoSpold metadata (name, unit, location, category, `includedProcesses`, `technology`,
   comment, source, period) and the resource flows of its aggregated vector, largest first — the
   candidates for the process's own direct resources — → `target.json`; SHA‑256 of the PDF, the text
   and the XML plus the pdftotext version → `manifest.json`.
3. **Extract** (one model prompt). `prompt-1-extract.md` ([prompts/draft_spec.md](prompts/draft_spec.md))
   holds the metadata, the resource candidates and the excerpt. The model returns one line item per
   table row: a verbatim `quote`, `raw_value` and `raw_unit` as printed, the table's basis (`per`),
   an optional conversion `factor` with `factor_source` (e.g. litres of diesel → MJ), `kind` (input /
   emission / resource / co‑product / ignore), a `search` phrase for the supplying dataset or flow,
   and a `confidence`; plus `basis_amount` (how many target units one table row refers to),
   `allocation`, `mass_sum` (when the excerpt says the composition adds up to a mass) and `gaps` —
   what the excerpt does not cover. The rules forbid the two things that need judgement: inventing
   inputs the excerpt does not mention (they go into `gaps`) and converting beyond a stated factor.
   A range in the table (`raw_min`/`raw_max`) becomes a `free` input with `bounds`.
4. **Map** (deterministic candidates, one model prompt). For each line item a keyword search over
   the 11,947 dataset names (inputs) or the EF 3.1 flow list (emissions, resources) — words matched
   at word starts, ranked by matches, then the target's location / RER / CH / DE / GLO, then name
   length — writes `candidates-2-map.json`. `prompt-2-map.md` ([prompts/map_inputs.md](prompts/map_inputs.md))
   asks the model to pick, per item, one candidate or none, with location, compartment, whether the
   candidate is itself an aggregated dataset, and a one‑sentence reason.
5. **Assemble** (deterministic). `amount = raw_value × factor / basis_amount`, unit names normalised;
   inputs take the chosen dataset, emissions and resources the chosen flow; an aggregated dependency
   is linked to its rebuilt sandbox node when one exists (cement → the rebuilt burnt shale);
   co‑products and ignored rows go to `provenance.skipped_items`, the model's gaps to
   `provenance.gaps_reported_by_model`. Every entry carries a `derivation` — quote, raw value,
   factor with source, search phrase, mapping reason, author, `reviewed_by: null` — and the spec
   carries a `provenance` block with model, prompt hashes and authors for all three model passes.
   The file gets `"variant": "draft"` so its sandbox nodes never collide with a hand‑written rebuild.

Model routes and what they record: the API route (`claude-opus-5`, structured output against the
saved JSON schemas) stores model id, message id, token usage and prompt hash; the Claude Code route
records `by=claude-code:<model>`; any other model or a person can answer the prompt files written by
`--dry-run` and continue with `draft-all` (responses are validated against the same schemas on
ingest). A claude.ai subscription is not an API key. Reproducible means: locate‑captions, evidence,
candidates and assembly regenerate bit‑for‑bit, the prompts and the model are pinned, every number
is auditable — not that the model returns identical JSON.

The per‑dataset commands behind the batch — `reverse-bafu locate|evidence|draft|assemble <code>` —
exist for debugging one dataset; `reverse-bafu draft <code> --dry-run` / `--from-response …` and
`/draft-spec <code> --report … --pages …` are their manual forms.

How the committed specs were made: `specs/*.draft.json` (burnt shale, cement ZN/D) are outputs of
this route, the three model prompts answered by a Claude Code session and labelled so in their
provenance; the drafted cement converges on the same calibrated composition as the hand‑written
spec. `d8ec4be3-burnt-shale.json`, `c3490cfc-cement-zn-d.json` and `gypsum-fibre-board-de.json`
were written by hand in a chat session before the route existed; their `evidence` and `note`
fields record the sources, but they have no per‑input `derivation`. For the gypsum board the
batch correctly stops at `pages-not-found`: the report keeps the board's production inventory in a
confidential annex, so that dataset needs the S2 template route, for which there is no command yet.

## 5. Rebuild the dataset from the spec

```bash
uv run reverse-bafu run specs/d8ec4be3-burnt-shale.json      # resolve → calibrate (report only) → build → check
uv run reverse-bafu run specs/c3490cfc-cement-zn-d.json      # links the rebuilt burnt shale ("sandbox" input): run burnt shale first
uv run reverse-bafu run specs/gypsum-fibre-board-de.json
uv run reverse-bafu run specs/c3490cfc-cement-zn-d-at-plant.draft.json   # the drafted variant; sandbox nodes <code>-draft-…
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
prompts/            the three fixed LLM prompt templates (locate, extract, map)
specs/              one JSON per rebuilt dataset; specs/evidence/<code>/ = drafting records
results/            system_terminated.csv, sources.csv, dois.csv, drafting_status.csv, checks/, benchmark/
artifacts/          the documentation: method-explainer, the-101, rebuilt-inventories, burnt-shale-rebuilt, code-walkthrough
references.txt      the two papers referenced, with their role for this project
.claude/commands/   /draft-all, /draft-spec
```

## Data licence and citation

Both BAFU files stay out of the repository (`.gitignore`: `*.zip`, `data/`,
`BAFU-2026 v1_Documentation/`). Citation required for anything derived from the installed data:

> Source: Life Cycle Inventory database of the Swiss Federal Administration, BAFU:2026.
