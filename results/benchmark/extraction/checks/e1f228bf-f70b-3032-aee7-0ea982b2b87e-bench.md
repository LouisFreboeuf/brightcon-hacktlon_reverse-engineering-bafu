# Check: Ventilation duct, steel, zinc coated, s= 0.75mm, at plant (e1f228bf-f70b-3032-aee7-0ea982b2b87e)

target `bafu-2026` vs explicit model `e1f228bf-f70b-3032-aee7-0ea982b2b87e-bench-disagg` and hybrid `e1f228bf-f70b-3032-aee7-0ea982b2b87e-bench-hybrid`

**Strategy:** S1 — transcription drafted from the report excerpt by the LLM pipeline (reverse-bafu draft). basis: Tabelle 42 'Lueftungskanaele aus verzinktem Stahlblech', column 'Lueftungskanal, Stahl verzinkt, s= 0.75mm, ab Werk' [CH], per 1 m2; allocation: none stated. Review every derivation; unreviewed entries have reviewed_by = null.
**Calibrated inputs:** Section bar rolling, steel [0.25–7.65]
**Links to rebuilt nodes:** none

## Flow agreement (explicit vs target, per elementary flow)

- the 50 largest kilogram flows: 47/50 within ±10 %, median |Δ| 1.8%
- kilogram mass covered within ±10 %: 96.8% of the target's total kg mass
- of the 1785 flows of the target, 1668 are determined by the solve (117 are round-off and are not scored; see lci.determined_flows)
- 1481 of those 1668 within ±10 % (89%), median |Δ| 2.0%, 0 missing from the model, 0 extra
- hybrid vs target: identical on every flow

| \|Δ\| bucket | flows | share of target flows |
|---|---|---|
| ≤ 10 % | 1489 | 83% |
| 10–20 % | 135 | 8% |
| 20–50 % | 65 | 4% |
| 50–100 % | 35 | 2% |
| > 100 % | 61 | 3% |
| missing (0 in model) | 0 | 0% |

## Largest target flows (by amount, per unit) and their agreement

### kilogram (1469 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Carbon Dioxide (fossil) [Emissions/Emissions to air] (kilogram) | 12.5 | 12.2 | -2.0% | +0.249 |
| Carbon Dioxide (fossil) [Emissions/Emissions to air] (kilogram) | 8.05 | 7.76 | -3.6% | +0.29 |
| Iron [Resources/Resources from ground] (kilogram) | 7.44 | 7.31 | -1.8% | +0.131 |
| Gravel [soil] (kilogram) | 7.25 | 7.19 | -0.9% | +0.0644 |
| Carbon Dioxide (fossil) [Emissions/Emissions to air] (kilogram) | 2.63 | 2.72 | +3.6% | -0.0954 |
| Calcite [resources/in ground] (kilogram) | 2 | 1.95 | -2.8% | +0.0566 |
| Waste mass, total, placed in landfill [resources/in ground] (kilogram) | 1.56 | 1.55 | -0.5% | +0.00755 |
| Carbon Dioxide (biogenic) [Emissions/Emissions to air] (kilogram) | 1.29 | 1.24 | -3.5% | +0.0455 |
| Dolomite [soil] (kilogram) | 1.16 | 1.14 | -1.8% | +0.0206 |
| carbon dioxide (biogenic) [Resources/Resources from air] (kilogram) | 0.755 | 0.67 | -11.2% | +0.0849 |
| Zinc [Resources/Resources from ground] (kilogram) | 0.691 | 0.692 | +0.1% | -0.00102 |
| Sulfate [emissions to water/groundwater, long-term] (kilogram) | 0.667 | 0.691 | +3.7% | -0.0248 |
| Platinum [air] (kilogram) | 0.663 | 0.587 | -11.5% | +0.0761 |
| Sodium chloride [resources/in ground] (kilogram) | 0.572 | 0.527 | -7.8% | +0.0446 |
| calcium [Emissions/Emissions to water] (kilogram) | 0.422 | 0.426 | +0.8% | -0.00325 |
| Chemically polluted water [emissions to water/river] (kilogram) | 0.339 | 0.336 | -1.1% | +0.00359 |
| Carbon Monoxide (fossil) [Emissions/Emissions to air] (kilogram) | 0.317 | 0.311 | -1.8% | +0.0056 |
| Clay [soil] (kilogram) | 0.23 | 0.225 | -2.2% | +0.00505 |
| Magnesite [soil] (kilogram) | 0.202 | 0.202 | -0.1% | +0.000101 |
| Carbon Dioxide (biogenic) [Emissions/Emissions to air] (kilogram) | 0.195 | 0.168 | -13.8% | +0.0268 |

