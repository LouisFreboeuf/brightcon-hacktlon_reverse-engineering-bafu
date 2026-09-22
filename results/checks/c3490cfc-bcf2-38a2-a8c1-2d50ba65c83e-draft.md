# Check: Cement ZN, D, at plant (c3490cfc-bcf2-38a2-a8c1-2d50ba65c83e)

target `bafu-2026` vs explicit model `c3490cfc-bcf2-38a2-a8c1-2d50ba65c83e-draft-disagg` and hybrid `c3490cfc-bcf2-38a2-a8c1-2d50ba65c83e-draft-hybrid`

**Strategy:** S1 — transcription drafted from the report excerpt by the LLM pipeline (reverse-bafu draft). basis: per 1 kg cement ZN/D, ab Werk (Tab. 3.14, Werner 2018); the composition rows are percentage ranges of the kg; allocation: none stated for the cement itself; the burnt-shale input carries the economic allocation of section 3.6. Review every derivation; unreviewed entries have reviewed_by = null.
**Calibrated inputs:** Clinker, at plant [0.4–0.7], Gypsum, mineral, at mine [0–0.1], Recycling aggregate from mixed demolition, dry, at plant [0.15–0.3], Burnt shale, at plant [0.15–0.3], Iron sulphate, at plant [0–0.01], Limestone, milled, loose, at plant [0–0.1]; mass sum 1.0
**Links to rebuilt nodes:** Burnt shale, at plant

## Flow agreement (explicit vs target, per elementary flow)

- the 50 largest kilogram flows: 8/50 within ±10 %, median |Δ| 44.2%
- kilogram mass covered within ±10 %: 0.5% of the target's total kg mass
- of the 1326 flows of the target, 1326 are determined by the solve (0 are round-off and are not scored; see lci.determined_flows)
- 249 of those 1326 within ±10 % (19%), median |Δ| 28.7%, 0 missing from the model, 447 extra
- hybrid vs target: identical on every flow

| \|Δ\| bucket | flows | share of target flows |
|---|---|---|
| ≤ 10 % | 249 | 19% |
| 10–20 % | 186 | 14% |
| 20–50 % | 403 | 30% |
| 50–100 % | 299 | 23% |
| > 100 % | 189 | 14% |
| missing (0 in model) | 0 | 0% |

## Largest target flows (by amount, per unit) and their agreement

### kilogram (1084 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Calcite [resources/in ground] (kilogram) | 0.833 | 1.04 | +24.8% | -0.206 |
| Carbon Dioxide (fossil) [Emissions/Emissions to air] (kilogram) | 0.483 | 0.584 | +20.9% | -0.101 |
| Shale [soil] (kilogram) | 0.13 | 0.144 | +10.7% | -0.014 |
| Clay [soil] (kilogram) | 0.0547 | 0.0605 | +10.5% | -0.00572 |
| Gypsum [resources/in ground] (kilogram) | 0.0303 | 3.45e-06 | -100.0% | +0.0303 |
| Carbon Dioxide (biogenic) [Emissions/Emissions to air] (kilogram) | 0.0263 | 0.0428 | +62.7% | -0.0165 |
| Carbon Dioxide (fossil) [Emissions/Emissions to air] (kilogram) | 0.0229 | 0.0253 | +10.7% | -0.00245 |
| Carbon Dioxide (fossil) [Emissions/Emissions to air] (kilogram) | 0.0161 | 0.0124 | -22.8% | +0.00366 |
| Gravel [soil] (kilogram) | 0.0102 | 0.0162 | +58.8% | -0.00601 |
| Waste mass, total, placed in landfill [resources/in ground] (kilogram) | 0.00705 | 0.00765 | +8.4% | -0.000593 |
| Sulfate [emissions to water/groundwater, long-term] (kilogram) | 0.00443 | 0.00665 | +50.0% | -0.00221 |
| carbon dioxide (biogenic) [Resources/Resources from air] (kilogram) | 0.00259 | 0.00379 | +46.2% | -0.0012 |
| calcium [Emissions/Emissions to water] (kilogram) | 0.00202 | 0.00261 | +29.4% | -0.000593 |
| Carbon Dioxide (biogenic) [Emissions/Emissions to air] (kilogram) | 0.00178 | 0.00296 | +65.7% | -0.00117 |
| Carbon Monoxide (fossil) [Emissions/Emissions to air] (kilogram) | 0.000985 | 0.00179 | +81.6% | -0.000804 |
| Chloride [Emissions/Emissions to water] (kilogram) | 0.000979 | 0.000348 | -64.4% | +0.000631 |
| Carbon Dioxide (biogenic) [Emissions/Emissions to air] (kilogram) | 0.000919 | 0.000423 | -54.0% | +0.000496 |
| Silicon [Emissions/Emissions to water] (kilogram) | 0.000742 | 0.000998 | +34.4% | -0.000255 |
| Iron [Resources/Resources from ground] (kilogram) | 0.000718 | 0.000733 | +2.1% | -1.51e-05 |
| Nitrogen Oxides [Emissions/Emissions to air] (kilogram) | 0.000602 | 0.000636 | +5.8% | -3.47e-05 |

