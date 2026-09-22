You are helping rebuild an aggregated life-cycle-inventory dataset as a unit process.

The dataset `CEM II, B-LL cement, at plant` [CH], reference unit 1 kg, is shipped in the BAFU-2026 database as a "system terminated" inventory: it has no technosphere inputs, only ~11 cumulative elementary flows. A public report documents the underlying process. Your job is to read the report excerpt and produce the *unit process* as line items — what the process consumes from other datasets and what it emits directly — each traceable to the excerpt.

## What the database says about the dataset

- BAFU category: construction materials / binder
- includedProcesses: The activity starts with the clinker in the silo to be used for cement production and with the additional ingredients of the cement at the gate of the cement plant. The activity includes also the electricy used for the grinding of the clinker, griding aids, heat for the drying of additions etc. and ends with the cement produced in the cement mill. The dataset does not include packaging and administration.
- technology: Industry data. Data approximates average swiss production
- generalComment: The dataset describes the production of cement (CEM II/B-LL) in Switzerland and was derived from the CEM II/B CH-Mix adapting the following three inputs: •         burnt shale share to 0\n•        clinker share CEM II/B-LL to 71 %  (average of Norm 72 %, and producer)\n•    increase limestone (0.269) up to 1 kg product\nTechnology: Industry data. Data approximates average swiss production\nTime period: Time of publications.\nVersion: 1\nEnergy values: Undefined\nLocal category: Mineralische Baustoffe\nLocal subcategory: Bindemittel\nUVEK 2022 source file:551-Zement-Klinker_v0.13_UVEK2021._CEM II.xml\n\n
UUID: 0884c269-5b53-330c-9fdd-e085230f9768
- source cited in the metadata: Tschuemperlin L. | 2020 | 2020 - LCA selected types of concrete - Tschuemperlin
- time period: 2015-01-2015-12

## Direct resource flows visible in the aggregated vector

These flows appear in the aggregated inventory with amounts that no upstream dataset would plausibly emit on this dataset's behalf; they are candidates for the process's own direct resource flows (per 1 kg):
- none

## Report excerpt

Source file: `report-p24-25.txt` (SHA-256 38b024cef9f732127dab4cffe4b3d60de4d19324ef9e5f22f8805ff99c2e5f4f), pages 24-25 of `2020 - LCA selected types of concrete - Tschuemperlin.pdf`.

