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
(`results/drafting_status.csv` records where each of the 101 stands); step 5 rebuilds every spec
(`results/rebuild_status.csv`, `results/checks/`); step 6 benchmarks the calibration step.

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
another name. The methods are installed by the import and are handy for a smoke test, but the
pipeline itself never uses them: every rebuild is judged against the original's elementary flows
directly, so no characterisation method and no weighting between impact categories enters the
result.

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

### The 37 the flag misses

```bash
PYTHONPATH=$PWD/src python scripts/find_system_processes.py --project reverse-bafu   # -> results/system_terminated_extended.csv
```

The `type=2` flag is reliable but not complete. BAFU-2026 also carries the APME / PlasticsEurope
era eco-profiles, which were never marked. They are found by structure instead — a dataset with no
production input at all (its only technosphere exchanges are waste-treatment services) but a real
elementary-flow vector — and there are **37**: benzene, toluene, styrene, propylene, butadiene,
butene, pentane, acetone, hydrogen cyanide, the chloromethanes, epoxy resin, the nylons, ABS, SAN,
GPPS, HIPS, polycarbonate, the PMMAs, polybutadiene, PVDC, polyols, MDI, TDI, methyl methacrylate,
acetone cyanohydrin, naphtha APME mix and the ethylene/propylene pipeline-system datasets.

All 37 confirm it in their own metadata, which the structural test never reads: *"Aggregated data
for all processes from raw material extraction until delivery at plant"*, or *"The data source for
this process is a system inventory from Boustead. Due to the cumulated form of this data only the
ressources and emissions included in the data source were considered."*

They matter because they are not at the edge of the database: **466 BAFU-2026 datasets consume at
least one of the 37** (936 consume one of the 101). `Ethyl benzene, at plant` consumes `Benzene, at
plant`; `Cumene, at plant` consumes benzene and propylene; `Glass fibre, at plant` consumes
`Nylon 6, at plant`. Ordinary unit processes terminate on them, which is exactly what the flag-based
survey could not see (`scripts/ecoprofile_consumers.py`). 22 of the 37 are rebuilt — 51 of the 138
aggregated datasets we found (a lower bound: a partly aggregated dataset passes both tests unseen).

`results/system_terminated_extended.csv` has the same schema as `system_terminated.csv` plus
`detected_by` (flag | structure) and `n_flows`. `db.aggregated_codes_all()` is the union of the two
and is what `resolve` and `check` use, so a rebuild terminating on one of these is now reported as
the dependency it is; `db.aggregated_codes()` stays flag-based because `benchmark.py` uses it to
choose synthetic test cases and widening it would move every published benchmark number.

Step 4 works through them with `--datasets results/system_terminated_extended.csv`;
`results/drafting_status_extended.csv` records where each one stands, and
`scripts/ecoprofile_agreement.py` reports their agreement against the flows the eco-profile itself
declares, which is the only denominator that means anything for them (see
[exports/README.md](exports/README.md), *The APME eco-profiles the ecoSpold type=2 flag missed*).

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

## 5. Rebuild the datasets from the specs

```bash
uv run reverse-bafu run-all             # every specs/*.json: resolve → calibrate (report only) → build → check
uv run reverse-bafu run-all --apply     # same, and calibrate writes the fitted amounts into the specs
uv run python scripts/render_pages.py   # regenerate artifacts/rebuilt-inventories.html from specs, sandbox and reports
```

`run-all` orders the specs so that one linking a rebuilt node (an input with `"sandbox"`, e.g.
cement → burnt shale) runs after the spec that builds it, and writes `results/rebuild_status.csv`:
per spec the status (`rebuilt` / `unresolved` / `error`) and the flow‑by‑flow agreement with the
original: how many of the 50 largest kilogram flows are within ±10 %, how much of the total
kilogram mass is, how many of *all* flows are, the median deviation and the report path. A spec whose inputs do
not all resolve is skipped with `unresolved` and does not stop the batch. The committed specs
already carry their calibrated amounts, so `run-all` without `--apply` reproduces `results/checks/`;
with `--apply` the amounts are re‑derived (they change only if the code changes). The nodes land in the Brightway database `reverse-bafu-sandbox`; the original datasets
are never touched.

