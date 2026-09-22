# Disaggregating the 101 "system terminated" BAFU datasets

Written for the hackathon team working on
[brightcon-2026-material#38](https://github.com/Depart-de-Sentier/brightcon-2026-material/issues/38).
Data basis: `results/system_terminated.csv` (produced by `scripts/list_system_terminated.py`),
the raw ecoSpold XML comments, and the `bafu-2026` Brightway database.

## 1. What the 101 are

All 101 carry ecoSpold `type=2`: the dataset holds the *cumulative* elementary flows of its whole
upstream chain (an LCI result), not the process's own flows plus links to suppliers. 87 have no
technosphere inputs at all; the 14 PlasticsEurope polymers keep 1-17 inputs, but those are only
the waste-treatment services ecoinvent v2 attached to the eco-profile's reported waste amounts.
The production chain itself (crude oil → naphtha → cracker → polymer) is folded into the flows.

The long flow lists are real, not padded: the ~1,300-flow (Empa) and ~1,660-flow (French) vectors
have 0-2 zero-amount entries each. They are the full ecoinvent-v2 / openLCA background resolved.

### Families, by data origin (the `family` column)

| Family | n | Consuming processes | Origin | Public data behind it | Unit-process sibling in BAFU |
|---|---|---|---|---|---|
| `plasticseurope` | 14 | **1,049** (HDPE 533, PP 173, LDPE 122, ethylene glycol 76, ethylene 72) | PlasticsEurope eco-profiles 2012-2014, via ecoinvent v2 | Eco-profile PDFs: gross energy per fuel, per stage (feedstock / fuel use / process / transport), waste, emissions — but cradle-to-gate totals only; member data confidential | none for the polymers; `Naphtha, at refinery` (32 inputs) and `Chemical plant, organics` exist as building blocks; no steam-cracker dataset in BAFU |
| `ecoinvent-v2-confidential` | 24 | 150 (zeolite 40, polycarboxylates 35, CMC 22, latex 22, feldspar 15) | Empa/ETH/ESU 2007: ecoinvent reports 8, 9, 11, 12 | Reports exist (ecoQuery v2 login) but the XML says "inventory data are confidential" / "based on company information" — the reports do not print unit-process tables for these | 4: the three `xx Packaging glass` colours and `Wood wool boards, cement bonded` (all obsolete `xx` variants) |
| `treeze-kbob` | 10 | 13 | treeze reports for KBOB: gypsum 2016 ("data from German manufacturers"), concrete 2020, cellulose 2014 | Reports public on treeze.ch; the German-manufacturer gypsum data likely aggregated by contract | 2: `Gypsum fibre board` (CH unit process with 10 inputs, DE aggregated), `Gypsum plaster board` |
| `french-biobased` | 29 | **0** | 2022 *Rapports méthodologiques ACV*: flax, hemp, jute, straw bale, rammed earth (FDES background studies) | Reports not found online; derived FDES are on INIES (module results only). Likely obtainable from the authors (FRD / Karibati / EVEA style studies) | none |
| `kbob-manufacturer` | 24 | 10 | Manufacturer-specific KBOB datasets: Flumroc rock wool (5), Misapor cellular glass (2), Hydro window frames (3), Baumgartner windows (4), V-ZUG washing machine (3), CLT (2), perlite brick (2), Supafil, render board | Manufacturer EPDs are public for Flumroc, Misapor, Hydro CIRCAL; the underlying bills of materials are confidential | generic siblings for the window frames (`Window frame, wood, opaquely painted, U=1.2 W/m2K, wall opening, at plant`, 2 inputs) — the manufacturer token in the name prevents the exact match in the CSV |

Two consequences for planning:

- **Impact and feasibility are anti-correlated.** The family that matters most downstream
  (PlasticsEurope, ~1,050 consumers, and HDPE alone touches 212 transport datasets) has no public
  unit-process data. The family with the best chance of clean transcription (French, 29 datasets)
  changes no downstream result.
- **A third of the list is obsolete or leaf.** 12 datasets carry the `xx`/`xxx` obsolete prefix
  and 60 have zero consumers. Replacing them only improves transparency of that one dataset.

### What the BAFU documentation bundle adds

The official `BAFU-2026 v1_Documentation` zip ships 114 LCI report PDFs whose file names equal the
`source.title` field of the XML, so `scripts/list_sources.py --reports …` joins them automatically:
108 of the 125 sources have a PDF, covering 11,541 of the 11,947 datasets. For the 101 aggregated
datasets the bundle was checked report by report:

| Family | PDF in bundle | What it contains for the flagged datasets | Consequence |
|---|---|---|---|
| `plasticseurope` | **`2025 - LCI plastics - Rajabihamedani.pdf`** (ESU-services for FOEN, July 2025) — not cited by any dataset, but it is *the* documentation of these 14 | States the PlasticsEurope data "are nowadays only available as system processes" (ILCD, by IFEU / PE International); documents the disposal re-linking to UVEK datasets (Tab. 3.1), substance/resource name mapping (Tab. 3.2–3.3), the methane add-on `CH4 = crude oil [kg]·0.0117 + natural gas [m³]·0.006`, a wrong-unit fix (crude oil reported in MJ, assumed kg) and a ×1000 correction on one flow, pedigree uncertainty set to 5 | No unit-process data, but everything needed to *undo* the post-processing before fitting (S4): strip the methane add-on and disposal inputs, then fit the remaining eco-profile vector |
| `ecoinvent-v2-confidential` — detergents (Zah 2007) | yes, 97 p. | Zeolite: "no unit process data … can be shown" (Fawer 1996 / Dall'Acqua 1999 confidential), but the process is described: hydrogel route from aluminium hydroxide + sodium silicate + NaOH, 38 % slurry / 62 % dried to 20 % water, "transport and infrastructure estimated" | S3 stoichiometric model + S4 fit; the description fixes the candidate input set |
| — packaging (Hischier 2007) | yes, 17 p. (overview only; Part II–IV are separate) | Latex, feldspar: APME/industry aggregated; packaging glass: obsolete `xx` datasets with unit-process siblings | S2 for glass, S3/S4 for latex/feldspar |
| — chemicals (Althaus 2007) | yes, 957 p. | TiO₂ chloride process, anthraquinone, versatic acid ester: chapters exist (§44, §85, §91) with process descriptions and literature (UBA BAT notes); inventory itself confidential | S3 from BAT data |
| — wood (Werner 2007) | yes, 176 p. | Wood wool boards: "energy consumption … is confidential"; the unit-process table is printed with `confidential` in the electricity cell, everything else visible | S2/S3: only one number is missing |
| `treeze-kbob` — concrete (Tschümperlin 2020) | yes | **Full gate-to-gate inventory tables**: burnt shale (Tab. 3.9: explosives, diesel, kWh per step, HCl/NaOH, dust/NOx/SO₂/CO₂ split fossil/geogenic), cement ZN/D (Tab. 3.14), CEM I–III (Tab. 3.11–3.13), transport distances (Tab. 3.10) | **S1 transcription** — the cleanest cases in the whole list |
| — KBOB renewal (Kasser 2016, 436 p.) | yes | Gypsum boards: "Sachbilanzdaten … im vertraulichen Anhang Z"; only the binder (anhydrite / hemihydrate) inventories and transport are printed; Misapor data confidential | S2 from the CH `Gypsum fibre board` unit process + printed binder data |
| — KBOB update (Wyss 2014) | yes, 23 p. | Cellulose fibres (isofloc): manufacturer-specific, "vertraulicher Hintergrundbericht (Werner 2011)" | S3/S4 |
| `french-biobased` | **no** | — | reports still to be obtained |
| `kbob-manufacturer` | no dedicated report; some appear inside Kasser 2016 (Misapor: confidential) | — | S3 from public EPDs or leave |

Net effect on the plan: `Burnt shale, at plant` and `Cement ZN, D, at plant` replace gypsum as the
first S1 pilot (a printed table, one consumer each), the 2025 plastics report makes the PlasticsEurope
fit better-posed than assumed, and the French family stays blocked on report access.

### What the ecoSpold metadata itself adds

Beyond the source citation, every dataset carries an `administrativeInformation` block (data-entry
person, data-generator person, proof-reading validator — each with name, company code and country;
addresses and e-mails are anonymised), a `representativeness` block (`samplingProcedure`, `percent`
of production covered, `productionVolume`, `extrapolations`), a `timePeriod`, and sometimes a second
`source`. `results/system_terminated.csv` now carries these as columns. For the 101:

| Family | Data generator / validator | Representativeness | Second source |
|---|---|---|---|
| `plasticseurope` | Christoph Meili / Niels Jungbluth [ESU] | "Questionnaires sent out to all production units in Europe operated by PlasticsEurope member companies"; **68.3 % of 6,720 kt HDPE (2011)**, 76.7 % PP, 72.3 % LDPE; period 2011–2023; "external review passed" | **`2025 - LCI plastics - Rajabihamedani`** — the ESU report is cited in the XML, just not as first source |
| `ecoinvent-v2-confidential` | Hischier [EMPA], Zah, Althaus [ecoexistence] / Kunst, Althaus, Dones | "company information by a filled in questionnaire", "survey", partly 90–100 % production coverage; period 2000 | — |
| `treeze-kbob` | Daniel Savi, Frank Werner [U+E], Büsser [treeze] | mostly empty | — |
| `kbob-manufacturer` | Stolz, Krebs, Messmer [treeze]; 11 "default / Not reviewed" | "Data survey at window manufacturer Baumgartner", "Data survey at SAPA Building Systems AG" | — |
| `french-biobased` | **Sébastien Lasvaux [HEIG/CH]** for all 29 (entry, generation and validation) | "Data were compiled from one agricultural …", "… from expert knowledge"; period placeholder 9999 | — |

The person fields answer the open question about the French reports: they were brought into BAFU
by Sébastien Lasvaux (HEIG-VD, Yverdon), so the *rapports méthodologiques* should be obtainable
from him rather than searched for online. The representativeness fields also give the fit (S4) a
hard constraint for PlasticsEurope: the eco-profile is a production-weighted European average, not
a single site.

What the metadata does *not* add: the per-exchange `generalComment` on aggregated datasets is a
pedigree placeholder only — `(5,5,5,5,5,BU:x); All uncertainty-values set to 5.0 by default as data
comes from System process` — so there is no per-flow provenance to mine. (The default-5 pedigree is
itself a usable aggregation marker, complementary to `type=2`.)

## 2. Strategies

### S1 · Transcription from the report
The report prints the inventory table (inputs, direct emissions); map each line to a BAFU dataset
name and emit a unit process. This is the only strategy that recovers the *actual* model.
Applies to: `french-biobased` (once the reports are obtained), `treeze-kbob` concrete/cellulose,
possibly the gypsum family. LLM fit: high — PDF table extraction and name mapping against the
11,947 BAFU names are exactly the tasks LLMs do well, and the harness (§3) catches mistakes.

### S2 · Template transfer from a sibling unit process
BAFU already contains a unit process of the same product for another location, U-value or vintage.
Copy its structure, adapt the parameters that differ (electricity mix DE vs CH, transport
distances, mass per m²), and check against the aggregated vector. Applies to: gypsum fibre board
(CH unit → DE aggregated), packaging glass, wood wool boards, the Baumgartner/Hydro window frames
(generic market-mix siblings). LLM fit: medium — the adaptation is judgement, the diff is mechanical.

### S3 · Top-down model from public technical parameters
No inventory table, but the eco-profile / EPD gives stage splits, energy per fuel, feedstock
share, yields. Build the chain explicitly from BAFU unit processes (naphtha, electricity, steam,
transport, infrastructure, the existing disposal inputs) with amounts derived from those
parameters and stoichiometry. Applies to: `plasticseurope` (eco-profile PDFs are public),
`kbob-manufacturer` (EPDs), `ecoinvent-v2-confidential` (report text gives process descriptions).
This is what ecoinvent v3 did when it turned the PlasticsEurope eco-profiles into datasets with
technosphere inputs — a documented precedent worth reading before inventing a method.
LLM fit: medium-high for extracting the parameters; the model choices need an LCA practitioner.

### S4 · Inventory fitting (the "reverse engineering" proper)
Treat the aggregated flow vector **b** as the target and the cumulative LCIs of candidate BAFU
inputs as columns **A**; solve **min ‖A·x − b‖, x ≥ 0** (non-negative least squares). The
background database supplies **A** for free (one `bw2calc` inventory per candidate). Constrain
the candidate set and bounds with S3's parameters, otherwise the fit is not identifiable (electricity
and heat LCIs are collinear). Output: input amounts that reproduce the target, plus a residual that
says which flows no candidate explains. Applies everywhere as the quantitative complement to S3;
the only option for confidential datasets. LLM fit: low for the solve, high for proposing candidates.

### S5 · Hybrid unit process with an explicit residual
Whatever S1-S4 identify, keep the remainder as a residual elementary-flow block:
**residual = b − Σ xᵢ·LCIᵢ**. The dataset becomes "explicit inputs + residual flows", its scores
stay identical *by construction*, and a single metric — share of each impact category carried by
the residual — measures how far disaggregation got. This makes "results stay the same" trivial
and turns the work into shrinking the residual. Negative residual entries flag over-explained
inputs. This is the framework I'd adopt for all families; S1-S4 are ways to move mass out of the
residual. Related reading in `references.txt`: Bourgault et al. 2012 (hybrid LCI computation with
partially aggregated data) and Schindler et al. 2025 (closing EPD data gaps with emission factors
in Brightway).

## 3. Verification harness (build this first)

Every strategy needs the same two diffs, so build them once, as a script that takes the original
code and a candidate unit process (dict of technosphere inputs + direct elementary flows):

1. **Score diff** — 25 EF 3.1 categories, %Δ vs the original dataset. Acceptance criterion; the
   `sentier_brightway.backtest.compare` module already implements this against openLCA scores.
2. **Flow diff** — candidate's cumulative inventory (`lca.inventory` summed) vs the original's
   1,300-1,700 flows, sorted by contribution to each category. The diagnostic: if CO₂ matches but
   Radon-222 is 40 % low, the electricity input is too small.

Plus, for S5, the residual share per category. Write the candidate into a sandbox database linked
to `bafu-2026` so the original stays untouched and consumers can be re-scored against both.

## 4. Recommendation

Three findings shape it: (i) an NNLS fit of a *known* unit process's cumulative inventory
reproduces all 25 EF scores to 1.000 while choosing 116 wrong inputs — scores do not identify
structure (with the true 10 input names fixed, the same fit gets 8/10 amounts within ±12 %);
(ii) the BAFU documentation bundle prints full inventories for some datasets and states
confidentiality for others; (iii) ~40 of the 101 need intermediate nodes that BAFU lacks (steam
cracker, flax/hemp scutching), the rest are one-node replacements.

1. **Representation: S5, always.** Explicit inputs + residual vector. "Results stay the same"
   holds by construction; progress = residual share per category. Never use score agreement as
   proof of a correct structure.
2. **Evidence before amounts.** The input list comes from report tables → report text / BAT
   descriptions → ecoSpold `includedProcesses` / `technology` → BAFU sibling unit processes.
   Amounts are transcribed where printed, otherwise NNLS-calibrated *with the list fixed*.
3. **Depth rule: terminate on the database.** New nodes only where no BAFU node exists; stop
   when every input is an existing dataset. Shared new nodes (one cracker → 6 polymers, one
   scutching node → ~10 bio-based datasets) are front-loaded work, not per-dataset cost.
4. **Harness first**: score diff, flow diff, residual share, and *structural* checks (plausible
   input count for the category, no decomposed grid mixes, mass/energy balance).
5. **LLMs** extract tables and parameters from the PDFs, map report line-items to BAFU dataset
   names, and draft nodes with metadata. They do not pick amounts without a fixed structure.
   Metric for the hackathon: share of datasets per tier that pass the harness without a human edit.

| Tier | Datasets | Route | Why |
|---|---|---|---|
| 1 transcribe | `Burnt shale, at plant`, `Cement ZN, D, at plant` (concrete 2020, Tab. 3.9 / 3.14); wood wool board (one confidential cell); packaging glass (siblings) | S1 / S2, one node | ground truth in hand — calibrates harness and pipeline |
| 2 describe + calibrate | zeolite family (10, 105 consumers), TiO₂ / anthraquinone, gypsum boards (CH sibling + printed binder data), isofloc cellulose | S3 + fixed-list NNLS + S5 | single layer, precursors exist in BAFU, reports give process description and representativeness |
| 3 sub-model | PlasticsEurope (14, ~1,050 consumers) | new cracker + polymerisation nodes; strip the 2025 ESU methane / disposal layers first; structure after ecoinvent v3's ethylene chain; explicit multi-output allocation | highest leverage; practitioner models, LLM extracts parameters |
| 4 blocked | French bio-based (29) | S1, multi-layer, once reports arrive | ask Sébastien Lasvaux (HEIG-VD); then the LLM automation test set |
| skip | `kbob-manufacturer` (confidential BOMs, 10 consumers), the 12 obsolete `xx` | — | no evidence, no leverage |

Order this week: harness → burnt shale by hand → zeolite through the pipeline → e-mail Lasvaux →
decide whether the cracker sub-model is in scope.

### Status: pipeline built, burnt shale through it

`src/reverse_bafu/` implements resolve → calibrate → build → check (README has the commands).
`Burnt shale, at plant` transcribed from Tab. 3.9 / 3.10: all 12 inputs terminate on existing
BAFU unit processes; direct CO₂ (0.422 kg) alone reproduces the target's climate score (0.429).
The table's gross grid electricity (68.6 kWh/t) is not what the original model used — it
overshoots ionising radiation by +614 % and the fixed-list fit puts it near zero, consistent
with the plant running on its 183.8 kWh/t co-generated electricity. After calibrating that
single amount, the energy-driven categories agree within ±7 %; toxicity, land and water
categories still miss flows the table does not print (metals from burning, water balance).
Two more rebuilds followed: `Cement ZN, D, at plant` (S1, composition ranges calibrated with a
1 kg mass constraint, linking the rebuilt burnt shale; climate −20 %, 8/25 within ±10 %) and
`Gypsum fibre board, at plant` DE (S2 from the CH unit process scaled to 10 kg/m²; climate
−51 %, 4/25 — the Swiss structure does not describe the German plant). Lessons: the harness
finds modelling conventions the report does not state; small-score categories need the flow
diff, not the score, to tell what is missing; and the calibration's category weighting is a
policy choice (`category_weights` in the spec) — equal weights by default.

### Benchmark on synthetic aggregated datasets

`reverse-bafu benchmark --n 40 --seed 7` turns 40 BAFU unit processes (one per category, 3–30
inputs) into system-terminated lookalikes — their cumulative inventory is exactly what a type=2
export would hold — and scores the calibration step against the known inputs under five evidence
packages (`results/benchmark/n40-seed7.md`):

| evidence package | cases with all 25 categories within ±10 % | material amounts within ±20 % | cases with wrong inputs chosen | residual share p90 |
|---|---|---|---|---|
| oracle — correct list, no amounts | 37 / 40 | 92 % | 0 | 0.0 % |
| bounded — list + amounts to ×2 | 34 / 40 | 93 % | 0 | 0.1 % |
| partial — 30 % of inputs missing | 27 / 40 | 81 % | 0 | 1.8 % (worst-category deviation p90: 61 %) |
| distractors — list + 10 wrong candidates | 35 / 40 | 85 % | **4** | 0.2 % |
| blind — no list, no direct flows (5 cases) | 0 / 5 | 0 % | 5 (22–27 wrong inputs each) | 44 % median |

Reading: with the right names the amounts come back; a report that omits minor lines keeps the
headline scores and loses the small-score categories (the pattern of the three real rebuilds);
and with plausible wrong candidates on the list, one case in ten swaps a true input for a
distractor *while the scores stay within tolerance* — the identifiability trap, measured.
Building the benchmark exposed two numerical traps now fixed in the pipeline: columns spanning
10¹² in magnitude (an infrastructure "unit" vs a kg) stall the solver unless normalised, and
weighting categories by their net score explodes when the score is tiny through cancellation
(biogenic CO₂ uptake vs release) — categories are now weighted by the sum of absolute
contributions.

### Reproducibility of the specs

The specs are the evidence step, so they are where reproducibility matters most. `reverse-bafu
evidence / draft / assemble` (README) splits the work: deterministic evidence extraction with
hashes, a pinned two-pass LLM step (extraction with verbatim quotes; mapping against
deterministically generated candidate lists) whose prompts and raw responses are stored, and a
deterministic assembly that writes a `derivation` on every entry. The prompt rules keep the
model from doing the two things that need judgement — inventing inputs the excerpt does not
mention (reported as `gaps`) and deciding amounts it is unsure of (flagged, calibrated later).
On burnt shale the drafted spec equals the hand-written one on every transcribed number.

## 5. Open questions

- The 2022 French *rapports méthodologiques* are not in the BAFU documentation bundle; ask
  Sébastien Lasvaux (HEIG-VD), who generated and validated all 29 datasets.
- Tolerance: ±5 % on climate change and ±20 % on toxicity categories is a starting proposal; the
  BAFU openLCA backtest already shows toxicity categories deviate for method reasons.
- For PlasticsEurope, decide whether the target is the 2012 eco-profile (what BAFU holds, with the
  methane update noted in the comment) or the current 2022 version.
- Report the dropped `type` flag to sentier-importers so this list becomes a column upstream.

## Sources

- EcoSpold01 `type` semantics: [EcoSpold01MetaInformation.xsd, lines 26-60](https://github.com/brightway-lca/pyecospold/blob/main/pyecospold/schemas/v1/EcoSpold01MetaInformation.xsd#L26-L60)
- PlasticsEurope eco-profiles: [eco-profiles set](https://plasticseurope.org/sustainability/circularity/life-cycle-thinking/eco-profiles-set/), [program and methodology v3.0](https://plasticseurope.org/wp-content/uploads/2021/12/PlasticsEurope-Ecoprofiles-program-and-methodology_V3.0.pdf), [HDPE/LDPE/LLDPE eco-profile 2014 (mirror)](https://www.pedagogie.ac-aix-marseille.fr/upload/docs/application/pdf/2015-11/4-_eco-profile_pe_2014-04.pdf)
- treeze reports: [Ökobilanz ausgewählter Betonsorten (2020)](https://treeze.ch/de/projects/fallstudien/gebaeude-und-baumaterialien/oekobilanz-ausgewaehlter-betonsorten-und-betonfertigteile), [QualiBOB: renewal and extension of the KBOB recommendation](https://treeze.ch/projects/case-studies/building-and-construction/qualibob-project), [KBOB list](https://treeze.ch/projects/case-studies/building-and-construction/kbob/)
- ecoinvent v2 reports: [ecoinvent version 2 knowledge base](https://support.ecoinvent.org/ecoinvent-version-2), [Zah & Hischier 2007, Life Cycle Inventories of Detergents (report No. 12)](https://www.researchgate.net/publication/233739504_Life_Cycle_Inventories_of_Detergents)
- French bio-based FDES context: [Biofib' hemp insulation FDES (EVEA, 2022)](https://www.biofib.com/wp-content/uploads/biofib-chanvre-fdes-200.pdf), [hemp-lime concrete FDES](https://www.materiaux-naturels.fr/doc/product/fdes_187.pdf)