```
Sachbilanzdaten und Modellierungsannahmen                                                            20




tiven Bandbreite des Klinkeranteils im Zementtype CEM II/B-LL abgeleitet. Laut Norm
SN EN 197-1 setzt sich der CEM II/B-LL Zement aus 65-79 % Portlandklinker zusam-
men. Der CEM II/B-LL Zement von Vigier enthält weniger als 70 %6 Klinker und der
Klinkeranteil im CEM II/B-LL von Jura Cement liegt innerhalb der normativen Band-
breite von 65 – 79 % Klinker7. Der Klinkeranteil des zu bilanzierenden CEM II/B-LL
Zements wird auf 71 % gesetzt, was dem Mittelwert der maximalen Klinkeranteile von
Vigier und der Norm SN EN 197-1 entspricht. Da sich gemäss Norm SN EN 197-1 der
Kalksteingehalt zwischen 21 % und 35 % bewegt, wurde die Differenz zu einem kg
CEM II/B-LL Zement noch mit Kalkstein aufgefüllt. Die Transportaufwände reduzieren
sich aufgrund des wegfallenden Imports des gebrannten Ölschiefers aus Deutschland.
Alle weiteren Aufwendungen werden vom CEM II/B CH-Mix Datensatz übernommen.
CEM II/B CH-Mix Zement enthält gebrannten Ölschiefer (siehe Beschreibung in Un-
terkapitel 3.6). Die Umweltkennwerte dieses Zements wurden mit den Sachbilanzdaten
von gebranntem Ölschiefer gemäss den beiden Allokationsansätzen ermittelt (siehe An-
hang A).




6
    http://www.vigier-ciment.ch/produkte/zemente/vigier-cem-iib-ll-325-r/, abgerufen am 26.10.2016
7
    http://www.juracement.ch/data/docs/download/8112/de/juraEco-broschuere.pdf, abgerufen am
    26.10.2016




Ökobilanz ausgewählter Betonsorten                                                           treeze Ltd.
Sachbilanzdaten und Modellierungsannahmen                                                                                                                                                                                     21




Tab. 3.13: Sachbilanzen von 1 kg CEM II/B CH-Mix, CEM II/B-LL und CEM II/A Zement, ab Werk




                                                                                                                                                                              StandardDeviation95%
                                                                               InfrastructureProcess




                                                                                                                                                           UncertaintyType
                                                                    Location
                                                                                                               CEM II/B CH-     CEM II/B-LL    CEM II/A




                                                                                                        Unit
                                           Name                                                                Mix cement, at   cement, at    cement, at                                             GeneralComment
                                                                                                                    plant         plant         plant



                                        Location                                                                    CH             CH            CH
                                InfrastructureProcess                                                                0              0             0
                                          Unit                                                                      kg             kg            kg
product         CEM II/B CH-Mix cement, at plant                    CH            0                     kg           1               0             0
product         CEM II/B-LL cement, at plant                        CH            0                     kg           0               1             0
product         CEM II/A cement, at plant                           CH            0                     kg           0               0             1
                                                                                                                                                                                  (1,1,1,1,1,1,BU:3); ; basiert auf
technosphere    cement plant                                        CH            1                    unit      2.73E-11        2.73E-11     2.73E-11       1               3.00
                                                                                                                                                                                  ecoinvent 3.2 Datensatz
                                                                                                                                                                                  (2,1,1,1,3,5,BU:1.05); ; basiert auf
                clinker (data from ecoinvent v3.2), at plant        CH            0                     kg        6.88E-1        7.10E-1       7.88E-1       1               1.31
                                                                                                                                                                                  ecoinvent 3.2 Datensatz
                                                                                                                                                                                  (1,3,3,3,1,1,BU:1.05); ; basiert auf
                burnt shale, at plant                               DE            0                     kg        1.36E-1                                    1               1.31
                                                                                                                                                                                  ecoinvent 3.2 Datensatz
                ground granulated blast furnace slag, no                                                                                                                          (1,3,3,3,1,1,BU:1.05); ; basiert auf
                                                                    RER           0                     kg                                     1.80E-3       1               1.31
                burdens, at plant                                                                                                                                                 ecoinvent 3.2 Datensatz
                                                                                                                                                                                  (2,1,1,1,3,5,BU:1.05); ; basiert auf
                electricity, medium voltage, at grid                CH            0                    kWh        3.42E-2        3.42E-2       3.13E-2       1               1.31
                                                                                                                                                                                  ecoinvent 3.2 Datensatz
                                                                                                                                                                                  (1,3,3,3,1,1,BU:1.05); ; basiert auf
                ethylene glycol, at plant                           RER           0                     kg        2.10E-4        2.10E-4       2.12E-4       1               1.13
                                                                                                                                                                                  ecoinvent 3.2 Datensatz
                                                                                                                                                                                  (4,5,na,na,na,na,BU:1.05); ; basiert
                gypsum, mineral, at mine                            CH            0                     kg        2.11E-2        2.11E-2       4.64E-2       1               1.30
                                                                                                                                                                                  auf ecoinvent 3.2 Datensatz
                                                                                                                                                                                  (2,1,1,1,1,5,BU:1.05); ; basiert auf
air, unspecified Heat, waste                                         -               -                  MJ        1.23E-1        1.23E-1       1.13E-1       1               1.22
                                                                                                                                                                                  ecoinvent 3.2 Datensatz
                                                                                                                                                                                  (2,1,1,1,1,5,BU:1.05); ; basiert auf
technosphere    steel, low-alloyed, at plant                        RER           0                     kg        4.00E-5        4.00E-5       4.04E-5       1               1.22
                                                                                                                                                                                  ecoinvent 3.2 Datensatz
                heavy fuel oil, burned in industrial furnace 1MW,                                                                                                                 (2,1,1,1,1,5,BU:1.05); ; basiert auf
                                                                    RER           0                     MJ                                     1.21E-3       1               1.22
                non-modulating                                                                                                                                                    ecoinvent 3.2 Datensatz
                                                                                                                                                                                  (2,1,1,1,1,5,BU:1.05); ; basiert auf
                limestone, crushed, for mill                        CH            0                     kg        1.51E-1        2.69E-1       1.61E-1       1               1.22
                                                                                                                                                                                  ecoinvent 3.2 Datensatz
                                                                                                                                                                                  (2,1,1,1,1,5,BU:2); hinzugefügt, da in
                transport, lorry 20-28t, fleet average              CH            0                    tkm        4.44E-2        2.00E-2       2.00E-2       1               2.05
                                                                                                                                                                                  ecoinvent v3.2 nicht berücksichtigt;
                                                                                                                                                                                  (2,1,1,1,1,5,BU:2); hinzugefügt, da in
                transport, freight, rail                            RER           0                    tkm        1.50E-4        1.50E-4       1.23E-3       1               2.05
                                                                                                                                                                                  ecoinvent v3.2 nicht berücksichtigt;



3.10 Herstellung von Zement ZN/D
Zement ZN/D setzt sich hauptsächlich aus Klinker, Mischgranulat und gebranntem Öl-
schiefer zusammen (Werner 2018). Die Tab. 3.14 dargestellte Sachbilanz stammt aus
Werner (2018) und addiert sich zu 1.00 kg Zement.
Tab. 3.14: Sachbilanz von 1kg Zement ZN/D, ab Werk

Inputs                                                                                                 Einheit                           Menge
Klinker                                                                                                %                                 40%-70%
Gips, mineralisch                                                                                      %                                  < 10%
Mischgranulat (MG)                                                                                     %                                 15%-30%
Schiefer, gebrannt                                                                                     %                                 15%-30%
Eisen-II Sulfat                                                                                        %                                    < 1%
Filterstaub / Kalkstein                                                                                %                                  < 10%
Ethylenglykol als Mahlhilfe                                                                            kg/kg                             5.50E-04
Strom, Mittelspannung                                                                                  kWh/kg                            4.97E-02
Schweröl zur Wärmeerzeugung                                                                            MJ/kg                             1.62E-01
Zementfabrik, Infrastruktur                                                                            p/kg                              5.36E-11
Stahl für Mahlwerk, niedrig legiert                                                                    kg/kg                             1.10E-04
Transport LKW                                                                                          tkm/kg                            8.37E-03
Transport Bahn                                                                                         tkm/kg                            4.28E-02


Ökobilanz ausgewählter Betonsorten                                                                                                                                                                                    treeze Ltd.
```

