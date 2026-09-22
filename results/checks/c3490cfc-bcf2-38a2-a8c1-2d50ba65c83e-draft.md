# Check: Cement ZN, D, at plant (c3490cfc-bcf2-38a2-a8c1-2d50ba65c83e)

target `bafu-2026` vs explicit model `c3490cfc-bcf2-38a2-a8c1-2d50ba65c83e-draft-disagg` and hybrid `c3490cfc-bcf2-38a2-a8c1-2d50ba65c83e-draft-hybrid`

**Strategy:** S1 — transcription drafted from the report excerpt by the LLM pipeline (reverse-bafu draft). basis: per 1 kg cement ZN/D, ab Werk (Tab. 3.14, Werner 2018); the composition rows are percentage ranges of the kg; allocation: none stated for the cement itself; the burnt-shale input carries the economic allocation of section 3.6. Review every derivation; unreviewed entries have reviewed_by = null.
**Calibrated inputs:** Clinker, at plant [0.4–0.7], Gypsum, mineral, at mine [0–0.1], Recycling aggregate from mixed demolition, dry, at plant [0.15–0.3], Burnt shale, at plant [0.15–0.3], Iron sulphate, at plant [0–0.01], Limestone, milled, loose, at plant [0–0.1]; mass sum 1.0
**Links to rebuilt nodes:** Burnt shale, at plant

## Scores (EF 3.1)

| category | target | explicit | Δ explicit | residual share | hybrid/target |
|---|---|---|---|---|---|
| Acidification | 0.001134 | 0.0008311 | -26.7% | +26.7% | 1.000000 |
| Climate change | 0.534 | 0.4277 | -19.9% | +19.9% | 1.000000 |
| Climate change-Biogenic | 0.000226 | 0.0002455 | +8.6% | -8.6% | 1.000000 |
| Climate change-Fossil | 0.5337 | 0.4275 | -19.9% | +19.9% | 1.000000 |
| Climate change-Land use and land use change | 4.704e-05 | 3.447e-05 | -26.7% | +26.7% | 1.000000 |
| EF-particulate Matter | 6.448e-09 | 4.875e-09 | -24.4% | +24.4% | 1.000000 |
| Ecotoxicity, freshwater | 0.4855 | 0.2234 | -54.0% | +54.0% | 1.000000 |
| Ecotoxicity, freshwater_inorganics | 0.4755 | 0.219 | -53.9% | +53.9% | 1.000000 |
| Ecotoxicity, freshwater_organics | 0.009985 | 0.0044 | -55.9% | +55.9% | 1.000015 |
| Eutrophication marine | 0.0002738 | 0.0002258 | -17.5% | +17.5% | 1.000000 |
| Eutrophication, freshwater | 6.223e-05 | 6.018e-05 | -3.3% | +3.3% | 1.000000 |
| Eutrophication, terrestrial | 0.003075 | 0.00263 | -14.5% | +14.5% | 1.000000 |
| Human toxicity, cancer | 3.231e-11 | 3.51e-11 | +8.7% | -8.7% | 0.999232 |
| Human toxicity, cancer_inorganics | 2.31e-11 | 2.476e-11 | +7.2% | -7.2% | 1.000000 |
| Human toxicity, cancer_organics | 9.207e-12 | 1.034e-11 | +12.3% | -12.3% | 0.997306 |
| Human toxicity, non-cancer | 1.335e-09 | 1.677e-09 | +25.6% | -25.6% | 1.000000 |
| Human toxicity, non-cancer_inorganics | 1.287e-09 | 1.633e-09 | +26.9% | -26.9% | 1.000000 |
| Human toxicity, non-cancer_organics | 4.809e-11 | 4.387e-11 | -8.8% | +8.8% | 1.000000 |
| Ionising radiation, human health | 0.07777 | 0.05941 | -23.6% | +23.6% | 1.000000 |
| Land use | 0.3176 | 0.3005 | -5.4% | +5.4% | 1.000000 |
| Ozone depletion | 3.052e-09 | 1.728e-09 | -43.4% | +43.4% | 1.000000 |
| Photochemical ozone formation - human health | 0.0008464 | 0.0007225 | -14.6% | +14.6% | 1.000000 |
| Resource use, fossils | 2.632 | 1.955 | -25.7% | +25.7% | 1.000000 |
| Resource use, minerals and metals | 1.394e-07 | 1.493e-07 | +7.1% | -7.1% | 1.000000 |
| Water use | 0.03857 | 0.03928 | +1.9% | -1.9% | 1.000000 |

