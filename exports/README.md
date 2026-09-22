# Disaggregated BAFU-2026 datasets — export and import

This folder holds a machine-readable export of the unit processes the `reverse-bafu` project
rebuilt for BAFU-2026's **aggregated ("system terminated") datasets** — the 101 datasets that ship
with no technosphere inputs, only a cumulative vector of elementary flows on the product.

The point of the export is that you can enrich **your own** Brightway project with them: the
rebuilt processes are added as a new database whose exchanges link, by code, to the BAFU-2026 and
EF 3.1 biosphere databases you already have.

> **Read [Known quality limits](#known-quality-limits) before using any of this in a study.**
> Several of these rebuilds reproduce only a few per cent of the original dataset's flows.

---

## Files

| file | what it is |
|---|---|
| `disaggregated_bafu2026.json` | the export. Plain, documented JSON — one object per rebuilt dataset, with every exchange, its supplier's BAFU code, every elementary flow with its EF 3.1 code **and** database, the residual block, and the provenance (report, page, quoted line) wherever the pipeline recorded it. |
| `disaggregated_bafu2026_exchanges.csv` | the **explicit** exchanges flattened to one row each, for reading in a spreadsheet. It is a *view*; the JSON is the source of truth (the CSV drops the derivation detail, the gaps, the evidence list and the ~31,000 residual rows, which would bury the 332 explicit ones). |
| `README.md` | this file. |

Both files are generated — never hand-edited — by:

```bash
PYTHONPATH=src python scripts/export_disaggregated.py --project bafu-2026
```

which reads `results/rebuild_status.csv`, the specs under `specs/`, and the Brightway sandbox
`reverse-bafu-sandbox` that `reverse-bafu run-all` built.

---

## Importing into your project

```bash
python scripts/import_disaggregated.py --project <your-project>
```

That creates one new database, `bafu-2026-disaggregated`, and touches nothing else. Your
aggregated BAFU datasets stay exactly as they are; the new unit processes link *to* them for their
supply chain.

Useful flags:

| flag | |
|---|---|
| `--dry-run` | resolve every reference and report, write nothing. Run this first. |
| `--database NAME` | name of the new database (default `bafu-2026-disaggregated`) |
| `--bafu-db NAME` | your BAFU-2026 database, if it is not called `bafu-2026` |
| `--biosphere NAME` | biosphere database to resolve flows in; repeat for several (default `ef-3.1-biosphere` and `bafu-2026-residual`) |
| `--include explicit\|hybrid\|both` | which nodes to import — see below (default `both`) |
| `--overwrite` | replace the target database if it already exists |

**It fails loudly.** If a referenced supplier code or elementary-flow code does not exist in your
project, the importer prints every missing reference — with the dataset and the exchange that
wanted it — and exits with code 2 **before writing anything**. The usual cause is that your
BAFU-2026 or EF 3.1 release differs from the one the export was made against
(`links_against` in the JSON records which that was).

### Explicit vs hybrid — which node to use

Each rebuilt dataset produces up to two nodes:

* **`<bafu-code>-disagg`, "… , disaggregated"** — the *explicit* model: only the exchanges the
  evidence supports. Transparent, but incomplete: its cumulative inventory does **not** equal the
  original aggregated dataset.
* **`<bafu-code>-hybrid`, "… , hybrid"** — the same exchanges **plus a residual block** of
  elementary flows equal to *(original cumulative inventory − explicit cumulative inventory)*,
  flow by flow. By construction the hybrid reproduces the original dataset **exactly**, while the
  part that is explained by a real supply chain is visible as named technosphere exchanges. This
  is strategy **S5** and it is what you want if you care about not changing your results.

Use the **hybrid** if you need results that match BAFU-2026. Use the **explicit** node only when
you deliberately want the incomplete, evidence-only model — for example to substitute a different
electricity mix into the part of the chain that *is* explicit.

The residual can contain negative amounts (where the explicit model overshoots the original). That
is expected and is what makes the hybrid exact.

> **Note on the residual and redistribution.** A residual block is *the original BAFU-2026
> cumulative flow vector minus the explicit model*, flow by flow. It therefore carries BAFU's
> numbers. If you are passing this export on and may not redistribute BAFU data, regenerate it
> with `scripts/export_disaggregated.py --no-residual`: the explicit nodes still export in full
> (they are derived from the public reports), and the recipient can rebuild the hybrids themselves
> from their own BAFU-2026 copy.
>
> **Note on release drift.** The residual was computed against the BAFU-2026 release named in
> `links_against`. If your copy differs, the hybrid will no longer be exactly equal to *your*
> original — it will be exactly equal to the one the export was made from. The importer cannot
> detect this; it only checks that the codes exist.

---

## Round-trip verification

`scripts/verify_import_roundtrip.py` imports this export into a scratch project and checks it, so
the claims above are measured rather than asserted:

```bash
PYTHONPATH=src python scripts/verify_import_roundtrip.py --source bafu-2026 --scratch import-test
```

The run behind the numbers in this file (`--source bafu-2026-t1 --scratch import-test-t1`):

```
STEP 1  refuse to import into a project that has no BAFU-2026
        OK   refused with: database 'bafu-2026' not found in project 'import-test-t1-empty'

STEP 2  scratch project 'import-test-t1', copied from 'bafu-2026-t1'
        databases: ['bafu-2026', 'bafu-2026-residual', 'ef-3.1-biosphere']   (build sandbox removed)

STEP 3  dry run:  resolved every reference: 40 nodes, 31692 exchanges
STEP 4  import:   wrote 40 nodes to 'bafu-2026-disaggregated'

STEP 5  technosphere exchanges: 442 (of which 432 link into bafu-2026)
        biosphere exchanges:  31210 (of which residual: 30988)
        dangling references:      0

STEP 6  LCA per imported dataset, cumulative inventory compared flow by flow with the original:
        20 datasets checked
        worst hybrid deviation:   8.905e-08        <- numerical noise
        explicit deviation range: 8.2 % to 155.4 %

RESULT: PASS
```

That last block is the whole story in two numbers: **the hybrid nodes reproduce the originals; the
explicit nodes do not.** If your own run shows a hybrid deviation that is not ~1e-8, your BAFU-2026
release is not the one this export was generated against.

---

## What the strategies mean

| | |
|---|---|
| **S1** | the report prints the dataset's inventory table — transcribed line by line, each amount traceable to a quoted line |
| **S2** | no table, but a *unit process of the same product* exists elsewhere in BAFU — its input structure is reused and the amounts are calibrated against the aggregated vector |
| **S3** | the report gives only a process description or a partial table (typical when the amounts are confidential) — the input **list** comes from the report, the **amounts** come from calibration |
| **S4** | nothing but the aggregated vector. Never used on its own: fitting an input list with no evidence produces a good-looking inventory with the wrong structure (see the `blind` row of the benchmark in the project README §6) |
| **S5** | hybrid: whatever S1–S3 produced, plus the residual block. Always built, so every rebuild can reproduce the original exactly |

"Calibrated" amounts are fitted by bounded least squares against the dataset's own aggregated flow
vector, with the input list held fixed. The export marks them: every technosphere exchange carries
`"calibrated": true/false`, and `"bounds"` when the fit was bounded. A `false` there means the
amount was read off the report.

---

## JSON format

```jsonc
{
  "schema": "reverse-bafu/disaggregated-bafu-2026",
  "schema_version": "1.0",          // major version bump = breaking change
  "generated_at": "...", "git_commit": "...", "source_project": "bafu-2026",
  "links_against": {                 // which databases the codes below refer to
    "inventory_database": "bafu-2026",
    "biosphere_databases": ["ef-3.1-biosphere", "bafu-2026-residual"]
  },
  "strategies": { "S1": "...", ... },
  "citation": "...",
  "datasets": [
    {
      "bafu_code": "<uuid>",             // the aggregated dataset this replaces
      "bafu_name": "...",
      "replaces": {"database": "bafu-2026", "code": "<uuid>", "name": "..."},
      "variant": "" | "draft",           // "draft" = produced by the LLM drafting pipeline
      "spec": "specs/....json",          // the spec it was generated from, in this repo
      "strategy": {"code": "S1", "label": "...", "note": "..."},
      "evidence": [{"source": "<report pdf>", "where": "pages 845-847 -> report-p845-847.txt"}],
      "quality": { ... },                // the agreement figures, copied from results/rebuild_status.csv
      "provenance": { "pipeline": ..., "extraction": ..., "mapping": ...,
                      "gaps_reported_by_model": [...], "skipped_items": [...] },
      "main_node_code": "<uuid>-disagg",
      "nodes": [
        {
          "node_code": "<uuid>-disagg",
          "name": "..., disaggregated", "location": "RER", "unit": "kilogram",
          "reference_product": "..., disaggregated",
          "technosphere": [
            {
              "supplier_code": "<uuid>",            // <- the BAFU-2026 code to link to
              "supplier_database_role": "bafu",     //    "bafu" = your bafu-2026;
                                                    //    "this-export" = another node in this file
              "supplier_name": "Cement, unspecified, at plant",
              "supplier_location": "CH",
              "amount": 215.0, "unit": "kilogram",
              "calibrated": true, "bounds": [180.0, 250.0],
              "comment": "...",
              "provenance": {                       // present where the pipeline recorded it
                "evidence": "report-p97-99.txt",
                "quote": "Portland Cement  ...  cement, unspecified, at plant  2.15E+02 kg",
                "raw_value": 215.0, "raw_unit": "kg", "per": "per m3 wood wool board",
                "factor": 1.0, "factor_source": "", "scale_to_unit": 1.0,
                "mapping_reason": "...", "confidence": "high",
                "by": "claude-code:...", "reviewed_by": null
              }
            }
          ],
          "biosphere": [
            {
              "flow_code": "<ef-3.1 uuid>",         // <- the elementary-flow code to link to
              "flow_database": "ef-3.1-biosphere",  // <- and the database it lives in
              "flow_name": "Waste Heat",
              "categories": ["air"],
              "kind": "emission" | "resource",
              "amount": 32.9, "unit": "megajoule",
              "comment": "...", "provenance": { ... }
            }
          ]
        }
      ],
      "residual": {                      // null if no hybrid was built
        "node_code": "<uuid>-hybrid",
        "name": "..., hybrid", "n_flows": 1289,
        "note": "S5 hybrid: ... reproduces the original exactly ...",
        "flows": [{"flow_code": "...", "flow_database": "...", "flow_name": "...",
                   "categories": [...], "amount": -1.2e-3, "unit": "kilogram"}]
      }
    }
  ]
}
```

Conventions worth knowing:

* **Codes, not names.** Every link is a code. Names are carried alongside for humans and are never
  used for matching.
* **`flow_database` matters.** Most elementary flows are EF 3.1, but BAFU-2026 also uses flows
  that have no EF 3.1 equivalent; those live in a second biosphere database (here
  `bafu-2026-residual`). The importer tries the named database first and then the others you gave
  it, so it still works if you keep them under different names.
* **`provenance.reviewed_by` is `null` everywhere.** Nothing in this export has been reviewed by a
  human LCA practitioner. Treat `"confidence": "low"` entries with particular suspicion.
* **`provenance.gaps_reported_by_model`** lists, per dataset, what the report did *not* cover.
  Read it — it is the honest part.

---

## Known quality limits

These are reconstructions, not the original data. The headline number per dataset is **what share
of the original's elementary flows the explicit model reproduces within ±10 %**, and for many of
them it is small.

| BAFU dataset | strategy | flows within +-10 % | of the 50 largest kg flows | kg mass covered | median deviation |
|---|---|---|---|---|---|
| Cement ZN, D, at plant (draft) | S1 | 249/1326 (19%) | 8/50 | 0.5 % | 28.7 % |
| Cement ZN, D, at plant | S1 | 249/1326 (19%) | 8/50 | 0.5 % | 28.7 % |
| Particle board, cement bonded, at plant (draft) | S1 | 140/1149 (12%) | 8/50 | 42.7 % | 63.0 % |
| Burnt shale, at plant | S1 | 128/1326 (10%) | 9/50 | 99.5 % | 66.2 % |
| Titanium dioxide at plant, sulphate process, at plant (draft) | S1 | 117/1148 (10%) | 11/50 | 13.3 % | 74.8 % |
| xxx Wood wool boards, cement bonded, at plant (draft) | S1 | 111/1149 (10%) | 7/50 | 30.6 % | 63.0 % |
| Burnt shale, at plant (draft) | S1 | 81/1326 (6%) | 3/50 | 30.4 % | 148.2 % |
| xx Packaging glass, white, at regional storage | S2 | 76/1146 (7%) | 5/50 | 0.1 % | 87.9 % |
| Anthraquinone, at plant (draft) | S1 | 75/1149 (7%) | 5/50 | 8.3 % | 68.1 % |
| xx Packaging glass, green, at regional storage | S2 | 72/1146 (6%) | 4/50 | 0.1 % | 88.9 % |
| xx Packaging glass, brown, at regional storage | S2 | 69/1146 (6%) | 3/50 | 0.1 % | 86.3 % |
| Gypsum plaster board, at plant | S2 | 59/1171 (5%) | 2/50 | 1.0 % | 99.9 % |
| xx Packaging glass, brown, at plant | S2 | 51/1146 (4%) | 3/50 | 0.1 % | 128.7 % |
| xx Packaging glass, white, at plant | S2 | 51/1146 (4%) | 4/50 | 0.2 % | 150.8 % |
| xx Packaging glass, green, at plant | S2 | 45/1146 (4%) | 4/50 | 0.6 % | 176.5 % |
| Titanium dioxide, chloride process, at plant (draft) | S1 | 42/1147 (4%) | 5/50 | 38.2 % | 70.7 % |
| Wood preservative, inorganic salt, containing Cr, at plant (draft) | S1 | 28/1148 (2%) | 0/50 | 0.0 % | 89.2 % |
| Gypsum fibre board, at plant | S2 | 27/1172 (2%) | 2/50 | 0.5 % | 245.9 % |
| xxx Wood wool boards, cement bonded, at plant | S2 | 26/1149 (2%) | 2/50 | 0.0 % | 70.1 % |
| Wood preservative, organic salt, Cr-free, at plant (draft) | S1 | 8/1149 (1%) | 0/50 | 0.0 % | 86.0 % |

Sorted worst-last. "flows within ±10 %" counts the elementary flows of the original aggregated
dataset that the **explicit** node reproduces within ±10 %, out of the flows the solve determines.
Source: `results/rebuild_status.csv`, and the per-dataset report named in each dataset's
`quality.report`.

Two caveats about the `strategy` column:

* Every spec produced by the drafting pipeline is labelled **S1**, because that is what the
  assembler writes. Several of them are in truth **S3**: the report named the inputs but printed
  `confidential` instead of the amounts, so the list is evidence and the amounts are a fit. You can
  tell them apart from the data: an S3-in-practice dataset has `"calibrated": true` on most of its
  technosphere exchanges. The two wood preservatives, the wood wool board, the particle board and
  (partly) anthraquinone are of that kind.
* Rows appearing twice (burnt shale, cement ZN D, wood wool board) are the same BAFU dataset
  rebuilt two ways — by hand and by the drafting pipeline (`"variant": "draft"`). They have
  different node codes and both are importable; pick one.


Read that column as: *the explicit node is a partial model.* The S2 rebuilds in particular — the
packaging glass family, the gypsum boards, the wood wool board — reproduce only a few per cent of
the original's flows, because the template unit process they borrow their structure from is a
different plant with a different supply chain, and calibration can only move amounts, not add or
remove inputs. The `kg_mass_covered` column shows the same thing from the mass side: for several
of them well under 1 % of the original's kilogram mass is explained.

Specific things to keep in mind:

1. **Only the hybrid node reproduces the original.** If you swap an aggregated dataset for the
   explicit `-disagg` node your results will change, often by a lot. That change is not an
   improvement in accuracy — it is the part of the supply chain the rebuild does not yet cover
   going missing. Use `-hybrid` unless you know exactly why you want otherwise.
2. **A good flow agreement does not prove a correct structure.** The project's calibration
   benchmark (project README §6) found the opposite case explicitly: adding ten random distractor
   inputs *improved* the inventory fit while giving a material amount to processes that are not in
   the real process at all. Inventory agreement and structural correctness are different things.
3. **Calibrated amounts are fits, not measurements.** Where a report printed "confidential", the
   input is in the list because the report names it, and the amount comes from the least-squares
   fit within the stated bounds. Those entries carry `"calibrated": true` and, usually,
   `"confidence": "low"` in their provenance. Several of them sit *on* their bound after the fit,
   which means the data wanted to go further and the bound stopped it.
4. **The drafted (`"variant": "draft"`) datasets were produced by an LLM pipeline** — locate the
   table in the PDF, transcribe it, map each line to a dataset or flow — with every step recorded
   and every number quoted, but **not** reviewed by a person. `reviewed_by` is `null` throughout.
5. **Coverage is limited by the documentation bundle.** Of the 101 aggregated datasets, only 34
   cite a report that is actually in the BAFU-2026 documentation bundle, and of those 34 most of
   the reports state outright that the unit-process data are confidential. The rest cannot be
   rebuilt from public evidence at all, and are deliberately absent from this export rather than
   invented. `results/drafting_status.csv` records the reason for each one.

---

## Licence and citation

The underlying data are BAFU's. Anything derived from them must carry:

> Source: Life Cycle Inventory database of the Swiss Federal Administration, BAFU:2026.

The disaggregation is a reconstruction by this project from the public LCI reports; it is not part
of BAFU-2026 and carries no endorsement by BAFU. Please say so when you pass these datasets on.