### kilo Becquerel (138 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Radon-222 [Emissions/Emissions to air] (kilo Becquerel) | 45.9 | 45.3 | -1.5% | +0.683 |
| Noble Gases, Radioactive, Unspecified [air] (kilo Becquerel) | 17.8 | 15.4 | -13.5% | +2.41 |
| Hydrogen-3 [Emissions/Emissions to water] (kilo Becquerel) | 0.717 | 0.62 | -13.5% | +0.0968 |
| Radon-222 [Emissions/Emissions to air] (kilo Becquerel) | 0.71 | 0.402 | -43.4% | +0.308 |
| Hydrogen-3 [Emissions/Emissions to water] (kilo Becquerel) | 0.0783 | 0.486 | +520.3% | -0.408 |

### square meter (37 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| To Arable, Non-irrigated, Intensive [Land use/Land transformation] (square meter) | 7.7e-05 | 9.73e-05 | +26.4% | -2.03e-05 |
| From Arable, Non-irrigated, Intensive [Land use/Land transformation] (square meter) | 5.46e-05 | 6.82e-05 | +24.8% | -1.35e-05 |
| To Arable, Non-irrigated [Land use/Land transformation] (square meter) | 3.09e-05 | 4.56e-05 | +47.3% | -1.46e-05 |
| From Arable, Non-irrigated [Land use/Land transformation] (square meter) | 2.98e-05 | 4.21e-05 | +41.4% | -1.23e-05 |
| To Forest, Intensive [Land use/Land transformation] (square meter) | 2.5e-05 | 3.83e-05 | +53.1% | -1.33e-05 |

### cubic meter (23 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Water [Emissions/Emissions to water] (cubic meter) | 1.03 | 0.934 | -9.2% | +0.0944 |
| Water to turbine [Resources/Resources from water] (cubic meter) | 1.03 | 0.932 | -9.2% | +0.0946 |
| Water [Resources/Resources from water] (cubic meter) | 0.000992 | 0.00158 | +59.1% | -0.000586 |
| river water [Resources/Resources from water] (cubic meter) | 0.000586 | 0.00054 | -7.8% | +4.58e-05 |
| Water To Cooling [Resources/Resources from water] (cubic meter) | 0.000568 | 0.000541 | -4.9% | +2.77e-05 |

### megajoule (21 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Crude Oil [Resources/Resources from ground] (megajoule) | 0.994 | 1.03 | +3.7% | -0.0364 |
| Waste Heat [air] (megajoule) | 0.938 | 0.91 | -2.9% | +0.0276 |
| Uranium [Resources/Resources from ground] (megajoule) | 0.707 | 0.612 | -13.5% | +0.0951 |
| Hard Coal [Resources/Resources from ground] (megajoule) | 0.583 | 0.174 | -70.2% | +0.409 |
| Waste Heat [air] (megajoule) | 0.559 | 0.532 | -4.9% | +0.0273 |