## Flow diff — worst categories, flows driving the gap (explicit − target, characterised)

### Ecotoxicity, freshwater_organics (Δ +55.9%)

| flow | target | explicit | Δ impact | share of target score |
|---|---|---|---|---|
| Hydrocarbons, Aromatic [Emissions/Emissions to water] (kilogram) | 2.29e-07 | 5.75e-08 | -0.00382 | -38.2% |
| Polycyclic Aromatic Hydrocarbons [Emissions/Emissions to water] (kilogram) | 1e-08 | 2.9e-09 | -0.0017 | -17.0% |
| Non-methane Volatile Organic Compounds [Emissions/Emissions to air] (kilogram) | 4.02e-05 | 0.000101 | +0.000523 | +5.2% |
| Non-methane Volatile Organic Compounds [Emissions/Emissions to air] (kilogram) | 5.23e-05 | 2.02e-06 | -0.000388 | -3.9% |
| Phenol [Emissions/Emissions to water] (kilogram) | 3.59e-08 | 2.38e-08 | -0.000211 | -2.1% |
| Cumene [Emissions/Emissions to water] (kilogram) | 1.08e-08 | 5.51e-08 | +0.000108 | +1.1% |
| Methane (fossil) [Emissions/Emissions to air] (kilogram) | 0.000359 | 6.34e-05 | -9.44e-05 | -0.9% |
| Methyl Cyclopentane [Emissions/Emissions to water] (kilogram) | 1.66e-07 | 4.86e-08 | -4.27e-05 | -0.4% |

### Ecotoxicity, freshwater (Δ +54.0%)

| flow | target | explicit | Δ impact | share of target score |
|---|---|---|---|---|
| Chloride [Emissions/Emissions to water] (kilogram) | 0.000979 | 0.00027 | -0.214 | -44.0% |
| Strontium [Emissions/Emissions to water] (kilogram) | 3.28e-06 | 9.17e-07 | -0.0427 | -8.8% |
| Iron [Emissions/Emissions to water] (kilogram) | 2.94e-05 | 3.4e-05 | +0.00985 | +2.0% |
| Hydrocarbons, Aromatic [Emissions/Emissions to water] (kilogram) | 2.29e-07 | 5.75e-08 | -0.00382 | -0.8% |
| Barium(2+) [Emissions/Emissions to water] (kilogram) | 1.14e-06 | 3.09e-07 | -0.00308 | -0.6% |
| Ammonium [Emissions/Emissions to water] (kilogram) | 1.73e-06 | 6.43e-07 | -0.0027 | -0.6% |
| Hydrogen Sulfide [Emissions/Emissions to air] (kilogram) | 1.79e-07 | 2.83e-08 | -0.00221 | -0.5% |
| Polycyclic Aromatic Hydrocarbons [Emissions/Emissions to water] (kilogram) | 1e-08 | 2.9e-09 | -0.0017 | -0.4% |

### Ecotoxicity, freshwater_inorganics (Δ +53.9%)