The four steps, per spec (`uv run reverse-bafu run|resolve|calibrate|build|check specs/<spec>.json`
for one dataset):

| Step | Does | Writes |
|---|---|---|
| resolve | maps every input name to a BAFU dataset: *unit* (link), *aggregated* (link, flag as dependency), *missing* (stop, suggest names); checks units | codes into the spec; exit 2 on anything missing |
| calibrate | bounded least squares for the inputs marked `free`, input list held fixed; one equation per elementary flow, weighted by 1/max(\|target\|, \|model\|) — relative error — and by 1/√(flows in the group), so every (unit, compartment) group contributes its mean squared relative error and counts equally; round-off flows get weight 0; solved with an active-set solver (NNLS/BVLS) on the column-scaled system, run twice so the result does not depend on the spec's starting amounts | prints spec vs fitted amounts; `--apply` writes them into the spec |
| build | the explicit node `<code>-disagg` and the hybrid `<code>-hybrid` (explicit + residual flows = original exactly) | `reverse-bafu-sandbox` |
| check | flow‑by‑flow agreement: deviation buckets, the largest flows per unit, the worst deviations, kilogram mass covered, structural checks | `results/checks/<code>.md` |

## 6. Benchmark: how well does the calibration recover a unit process?

```bash
uv run reverse-bafu benchmark --project bafu-2026-bench --n 100 --seed 7 --scenarios oracle,bounded,partial,distractors --name flow-n100-seed7
uv run reverse-bafu benchmark --project bafu-2026-bench --n 25 --seed 7 --scenarios blind --name blind-n25-seed7   # the no-list control
```

**Two modes.** `--mode calibration` (the default, below) tests one step: step 5's `calibrate`, the
least‑squares recovery of input *amounts* from an aggregated flow vector given an input *list*;
its ground truth is free, so it runs without any model. `--mode extraction` (end of this section)
tests the whole route from the PDF to the checked node, on unit processes whose report is in the
bundle; it needs the model for three prompts per case.

**How it works, step by step.**

1. *Test set.* BAFU unit processes with 3–30 technosphere inputs, not among the 101, name not
   starting with `xx`; grouped by BAFU top‑level category, each group sorted by code and shuffled
   with the seed, then drawn round‑robin over the categories until `--n` — so 40 cases span 40
   categories (transport, chemicals, agriculture, …). Their real inputs and amounts are the answer key.
2. *Synthetic aggregated dataset.* For each case the cumulative inventory `B·A⁻¹·e` is computed —
   exactly what an ecoSpold `type=2` export of that process would contain — and becomes the
   target vector. The process's own direct emissions are known too (given in every scenario but
   `blind`).
3. *Evidence packages.* The same fit is run five times per case with different candidate lists and
   bounds, mimicking evidence of decreasing quality:

   | Scenario | Candidate inputs | Bounds | Stands for |
   |---|---|---|---|
   | `oracle` | exactly the true inputs, amounts unknown | 0…∞ | a complete, correct table |
   | `bounded` | the true inputs | 0.5×–2× the true amount | a table with ranges |
   | `partial` | the true inputs minus the 30 % that explain the fewest flows | 0…∞ | a report that omits minor lines |
   | `distractors` | the true inputs plus 10 random processes used ≥ 30 times in BAFU | 0…∞ | an over‑proposed list (an LLM guessing inputs) |
   | `blind` | every process used ≥ 30 times (~675), no direct flows | 0…∞ | no evidence at all (field‑agnostic fitting) |

4. *Fit.* Exactly the pipeline's calibration: one row per elementary flow, weighted by
   1/max(|target|, |model|) so a kilogram of CO₂ and a microgram of a trace metal weigh the same,
   and by 1/√(flows in the group), so every (unit, compartment) group — land use, water,
   radioactivity, each emission compartment — contributes its mean squared relative error and
   counts equally; the ~1,200 flows of "kilogram/emissions" do not outvote the rest. Round-off flows
   (`lci.determined_flows`) get weight 0. The weights are computed against a first unweighted fit,
   then once more against the weighted one. No impact assessment enters. Columns and right-hand side
   scaled to unit norm; NNLS when unbounded, BVLS when bounded (`lci.solve_weighted`).