## Rules

1. Every line item must quote the exact line of the excerpt it comes from (`quote`), with the raw value and raw unit as printed. Never invent a value. If the excerpt gives a range, report the range as `raw_min`/`raw_max` and put your point estimate in `raw_value`.
2. Report values per the excerpt's own basis (`per`, e.g. "per t burnt shale", "per m2 board"); do not convert. State the reference basis you found in `basis` so the code can scale to 1 kg.
3. If a value needs a physical conversion (litres of diesel to MJ, m3 of water to kg), give `factor`, `factor_unit` and `factor_source` (a standard value with its source, e.g. "diesel 0.84 kg/l × 42.8 MJ/kg = 36 MJ/l, ecoinvent convention"). Leave `factor` at 1 otherwise.
4. Classify each line: `kind` = "input" (a product or service from another dataset), "emission" (a direct release to air/water/soil), "resource" (a direct extraction from nature), "product" (the reference product), "co-product" or "ignore" (with a reason).
5. Propose a `search` phrase (2–4 words) that a name search in a life-cycle database would use: for inputs the supplying dataset in ecoinvent-2 naming style ("diesel burned building machine", "sodium hydroxide production mix"); for emissions and resources the substance in EF 3.1 / ecoinvent nomenclature ("particles PM10" for dust, "nitrogen oxides", "carbon dioxide fossil", "crude oil", "water"). Do not guess the exact name; the search is resolved by code afterwards.
6. If the excerpt describes allocation (e.g. an economic allocation between co-products), record it in `allocation` and use the allocated column when the table has one. If it states that the composition items add up to a mass ("adds up to 1.00 kg"), put that mass per basis in `mass_sum`, else null.
7. Mark anything you are unsure about with `confidence` = "low" and say why in `note`. Do not omit uncertain items; the reviewer decides.
8. Do not add inputs the excerpt does not mention, even if you know the process needs them. Missing items are reported in `gaps` instead.

Return only the JSON object described by the schema.
