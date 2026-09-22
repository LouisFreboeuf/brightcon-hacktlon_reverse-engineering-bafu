# Check: xx Packaging glass, brown, at plant (ddefdbda-3a45-39fc-84ad-17c4c7bdc3f9)

target `bafu-2026` vs explicit model `ddefdbda-3a45-39fc-84ad-17c4c7bdc3f9-disagg` and hybrid `ddefdbda-3a45-39fc-84ad-17c4c7bdc3f9-hybrid`

**Strategy:** S2 — template transfer from a BAFU unit process of the same product; main amounts calibrated within 0.5-2x. BAFU ships the Swiss brown packaging glass as an aggregated xx dataset, but keeps the same product as a RER unit process (21 inputs). That structure is reused with the grid switched to CH (the datasets describe Vetropack's Swiss sites); ten amounts free within 0.5-2x.
**Calibrated inputs:** Dolomite, at plant [0.0294–0.118], Natural gas, high pressure, at consumer [1.78–7.14], Silica sand, at plant [0.143–0.574], Heavy fuel oil, at regional storage [0.0216–0.0866], Limestone, milled, loose, at plant [0.0209–0.0838], Light fuel oil, at regional storage [0.0209–0.0838], Soda, powder, at plant [0.043–0.172], Glass, from public collection, unsorted [0.278–1.11], Electricity, medium voltage, at grid [0.122–0.488]
**Links to rebuilt nodes:** none

## Flow agreement (explicit vs target, per elementary flow)

- the 50 largest kilogram flows: 3/50 within ±10 %, median |Δ| 62.6%
- kilogram mass covered within ±10 %: 0.1% of the target's total kg mass
- all 1146 flows of the target: 51 within ±10 % (4%), median |Δ| 127.7%, 0 missing from the model, 631 extra
- hybrid vs target: 1 flows differ

| \|Δ\| bucket | flows | share of target flows |
|---|---|---|
| ≤ 10 % | 51 | 4% |
| 10–20 % | 53 | 5% |
| 20–50 % | 142 | 12% |
| 50–100 % | 285 | 25% |
| > 100 % | 615 | 54% |
| missing (0 in model) | 0 | 0% |

## Largest target flows (by amount, per unit) and their agreement

### kilogram (922 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Gravel [soil] (kilogram) | 0.622 | 0.278 | -55.3% | +0.344 |
| Carbon Dioxide (fossil) [Emissions/Emissions to air] (kilogram) | 0.505 | 0.0904 | -82.1% | +0.415 |
| Calcite [resources/in ground] (kilogram) | 0.129 | 0.054 | -58.2% | +0.0754 |
| Dolomite [soil] (kilogram) | 0.103 | 0.03 | -70.9% | +0.073 |
| Carbon Dioxide (fossil) [Emissions/Emissions to air] (kilogram) | 0.099 | 0.0371 | -62.5% | +0.0619 |
| Sodium chloride [resources/in ground] (kilogram) | 0.0717 | 0.0288 | -59.8% | +0.0429 |
| carbon dioxide (biogenic) [Resources/Resources from air] (kilogram) | 0.068 | 0.123 | +81.4% | -0.0553 |
| Carbon Dioxide (fossil) [Emissions/Emissions to air] (kilogram) | 0.0384 | 0.543 | +1311.5% | -0.504 |
| Carbon Dioxide (biogenic) [Emissions/Emissions to air] (kilogram) | 0.0241 | 0.0531 | +120.9% | -0.0291 |
| Clay [soil] (kilogram) | 0.02 | 0.0352 | +76.0% | -0.0152 |
| Chloride [Emissions/Emissions to water] (kilogram) | 0.0125 | 0.00623 | -50.1% | +0.00626 |
| Sulfate [emissions to water/groundwater, long-term] (kilogram) | 0.00973 | 0.00537 | -44.8% | +0.00436 |
| Iron [Resources/Resources from ground] (kilogram) | 0.00599 | 0.00417 | -30.5% | +0.00183 |
| Calcium [Emissions/Emissions to water] (kilogram) | 0.00479 | 0.00178 | -62.8% | +0.00301 |
| Solids, Inorganic [water] (kilogram) | 0.0047 | 0.00156 | -66.8% | +0.00314 |
| calcium [Emissions/Emissions to water] (kilogram) | 0.0029 | 0.00821 | +183.2% | -0.00531 |
| Nitrogen Oxides [Emissions/Emissions to air] (kilogram) | 0.00253 | 0.000212 | -91.6% | +0.00232 |
| Silicon [Emissions/Emissions to water] (kilogram) | 0.00231 | 0.00148 | -35.6% | +0.000821 |
| Methane (fossil) [Emissions/Emissions to air] (kilogram) | 0.00158 | 0.000327 | -79.2% | +0.00125 |
| magnesium [Emissions/Emissions to water] (kilogram) | 0.00137 | 0.0009 | -34.3% | +0.000471 |

### kilo Becquerel (135 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Radon-222 [Emissions/Emissions to air] (kilo Becquerel) | 28.6 | 76.6 | +167.8% | -48 |
| Noble Gases, Radioactive, Unspecified [air] (kilo Becquerel) | 13.2 | 26.1 | +98.1% | -12.9 |
| Radon-222 [Emissions/Emissions to air] (kilo Becquerel) | 0.684 | 0.732 | +7.0% | -0.048 |
| Hydrogen-3 [Emissions/Emissions to water] (kilo Becquerel) | 0.53 | 1.05 | +98.2% | -0.521 |
| Hydrogen-3 [Emissions/Emissions to water] (kilo Becquerel) | 0.0633 | 6.04 | +9447.9% | -5.98 |

### square meter (34 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| From Forest, Extensive [Land use/Land transformation] (square meter) | 0.00102 | 1.01e-06 | -99.9% | +0.00102 |
| To Forest, Intensive [Land use/Land transformation] (square meter) | 0.00101 | 0.00224 | +122.5% | -0.00123 |
| To Arable, Non-irrigated [Land use/Land transformation] (square meter) | 0.000289 | 0.00118 | +309.5% | -0.000895 |
| From Arable, Non-irrigated [Land use/Land transformation] (square meter) | 0.000289 | 0.00115 | +296.3% | -0.000856 |
| To Mineral Extraction Site [Land use/Land transformation] (square meter) | 8.3e-05 | 3.05e-05 | -63.2% | +5.25e-05 |

### cubic meter (20 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Water [Emissions/Emissions to water] (cubic meter) | 5.18 | 1.63 | -68.5% | +3.55 |
| Water to turbine [Resources/Resources from water] (cubic meter) | 5.17 | 1.62 | -68.6% | +3.55 |
| Water [Resources/Resources from water] (cubic meter) | 0.00571 | 0.00615 | +7.7% | -0.000441 |
| Water To Cooling [Resources/Resources from water] (cubic meter) | 0.00487 | 0.00392 | -19.6% | +0.000955 |
| river water [Resources/Resources from water] (cubic meter) | 0.000633 | 0.000865 | +36.7% | -0.000232 |

### megajoule (20 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Waste Heat [air] (megajoule) | 10.2 | 5.1 | -50.0% | +5.1 |
| Natural Gas [Resources/Resources from ground] (megajoule) | 8.11 | 3.16 | -61.0% | +4.95 |
| Crude Oil [Resources/Resources from ground] (megajoule) | 1.11 | 3.56 | +219.9% | -2.45 |
| Waste Heat [air] (megajoule) | 1.04 | 0.923 | -11.1% | +0.115 |
| Hard Coal [Resources/Resources from ground] (megajoule) | 0.95 | 0.24 | -74.7% | +0.709 |

### square meter-year (14 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Forest, Intensive [Land use/Land occupation] (square meter-year) | 0.132 | 0.215 | +62.8% | -0.0829 |
| Industrial Area [Land use/Land occupation] (square meter-year) | 0.00195 | 0.00217 | +11.1% | -0.000216 |
| Traffic Area, Rail/road Embankment [Land use/Land occupation] (square meter-year) | 0.00174 | 0.00278 | +60.1% | -0.00104 |
| Inland Water Bodies [land use] (square meter-year) | 0.000546 | 0.000162 | -70.4% | +0.000384 |
| Dump Site [Land use/Land occupation] (square meter-year) | 0.000448 | 0.000231 | -48.5% | +0.000217 |

### cubic meter-year (1 flows)

| flow | target | explicit | Δ | residual |
|---|---|---|---|---|
| Volume Occupied, Reservoir [land use] (cubic meter-year) | 0.00756 | 0.00818 | +8.2% | -0.000622 |

## Worst deviations among the 50 largest kilogram flows

| flow | target | explicit | Δ |
|---|---|---|---|
| Carbon Dioxide (fossil) [Emissions/Emissions to air] (kilogram) | 0.0384 | 0.543 | +1311.5% |
| Fluorspar [soil] (kilogram) | 0.00021 | 0.00243 | +1055.8% |
| Carbon Dioxide (biogenic) [Emissions/Emissions to air] (kilogram) | 0.000307 | 0.00262 | +752.6% |
| Kaolinite [soil] (kilogram) | 0.000441 | 0.00145 | +228.5% |
| Sodium [water] (kilogram) | 0.000311 | 0.000943 | +202.9% |
| calcium [Emissions/Emissions to water] (kilogram) | 0.0029 | 0.00821 | +183.2% |
| Barite [resources/in ground] (kilogram) | 0.000319 | 0.000747 | +134.0% |
| Carbon Dioxide (biogenic) [Emissions/Emissions to air] (kilogram) | 0.0241 | 0.0531 | +120.9% |
| Metamorphous rock, graphite containing [resources/in ground] (kilogram) | 0.00104 | 2.41e-07 | -100.0% |
| Nitrogen Oxides [Emissions/Emissions to air] (kilogram) | 0.00253 | 0.000212 | -91.6% |

## Structural checks

- ✓ 21 explicit input(s) over 1 node(s)
- ✓ no decomposed grid mixes
- ✗ depends on aggregated datasets (rebuild those first): ['Polyethylene, HDPE, granulate, at plant', 'Feldspar, at plant']
- ✓ mass in: 0.763 kg technosphere + 0 kg resources per 1 kilogram product (informational)
- ✓ all inputs resolved

residual: 426 flows under-explained, 1351 over-explained (negative residual)

## Evidence

- bafu-2026: xx Packaging glass, brown, at plant [RER] (unit process, 21 inputs) — template transfer (S2) Same product and reference unit; grid electricity switched to CH.
- 2007 - LCI packagings and graphical papers - Hischier.pdf — packaging glass The bundled report is a 17-page overview and prints no inventory table, so the sibling unit process is the only evidence.
