# Check: Burnt shale, at plant (d8ec4be3-c410-3806-98f5-a2ec5a284fee)

target `bafu-2026` vs explicit model `d8ec4be3-c410-3806-98f5-a2ec5a284fee-disagg` and hybrid `d8ec4be3-c410-3806-98f5-a2ec5a284fee-hybrid`

## Scores (EF 3.1)

| category | target | explicit | Δ explicit | residual share | hybrid/target |
|---|---|---|---|---|---|
| Acidification | 0.001025 | 0.001059 | +3.3% | -3.3% | 1.000000 |
| Climate change | 0.4291 | 0.454 | +5.8% | -5.8% | 1.000000 |
| Climate change-Biogenic | 4.14e-06 | 0.0004087 | +9772.1% | -9772.1% | 0.999999 |
| Climate change-Fossil | 0.4291 | 0.4536 | +5.7% | -5.7% | 1.000000 |
| Climate change-Land use and land use change | 2.502e-06 | 1.059e-05 | +323.3% | -323.3% | 1.000000 |
| EF-particulate Matter | 4.749e-09 | 5.022e-09 | +5.7% | -5.7% | 1.000000 |
| Ecotoxicity, freshwater | 0.153 | 0.1199 | -21.6% | +21.6% | 1.000000 |
| Ecotoxicity, freshwater_inorganics | 0.1481 | 0.119 | -19.7% | +19.7% | 1.000000 |
| Ecotoxicity, freshwater_organics | 0.004871 | 0.0009662 | -80.2% | +80.2% | 1.000001 |
| Eutrophication marine | 0.000209 | 0.0002311 | +10.6% | -10.6% | 1.000000 |
| Eutrophication, freshwater | 1.098e-06 | 3.278e-05 | +2886.3% | -2886.3% | 1.000001 |
| Eutrophication, terrestrial | 0.00228 | 0.002518 | +10.4% | -10.4% | 1.000000 |
| Human toxicity, cancer | 2.342e-12 | 3.322e-11 | +1318.3% | -1318.3% | 1.010190 |
| Human toxicity, cancer_inorganics | 1.542e-12 | 4.018e-12 | +160.7% | -160.7% | 1.000000 |
| Human toxicity, cancer_organics | 8.003e-13 | 2.92e-11 | +3548.2% | -3548.2% | 1.029819 |
| Human toxicity, non-cancer | 6.432e-11 | 1.612e-10 | +150.7% | -150.7% | 1.000000 |
| Human toxicity, non-cancer_inorganics | 5.527e-11 | 1.492e-10 | +170.0% | -170.0% | 1.000000 |
| Human toxicity, non-cancer_organics | 9.044e-12 | 1.2e-11 | +32.7% | -32.7% | 1.000000 |
| Ionising radiation, human health | 0.000719 | 0.005136 | +614.3% | -614.3% | 1.000000 |
| Land use | 0.03701 | 0.1343 | +262.8% | -262.8% | 1.000000 |
| Ozone depletion | 4.009e-10 | 5.54e-10 | +38.2% | -38.2% | 1.000003 |
| Photochemical ozone formation - human health | 0.0006214 | 0.0006568 | +5.7% | -5.7% | 1.000000 |
| Resource use, fossils | 3.965 | 4.029 | +1.6% | -1.6% | 1.000000 |
| Resource use, minerals and metals | 9.929e-09 | 3.513e-08 | +253.8% | -253.8% | 1.000000 |
| Water use | 0.002471 | 0.009306 | +276.7% | -276.7% | 0.999930 |

## Flow diff — worst categories, flows driving the gap (explicit − target, characterised)

### Climate change-Biogenic (Δ +9772.1%)

| flow | target | explicit | Δ impact | share of target score |
|---|---|---|---|---|
| Methane (biogenic) [Emissions/Emissions to air] (kilogram) | 4.29e-08 | 1.1e-05 | +0.000296 | +7140.4% |
| Methane (biogenic) [Emissions/Emissions to air] (kilogram) | 1.1e-07 | 4.14e-06 | +0.000109 | +2630.7% |
| Methane (biogenic) [Emissions/Emissions to air] (kilogram) | 1.85e-10 | 1.67e-09 | +4.02e-08 | +1.0% |

### Human toxicity, cancer_organics (Δ +3548.2%)

| flow | target | explicit | Δ impact | share of target score |
|---|---|---|---|---|
| Benzo[a]pyrene [Emissions/Emissions to air] (kilogram) | 2.33e-11 | 6.47e-09 | +2.34e-11 | +2928.3% |
| Formaldehyde [Emissions/Emissions to air] (kilogram) | 4.64e-09 | 1.87e-07 | +4.6e-12 | +575.3% |
| Benzene [Emissions/Emissions to air] (kilogram) | 6.51e-09 | 9.2e-07 | +7.6e-14 | +9.5% |
| 2,3,7,8-tetrachlorodibenzo-p-dioxin [Emissions/Emissions to air] (kilogram) | 1.27e-15 | 3.37e-15 | +7.37e-14 | +9.2% |
| Benzo[a]pyrene [Emissions/Emissions to air] (kilogram) | 1.94e-13 | 1.18e-11 | +5.23e-14 | +6.5% |
| Formaldehyde [Emissions/Emissions to air] (kilogram) | 3.28e-08 | 3.51e-08 | +2.96e-14 | +3.7% |
| Benzo[a]pyrene [Emissions/Emissions to water] (kilogram) | 0 | 1.63e-11 | +2.95e-14 | +3.7% |
| Pentachlorophenol [Emissions/Emissions to air] (kilogram) | 9.88e-12 | 2.85e-09 | +2.31e-14 | +2.9% |