| flow | target | explicit | Δ impact | share of target score |
|---|---|---|---|---|
| Chloride [Emissions/Emissions to water] (kilogram) | 0.000979 | 0.00027 | -0.214 | -44.9% |
| Strontium [Emissions/Emissions to water] (kilogram) | 3.28e-06 | 9.17e-07 | -0.0427 | -9.0% |
| Iron [Emissions/Emissions to water] (kilogram) | 2.94e-05 | 3.4e-05 | +0.00985 | +2.1% |
| Barium(2+) [Emissions/Emissions to water] (kilogram) | 1.14e-06 | 3.09e-07 | -0.00308 | -0.6% |
| Ammonium [Emissions/Emissions to water] (kilogram) | 1.73e-06 | 6.43e-07 | -0.0027 | -0.6% |
| Hydrogen Sulfide [Emissions/Emissions to air] (kilogram) | 1.79e-07 | 2.83e-08 | -0.00221 | -0.5% |
| Aluminium [Emissions/Emissions to water] (kilogram) | 9.03e-07 | 6.55e-07 | -0.00108 | -0.2% |
| Ammonia [Emissions/Emissions to air] (kilogram) | 1.8e-05 | 2.39e-05 | +0.000787 | +0.2% |

### Ozone depletion (Δ +43.4%)

| flow | target | explicit | Δ impact | share of target score |
|---|---|---|---|---|
| Bromochlorodifluoromethane [Emissions/Emissions to air] (kilogram) | 1.91e-10 | 3.29e-12 | -1.3e-09 | -42.4% |
| CFC-114 [Emissions/Emissions to air] (kilogram) | 2.57e-09 | 1.55e-09 | -5.07e-10 | -16.6% |
| Bromotrifluoromethane [Emissions/Emissions to air] (kilogram) | 2.45e-11 | 5.49e-11 | +4.61e-10 | +15.1% |
| Cfc 113 [Emissions/Emissions to air] (kilogram) | 2.01e-11 | 5.72e-11 | +3.01e-11 | +1.0% |
| Chlorodifluoromethane [Emissions/Emissions to air] (kilogram) | 8.68e-10 | 1.87e-10 | -2.31e-11 | -0.8% |
| CFC-10 [Emissions/Emissions to air] (kilogram) | 7.28e-16 | 1.08e-11 | +7.78e-12 | +0.3% |
| CFC-12 [Emissions/Emissions to air] (kilogram) | 3.59e-12 | 5.38e-12 | +1.3e-12 | +0.0% |
| Cfc 113 [Emissions/Emissions to air] (kilogram) | 2.94e-13 | 1.33e-12 | +8.4e-13 | +0.0% |

### Human toxicity, non-cancer_inorganics (Δ +26.9%)

| flow | target | explicit | Δ impact | share of target score |
|---|---|---|---|---|
| Mercury [Emissions/Emissions to air] (kilogram) | 6.67e-09 | 1.01e-08 | +4.42e-10 | +34.3% |
| Arsenic [Emissions/Emissions to air] (kilogram) | 2.37e-08 | 4.83e-09 | -4.7e-11 | -3.7% |
| Mercury [Emissions/Emissions to air] (kilogram) | 6.13e-10 | 3.97e-10 | -2.8e-11 | -2.2% |
| Lead [Emissions/Emissions to air] (kilogram) | 2.24e-08 | 9.1e-09 | -2.32e-11 | -1.8% |
| Barium(2+) [Emissions/Emissions to water] (kilogram) | 1.14e-06 | 3.09e-07 | -1.18e-11 | -0.9% |
| Mercury [Emissions/Emissions to air] (kilogram) | 9.31e-11 | 1.69e-10 | +9.55e-12 | +0.7% |
| Arsenic [Emissions/Emissions to water] (kilogram) | 1.35e-08 | 1.66e-08 | +4.23e-12 | +0.3% |
| Cadmium [Emissions/Emissions to air] (kilogram) | 1.37e-09 | 9.98e-10 | -2.72e-12 | -0.2% |

## Structural checks

- ✓ 13 explicit input(s) over 1 node(s)
- ✓ no decomposed grid mixes
- ✗ depends on aggregated datasets (rebuild those first): ['Ethylene glycol, at plant']
- ✓ mass in: 1.05 kg technosphere + 0 kg resources per 1 kg product (informational)
- ✓ all inputs resolved

residual: 876 flows under-explained, 915 over-explained (negative residual)

## Evidence

- 2020 - LCA selected types of concrete - Tschuemperlin.pdf — pages 25-26 -> report-p25-26.txt report sha256 83e2e7ea46d35899…, text sha256 95d82d20fed0b8de…