### kilo Becquerel (171 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Radon-222 [Emissions/Emissions to air] (kilo Becquerel) | 3.73e+03 | 3.8e+03 | +1.8% | -68.3 |
| Noble Gases, Radioactive, Unspecified [air] (kilo Becquerel) | 1.33e+03 | 1.38e+03 | +4.2% | -55.9 |
| Hydrogen-3 [Emissions/Emissions to water] (kilo Becquerel) | 53.4 | 55.7 | +4.2% | -2.25 |
| Radon-222 [Emissions/Emissions to air] (kilo Becquerel) | 34.4 | 35.1 | +1.9% | -0.658 |
| Hydrogen-3 [Emissions/Emissions to water] (kilo Becquerel) | 17.8 | 17.8 | +0.1% | -0.0197 |

### square meter (50 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| To Arable, Non-irrigated, Intensive [Land use/Land transformation] (square meter) | 0.0423 | 0.0401 | -5.2% | +0.00221 |
| From Arable, Non-irrigated, Intensive [Land use/Land transformation] (square meter) | 0.03 | 0.0284 | -5.2% | +0.00157 |
| To Arable, Non-irrigated [Land use/Land transformation] (square meter) | 0.0175 | 0.0165 | -5.7% | +0.000993 |
| From Arable, Non-irrigated [Land use/Land transformation] (square meter) | 0.0166 | 0.0157 | -5.7% | +0.000952 |
| From Pasture/meadow [Land use/Land transformation] (square meter) | 0.013 | 0.0122 | -5.7% | +0.000739 |

### megajoule (28 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Waste Heat [air] (megajoule) | 169 | 155 | -8.4% | +14.2 |
| Natural Gas [Resources/Resources from ground] (megajoule) | 87.8 | 86.7 | -1.3% | +1.11 |
| Waste Heat [air] (megajoule) | 67 | 68.7 | +2.7% | -1.79 |
| Hard Coal [Resources/Resources from ground] (megajoule) | 54.2 | 54.9 | +1.2% | -0.667 |
| Uranium [Resources/Resources from ground] (megajoule) | 50.6 | 51.5 | +1.8% | -0.924 |

### square meter-year (27 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Forest, Intensive [Land use/Land occupation] (square meter-year) | 0.761 | 0.68 | -10.6% | +0.0806 |
| Forest [Land use/Land occupation] (square meter-year) | 0.182 | 0.175 | -3.9% | +0.00707 |
| Industrial Area [Land use/Land occupation] (square meter-year) | 0.176 | 0.174 | -1.5% | +0.0026 |
| Traffic Area, Road Network [Land use/Land occupation] (square meter-year) | 0.071 | 0.0704 | -1.0% | +0.000687 |
| Water Bodies [land use] (square meter-year) | 0.0524 | 0.0457 | -12.9% | +0.00674 |

### cubic meter (23 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Water [Emissions/Emissions to water] (cubic meter) | 69 | 69.4 | +0.5% | -0.312 |
| Water to turbine [Resources/Resources from water] (cubic meter) | 68.2 | 68.6 | +0.6% | -0.384 |
| Water, salt, ocean [resources/in water] (cubic meter) | 6.8 | 6.71 | -1.3% | +0.0916 |
| Water [water] (cubic meter) | 6.79 | 6.7 | -1.4% | +0.0919 |
| Water To Cooling [Resources/Resources from water] (cubic meter) | 0.65 | 0.578 | -11.1% | +0.0722 |

