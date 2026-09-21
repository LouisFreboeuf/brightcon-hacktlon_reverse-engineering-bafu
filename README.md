# brightcon-hackathon: reverse-engineering BAFU

Brightcon 2026 hackathon project for [brightcon-2026-material#38](https://github.com/Depart-de-Sentier/brightcon-2026-material/issues/38):
replace aggregated BAFU-2026 datasets with unit process data and check that the results stay the same.

The BAFU-2026 v1 inventory is installed into Brightway 2.5 with
[sentier-dev/sentier-brightway](https://github.com/sentier-dev/sentier-brightway). It fetches the
BAFU processes, the EF 3.1 biosphere, the 25 EF 3.1 methods and the BAFU→EF 3.1 flow mappings from
pinned commits of the Sentier data repos (`sentier-inventory`, `sentier-vocab`, `sentier-methods`,
`sentier-mappings`) — nothing needs to be parsed from the ecoSpold zip.

## Setup

Needs [uv](https://docs.astral.sh/uv/). Python 3.12 is picked up automatically (`.python-version`).

```bash
uv sync
```

This installs `sentier-brightway` from its GitHub `main` (pinned to a commit in `uv.lock`),
`bw2data` 4.x and `bw2calc` 2.x into `.venv/`.

## Import into Brightway 2.5

```bash
# 1. sanity check: how many BAFU flows link to EF 3.1 (downloads ~40 MB of parquet on first run,
#    cached in ~/.cache/sentier-brightway/, no Brightway project touched)
uv run sentier-brightway coverage

# 2. write the databases + methods into the Brightway project "reverse-bafu" (~3-4 min)
uv run sentier-brightway db --project reverse-bafu
```

`run_bafu.sh` runs both.

Afterwards the project `reverse-bafu` contains:

| Object | Content |
|---|---|
| database `bafu-2026` | 11,947 BAFU-2026 v1 processes |
| database `ef-3.1-biosphere` | EF 3.1 elementary flows, BAFU emissions relinked onto them (95.8 % of flows, 96.8 % of exchanges) |
| database `bafu-2026-residual` | the 113 BAFU flows with no EF 3.1 counterpart (kept, no characterization factor) |
| methods `("sentier", "EF v3.1", <category>)` | 25 EF 3.1 impact categories |

Re-run with `--overwrite` to replace a previous install. In Activity Browser, open the `reverse-bafu`
project; the methods sit under `sentier` › `EF v3.1`.

Quick check that everything works:

```python
import bw2data as bd, bw2calc as bc

bd.projects.set_current("reverse-bafu")
act = bd.Database("bafu-2026").get("c4a92617-9f99-3d7b-95c0-15fb110b80ad")  # Electricity, low voltage, at grid | CH
lca = bc.LCA({act: 1}, ("sentier", "EF v3.1", "Climate change"))
lca.lci(); lca.lcia()
print(lca.score)  # 0.0969623 kg CO2 eq per kWh
```

### Other sentier-brightway commands

| Command | What it does |
|---|---|
| `uv run sentier-brightway files --out output/files` | Same build as plain files (parquet registry + `bw_processing` datapackages), no bw2data project needed. |
| `uv run sentier-brightway backtest --out output/backtest --xlsx <BAFU LCIA results .xlsx/.zip>` | Scores every process in all 25 categories, compares with BAFU's published openLCA results, writes a dashboard. Add `uv sync --extra fast` first for the pypardiso solver. |
| `uv run sentier-brightway <cmd> --data-root ~/dds` | Read the four Sentier data repos from local clones under `~/dds` instead of downloading (also `$SENTIER_DATA_ROOT`). |

The backtest is our regression check for the hackathon: after swapping an aggregated dataset for
unit processes, the scores of everything downstream should stay within tolerance.

## Aggregated datasets: the ecoSpold "system terminated" list

```bash
uv run python scripts/list_system_terminated.py      # ~15 s, writes results/system_terminated.csv
```

In the EcoSpold01 schema every dataset carries `dataSetInformation@type`: 1 = unit process
(direct flows + links to suppliers), 2 = *system terminated* — the cumulative elementary flows
of the whole upstream chain, i.e. an LCI result
([schema documentation](https://github.com/brightway-lca/pyecospold/blob/main/pyecospold/schemas/v1/EcoSpold01MetaInformation.xsd#L26-L60)).
The type-2 datasets are the explicitly aggregated ones to rebuild as unit processes.

The flag is read from the unzipped XML in `data/` (the Sentier import drops it); the file-name
UUID is the Brightway activity code, so each row is joined with the installed database for the
number of technosphere inputs, elementary flows and consuming processes. BAFU-2026 v1 has
**101** such datasets ([results/system_terminated.csv](results/system_terminated.csv)); 87 have
no technosphere inputs at all, the 14 PlasticsEurope polymers keep a few disposal inputs. (A
102nd flagged dataset, `Disposal, rectangular straw bale`, has no exchanges and is skipped.)
Sorted by consumers: HDPE granulate (533), PP (173), LDPE (122), ethylene glycol (76), ethylene (72).
The `family` column groups them by data origin (PlasticsEurope eco-profiles, confidential
ecoinvent-v2 industry data, treeze/KBOB reports, French bio-based FDES studies, manufacturer KBOB
datasets); `unit_sibling` names a unit process of the same product already in BAFU.
[docs/disaggregation_strategies.md](docs/disaggregation_strategies.md) discusses what is behind
each family and how it could be disaggregated.

## Disaggregation pipeline (`reverse-bafu`)

One aggregated dataset at a time, driven by a JSON *spec* holding the evidence-derived unit process
(see [specs/d8ec4be3-burnt-shale.json](specs/d8ec4be3-burnt-shale.json) and the docstring in
[src/reverse_bafu/spec.py](src/reverse_bafu/spec.py)):

```bash
uv run reverse-bafu resolve   specs/<spec>.json   # map every input to a BAFU unit process; flag missing / aggregated ones
uv run reverse-bafu calibrate specs/<spec>.json   # NNLS amounts for inputs marked "free", list held fixed (--apply writes back)
uv run reverse-bafu build     specs/<spec>.json   # write <code>-disagg and <code>-hybrid into the sandbox database
uv run reverse-bafu check     specs/<spec>.json   # harness: score diff, flow diff, residual share, structural checks
uv run reverse-bafu run       specs/<spec>.json   # all four
```

`--project` defaults to `reverse-bafu`. Nodes land in the Brightway database `reverse-bafu-sandbox`
(depends on `bafu-2026` and the two biosphere databases); the original dataset is never touched.
`<code>-disagg` is the explicit model, `<code>-hybrid` adds a residual block of elementary flows so
its cumulative inventory equals the original exactly (the S5 representation). Check reports go to
`results/checks/<code>.md`.

Why the harness has a structural section: with a free input list, NNLS reproduces all 25 EF scores
to 1.000 while choosing 116 wrong inputs (see the strategy doc §4); score agreement is necessary,
not sufficient. Inputs may carry a nested `"node"` for intermediate processes BAFU lacks; they are
built first and linked ("terminate on the database").

Pilot — `Burnt shale, at plant` from the concrete 2020 report, Tab. 3.9: 12 inputs, all resolved
to existing unit processes; direct CO₂ alone reproduces the climate score; the table's gross grid
electricity (68.6 kWh/t) overshoots ionising radiation by +614 % and the fit puts it at 2.5 kWh/t —
the plant co-generates 183.8 kWh/t, so the original nets its own generation. With that one amount
calibrated: climate, acidification, particulates, photochemical ozone and fossil resources within
±7 %; the toxicity / land / water categories still miss flows the table does not list (metals from
burning, water) — that is what the flow diff in the report is for.

### Benchmark with known answers

```bash
uv run reverse-bafu benchmark --n 40 --seed 7          # ~12 min; results/benchmark/n40-seed7.{csv,md}
uv run reverse-bafu benchmark --n 5 --scenarios blind  # the field-agnostic control, slow
```

Turns BAFU unit processes into synthetic system-terminated datasets (their cumulative inventory)
and scores the calibration against the real inputs under five evidence packages — correct list,
list with ranges, list with 30 % missing, list with 10 distractors, no list. Latest run: correct
list → 37/40 cases match all 25 categories, 92 % of material amounts within ±20 %; with distractors
4/40 cases choose a wrong input while scores still match. Details in
[docs/disaggregation_strategies.md](docs/disaggregation_strategies.md) §4.

## Sources and reports

```bash
uv run python scripts/list_sources.py     # writes results/sources.csv and results/dois.csv
```

Every dataset cites one source in its ecoSpold metadata (author, year, title, publisher, full
citation); [results/sources.csv](results/sources.csv) lists the 125 distinct ones with how many
datasets (and how many aggregated ones) cite each, and [results/dois.csv](results/dois.csv) the 36
DOIs embedded in dataset comments. If the official `BAFU-2026 v1_Documentation` bundle is unzipped
next to the repo (gitignored), the `pdf` column links each source to its report PDF — 108 of 125
sources, 11,541 of 11,947 datasets.

## Data

`BAFU-2026 v1_ecoSpold v1.zip` (11,948 ecoSpold v1 XML files, one `process_<uuid>.xml` per dataset)
is the original export from BAFU. It is gitignored (`*.zip`, `data/`) and is **not** needed for the
import above — keep it around as the reference for the reverse-engineering work. Unzip it into
`data/` if you want to read the raw XML.

Citation required for anything derived from the installed data:

> Source: Life Cycle Inventory database of the Swiss Federal Administration, BAFU:2026.