### Eutrophication, freshwater (Δ +2886.3%)

| flow | target | explicit | Δ impact | share of target score |
|---|---|---|---|---|
| Phosphate [Emissions/Emissions to water] (kilogram) | 2.67e-06 | 8.81e-05 | +2.82e-05 | +2570.1% |
| Phosphate [Emissions/Emissions to water] (kilogram) | 6.46e-07 | 1.12e-05 | +3.47e-06 | +316.3% |
| Phosphorus [Emissions/Emissions to water] (kilogram) | 3.13e-09 | 2.39e-09 | -7.46e-10 | -0.1% |
| Phosphorus [Emissions/Emissions to water] (kilogram) | 1.28e-10 | 5.95e-10 | +4.66e-10 | +0.0% |
| Phosphorus [Emissions/Emissions to soil] (kilogram) | 1.3e-08 | 5.47e-09 | -3.77e-10 | -0.0% |
| Phosphorus [Emissions/Emissions to soil] (kilogram) | 1.4e-11 | 1.48e-11 | +3.87e-14 | +0.0% |
| Phosphorus [Emissions/Emissions to soil] (kilogram) | 0 | 1.22e-13 | +6.09e-15 | +0.0% |
| Phosphate [Emissions/Emissions to soil] (kilogram) | 0 | 4.71e-15 | +7.53e-17 | +0.0% |

### Human toxicity, cancer (Δ +1318.3%)

| flow | target | explicit | Δ impact | share of target score |
|---|---|---|---|---|
| Benzo[a]pyrene [Emissions/Emissions to air] (kilogram) | 2.33e-11 | 6.47e-09 | +2.34e-11 | +1000.7% |
| Formaldehyde [Emissions/Emissions to air] (kilogram) | 4.64e-09 | 1.87e-07 | +4.6e-12 | +196.6% |
| Chromium [Emissions/Emissions to water] (kilogram) | 2.28e-09 | 8.06e-09 | +5.72e-13 | +24.4% |
| Chromium [Emissions/Emissions to air] (kilogram) | 8.94e-09 | 1.64e-08 | +5.66e-13 | +24.2% |
| Mercury [Emissions/Emissions to air] (kilogram) | 9.19e-11 | 4.11e-10 | +3.51e-13 | +15.0% |
| Chromium [Emissions/Emissions to soil] (kilogram) | 2.1e-10 | 7.08e-09 | +3.46e-13 | +14.8% |
| Arsenic [Emissions/Emissions to water] (kilogram) | 4.28e-10 | 1.21e-08 | +2.17e-13 | +9.3% |
| Mercury [Emissions/Emissions to air] (kilogram) | 7.98e-11 | 1.76e-10 | +1.02e-13 | +4.3% |

### Ionising radiation, human health (Δ +614.3%)

| flow | target | explicit | Δ impact | share of target score |
|---|---|---|---|---|
| Radon-222 [Emissions/Emissions to air] (kilo Becquerel) | 0.413 | 3.46 | +0.00347 | +482.5% |
| Carbon-14 [Emissions/Emissions to air] (kilo Becquerel) | 2.24e-05 | 0.000115 | +0.000922 | +128.3% |
| Radon-222 [Emissions/Emissions to air] (kilo Becquerel) | 0.00965 | 0.0319 | +2.54e-05 | +3.5% |
| Radium-226 [Emissions/Emissions to water] (kilo Becquerel) | 0.00198 | 0.000617 | -8.26e-06 | -1.1% |
| Iodine-129 [Emissions/Emissions to air] (kilo Becquerel) | 2.25e-08 | 1.13e-07 | +3.99e-06 | +0.6% |
| Carbon-14 [Emissions/Emissions to air] (kilo Becquerel) | 0 | 1.15e-07 | +1.15e-06 | +0.2% |
| Cesium-137 [Emissions/Emissions to water] (kilo Becquerel) | 1.86e-08 | 1.05e-07 | +6.78e-07 | +0.1% |
| Uranium-234 [Emissions/Emissions to air] (kilo Becquerel) | 5.42e-08 | 1.53e-07 | +4.49e-07 | +0.1% |

## Structural checks

- ✓ 12 explicit input(s) over 1 node(s)
- ✓ no decomposed grid mixes
- ✓ no dependency on another aggregated dataset
- ✓ mass in: 0.568 kg technosphere + 0.963 kg resources per 1 kilogram product (informational)
- ✓ all inputs resolved

residual: 496 flows under-explained, 1295 over-explained (negative residual)

## Evidence

- 2020 - LCA selected types of concrete - Tschuemperlin.pdf — section 3.6, Tab. 3.9 (inventory per t, 71.3 % economic allocation column) and Tab. 3.10 (transport distances) Werner (2013) inventory, allocation electricity 28.7 % / burnt shale 71.3 % per Werner (2018). 1 t burnt shale co-produces 183.8 kWh electricity. Diesel and heating oil converted from litres at 36 MJ/l; per-t values divided by 1000.
- target dataset cumulative vector — direct resource flows unique to this process raw shale (0.9626 kg/kg = ~1.35 kg raw shale x 71.3 %) and the shale's energy content booked as crude-oil resource (3.658 MJ/kg), which no upstream node emits