### square meter-year (17 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Forest, Intensive [Land use/Land occupation] (square meter-year) | 0.00215 | 0.00337 | +56.8% | -0.00122 |
| Forest [Land use/Land occupation] (square meter-year) | 0.00128 | 0.00146 | +14.0% | -0.00018 |
| Industrial Area [Land use/Land occupation] (square meter-year) | 0.000426 | 0.000374 | -12.3% | +5.26e-05 |
| Mineral Extraction Site [Land use/Land occupation] (square meter-year) | 0.000197 | 0.00017 | -14.0% | +2.76e-05 |
| Traffic Area, Road Network [Land use/Land occupation] (square meter-year) | 0.000195 | 0.000223 | +14.3% | -2.8e-05 |

### kilometer (2 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Noise, road, lorry, average [non material emissions/unspecified] (kilometer) | 0.00406 | 0.00792 | +95.0% | -0.00386 |
| Noise, road, passenger car, average [non material emissions/unspecified] (kilometer) | 2.48e-05 | 2.3e-05 | -7.4% | +1.82e-06 |

### ton kilometer (2 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Noise, rail, freight train [non material emissions/unspecified] (ton kilometer) | 0.0595 | 0.108 | +81.3% | -0.0484 |
| Noise, aircraft, freight [non material emissions/unspecified] (ton kilometer) | 3.24e-07 | 3.75e-07 | +15.8% | -5.1e-08 |

### cubic meter-year (1 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Volume Occupied, Reservoir [land use] (cubic meter-year) | 0.00455 | 0.00396 | -13.0% | +0.000591 |

### person kilometer (1 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Noise, aircraft, passenger [non material emissions/unspecified] (person kilometer) | 1.89e-06 | 2.41e-06 | +27.4% | -5.18e-07 |

## Worst deviations among the 50 largest kilogram flows

| flow | target | explicit | Δ |
|---|---|---|---|
| Gypsum [resources/in ground] (kilogram) | 0.0303 | 3.45e-06 | -100.0% |
| Non-methane Volatile Organic Compounds [Emissions/Emissions to air] (kilogram) | 5.23e-05 | 2.58e-06 | -95.1% |
| Platinum [air] (kilogram) | 0.00047 | 0.000868 | +84.7% |
| Solids, Inorganic [water] (kilogram) | 6.44e-05 | 0.000118 | +83.8% |
| Aluminium [Resources/Resources from ground] (kilogram) | 0.000499 | 0.000915 | +83.5% |
| Carbon Monoxide (fossil) [Emissions/Emissions to air] (kilogram) | 0.000985 | 0.00179 | +81.6% |
| Sodium [water] (kilogram) | 8.45e-05 | 0.00015 | +77.3% |
| Methane (fossil) [Emissions/Emissions to air] (kilogram) | 0.000359 | 9.78e-05 | -72.7% |
| Sodium chloride [resources/in ground] (kilogram) | 7.06e-05 | 0.000117 | +66.2% |
| Sodium [water] (kilogram) | 0.000319 | 0.000108 | -66.1% |

## Structural checks

- ✓ 13 explicit input(s) over 1 node(s)
- ✓ no decomposed grid mixes
- ✗ depends on aggregated datasets (rebuild those first): ['Ethylene glycol, at plant']
- ✓ mass in: 1.05 kg technosphere + 0 kg resources per 1 kg product (informational)
- ✓ all inputs resolved

residual: 538 flows under-explained, 1235 over-explained (negative residual)

## Evidence

- 2020 - LCA selected types of concrete - Tschuemperlin.pdf — pages 25-26 -> report-p25-26.txt report sha256 83e2e7ea46d35899…, text sha256 95d82d20fed0b8de…