5. *Metrics per case and scenario* (`results/benchmark/<name>.csv`): inventory agreement — the
   share of the target's flows the fit reproduces within ±10 %, the median deviation, flows missing
   and flows added; amount recovery — the share of *material* inputs (those supplying ≥ 1 % of some
   flow of the target) fitted within ±20 %; structure — false positives (candidates given a material
   amount that are not true inputs), false negatives (material true inputs dropped); runtime.
   `<name>.md` holds the medians per scenario.

**What the latest run says** (`results/benchmark/flow-n100-seed7.md`, 100 cases;
`blind-n25-seed7.md`, 25 cases). Flows: median share of a case's determined flows within ±10 %.
Amounts: material inputs within ±20 % of the true amount, pooled over all cases.

| Scenario | Flows within ±10 % | Amounts within ±20 % | Wrong inputs used (median) |
|---|---|---|---|
| `oracle` | 100 % | 787 / 803 | 0 |
| `bounded` | 100 % | 795 / 803 | 0 |
| `partial` | 99 % | 539 / 605 | 0 (2 material inputs lost) |
| `distractors` | 100 % | 785 / 803 | 0 |
| `blind` | 98 % | 56 / 122 | 86 |

With the right inputs on the list the fit recovers the amounts; the misses are mostly pairs of
inputs whose cumulative inventories are (near-)identical, e.g. inert waste and gravel to the same
landfill, where any split gives the same flows. Ten wrong candidates are set to zero — an optimistic
result, since a synthetic target is reproduced exactly by its true inputs and a wrong one has
nothing left to absorb; real originals were computed on older background data. With no list the fit
reproduces 98 % of the flows with a made-up process of ~86 wrong inputs: **the identifiability
trap, a near-perfect inventory fit with the wrong structure.**

