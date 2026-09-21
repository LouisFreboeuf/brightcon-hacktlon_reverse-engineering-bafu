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
**102** such datasets ([results/system_terminated.csv](results/system_terminated.csv)); 88 have
no technosphere inputs at all, the 14 PlasticsEurope polymers keep a few disposal inputs.
Sorted by consumers: HDPE granulate (533), PP (173), LDPE (122), ethylene glycol (76), ethylene (72).

## Data

`BAFU-2026 v1_ecoSpold v1.zip` (11,948 ecoSpold v1 XML files, one `process_<uuid>.xml` per dataset)
is the original export from BAFU. It is gitignored (`*.zip`, `data/`) and is **not** needed for the
import above — keep it around as the reference for the reverse-engineering work. Unzip it into
`data/` if you want to read the raw XML.

Citation required for anything derived from the installed data:

> Source: Life Cycle Inventory database of the Swiss Federal Administration, BAFU:2026.