### Becquerel (9 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Uranium alpha [emissions to water/river] (Becquerel) | -1.13e-18 | -1.69e-18 | +50.0% | +5.64e-19 |
| Uranium alpha [emissions to water/lake] (Becquerel) | -5.28e-19 | -7.92e-19 | +50.0% | +2.64e-19 |
| Uranium alpha [emissions to air/low. pop.] (Becquerel) | -9.6e-20 | -1.44e-19 | +50.0% | +4.8e-20 |
| Thorium-232 [emissions to water/river] (Becquerel) | -1.14e-21 | -1.71e-21 | +50.0% | +5.7e-22 |
| Thorium-232 [emissions to air/low. pop.] (Becquerel) | -3.37e-22 | -5.06e-22 | +50.0% | +1.69e-22 |

### kilometer (2 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Noise, road, lorry, average [non material emissions/unspecified] (kilometer) | 0.793 | 0.775 | -2.3% | +0.0181 |
| Noise, road, passenger car, average [non material emissions/unspecified] (kilometer) | 0.00642 | 0.00625 | -2.5% | +0.000163 |

### ton kilometer (2 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Noise, rail, freight train [non material emissions/unspecified] (ton kilometer) | 18.8 | 18.8 | -0.1% | +0.024 |
| Noise, aircraft, freight [non material emissions/unspecified] (ton kilometer) | 4.72e-05 | 4.47e-05 | -5.2% | +2.47e-06 |

### meter (2 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Noise, road, lorry, average [non material emissions/unspecified] (meter) | -1.4e-16 | -1.42e-16 | +1.7% | +2.34e-18 |
| Noise, road, passenger car, average [non material emissions/unspecified] (meter) | -1.07e-19 | -1.6e-19 | +50.0% | +5.33e-20 |

### cubic meter-year (1 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Volume Occupied, Reservoir [land use] (cubic meter-year) | 0.61 | 0.61 | +0.0% | -1.01e-05 |

### person kilometer (1 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Noise, aircraft, passenger [non material emissions/unspecified] (person kilometer) | 0.00148 | 0.00146 | -1.4% | +2e-05 |

## Worst deviations among the 50 largest kilogram flows

| flow | target | explicit | Δ |
|---|---|---|---|
| Carbon Dioxide (biogenic) [Emissions/Emissions to air] (kilogram) | 0.195 | 0.168 | -13.8% |
| Platinum [air] (kilogram) | 0.663 | 0.587 | -11.5% |
| carbon dioxide (biogenic) [Resources/Resources from air] (kilogram) | 0.755 | 0.67 | -11.2% |
| BOD5, Biological Oxygen Demand [emissions to water/groundwater, long-term] (kilogram) | 0.0253 | 0.0227 | -10.0% |
| Sodium chloride [resources/in ground] (kilogram) | 0.572 | 0.527 | -7.8% |
| DOC, Dissolved Organic Carbon [emissions to water/groundwater, long-term] (kilogram) | 0.0301 | 0.0285 | -5.5% |
| TOC, Total Organic Carbon [emissions to water/groundwater, long-term] (kilogram) | 0.0301 | 0.0285 | -5.5% |
| COD, Chemical Oxygen Demand [emissions to water/groundwater, long-term] (kilogram) | 0.0747 | 0.0707 | -5.4% |
| Carbon Dioxide (biogenic) [Emissions/Emissions to air] (kilogram) | 0.052 | 0.0494 | -5.1% |
| Phosphate [Emissions/Emissions to water] (kilogram) | 0.0217 | 0.0227 | +4.2% |

## Structural checks

- ✓ 14 explicit input(s) over 1 node(s)
- ✓ no decomposed grid mixes
- ✓ no dependency on another aggregated dataset
- ✓ mass in: 28 kg technosphere + 0 kg resources per 1 m2 product (informational)
- ✓ all inputs resolved

residual: 1437 flows under-explained, 348 over-explained (negative residual)

## Evidence

- 2014 - LCA data ventilation and heating systems - Klingler.pdf — pages 117-119 -> report-p117-119.txt report sha256 f4692d86e964f922…, text sha256 fbda9f888ca9fd8e…