Earlier runs (before 2026-09-23) read much worse — 614/803 for `oracle`, 63 % of flows for
`distractors`, 6 % for `blind` — because of two faults in the fit, not the method: `lsq_linear`'s
trust-region solver stopped early on the badly scaled system, and the group normalisation (dividing
by the group's sum of weights) weighted each group by its smallest flow, so "kilogram/emissions"
counted 1e-58 of one land-use flow and the fit saw ~20 of ~1,670 flows.

### Extraction mode: the whole route, including the PDF

```bash
uv run reverse-bafu benchmark --mode extraction --n 10 --seed 7            # API route (needs the anthropic SDK and a key)
uv run reverse-bafu benchmark --mode extraction --n 10 --seed 7 --dry-run  # writes the pending prompts; rerun after answering them
```

or `/benchmark-extraction --n 10 --seed 7` inside Claude Code, which answers the prompts itself
([.claude/commands/benchmark-extraction.md](.claude/commands/benchmark-extraction.md)).

This mode tests everything step 4 and step 5 do, on cases with a known answer. The cases are BAFU
*unit processes* whose cited report is in the documentation bundle (same stratified, seeded
sampling as above, skipping processes without a report). Each is treated exactly like a real
aggregated dataset: locate the table in the PDF → evidence → extract → map → assemble → resolve
→ calibrate (`--apply`) → build → check, with the same three model routes and the same on‑disk
state machine as `draft-all` (files under `results/benchmark/extraction/`, never under `specs/`).
The drafted spec is then compared with the process's real exchanges:

| Metric | Meaning |
|---|---|
| `pages` / `pages-not-found` | did the locate pass find the table |
| `inputs_matched` / `inputs_missed` / `inputs_extra` | true inputs recovered *and mapped to the right dataset* (by code); true inputs absent; drafted inputs that are not in the process |
| `input_amounts_within_20pct` | of the matched inputs, how many amounts (after calibration) are within ±20 % of the real ones |
| `direct_flows_matched` | direct emissions/resources recovered (by substance and compartment) |
| `top_flows_within_10pct`, `kg_mass_covered_pct`, `flows_within_10pct` | the harness's verdict on the rebuilt node vs the real process: the 50 largest kilogram flows, the share of kilogram mass, all flows |
| `gaps_reported` | what the model said the excerpt did not cover |

Model calls per case: three (locate, extract, map). The one case run so far, `CEM II, B‑LL
cement` from the concrete 2020 report (answered by a Claude Code session, labelled so): 9/9 inputs
found and mapped, 8/9 amounts within ±20 %, the direct flow matched. The one amount miss is a finding about the data, not the pipeline: the
report prints 2.0E‑2 tkm of lorry transport for that cement, the BAFU dataset carries 4.3E‑4.

## 7. Share the rebuilds: export and import

The rebuilt unit processes live in the Brightway sandbox of whoever ran `run-all`. To let someone
else enrich *their* BAFU-2026 project with them:

```bash
PYTHONPATH=src python scripts/export_disaggregated.py --project bafu-2026   # -> exports/
python scripts/import_disaggregated.py --project <their-project> --dry-run  # resolve, write nothing
python scripts/import_disaggregated.py --project <their-project>            # add one new database
PYTHONPATH=src python scripts/verify_import_roundtrip.py --source bafu-2026 --scratch import-test
```

The export is a plain documented JSON (plus a flat CSV of the explicit exchanges): per dataset the
name, location, unit, reference product, the BAFU code it replaces, the strategy, every
technosphere exchange with its supplier's BAFU code, every elementary flow with its EF 3.1 code and
database, the residual block, and the provenance (report, page, quoted line) where the pipeline
recorded it. The importer links by code, creates one new database and **refuses to write anything**
if a referenced code is missing in the target project, naming every one.

Format, flags, what the strategies mean and — importantly — the per-dataset quality limits are in
[exports/README.md](exports/README.md). The short version: import the `*-hybrid` nodes if you need
results that match BAFU-2026 (they reproduce the originals to 1e-8), the `*-disagg` nodes only if
you want the evidence-only model, which reproduces between 0 % and 90 % of a dataset's flows. The
spread is wide, the high end is not what it looks like and the low end is often not either — both
traps are documented in [exports/README.md](exports/README.md), under *The PlasticsEurope family*
and *The APME eco-profiles the ecoSpold type=2 flag missed*. The sharpest single illustration is in
the second one: substituting BAFU's own disaggregated epoxy resin for BAFU's own aggregated epoxy
resin, with no modelling at all, gets fossil CO₂ to +1.5 % and 75 % of the kilogram mass — and
scores 0 % on "flows within ±10 %".

## Layout

```
src/reverse_bafu/   pipeline: cli, spec, db, lci, resolve, calibrate, build, check, runall, draft, benchmark
scripts/            list_system_terminated.py, find_system_processes.py, list_sources.py,
                    render_pages.py (+ templates/), ecoprofile_agreement.py, ecoprofile_consumers.py,
                    transcription_vs_truth.py,
                    export_disaggregated.py, import_disaggregated.py, verify_import_roundtrip.py
prompts/            the three fixed LLM prompt templates (locate, extract, map)
specs/              one JSON per rebuilt dataset; specs/evidence/<code>/ = drafting records
results/            system_terminated.csv, sources.csv, dois.csv, drafting_status.csv, rebuild_status.csv, checks/, benchmark/
exports/            the shareable export of the rebuilt datasets + its README (format, import, quality limits)
artifacts/          the documentation: method-explainer, the-101, rebuilt-inventories, burnt-shale-rebuilt, code-walkthrough
references.txt      the two papers referenced, with their role for this project
.claude/commands/   /draft-all, /draft-spec, /benchmark-extraction
```

## Data licence and citation

Both BAFU files stay out of the repository (`.gitignore`: `*.zip`, `data/`,
`BAFU-2026 v1_Documentation/`). Citation required for anything derived from the installed data:

> Source: Life Cycle Inventory database of the Swiss Federal Administration, BAFU:2026.
