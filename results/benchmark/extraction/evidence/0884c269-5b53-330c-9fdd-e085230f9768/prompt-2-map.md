You are mapping line items of a unit process to datasets and elementary flows in the BAFU-2026 life-cycle database.

For each line item below, candidates were found by a keyword search — over the 11,947 dataset names for inputs, over the EF 3.1 elementary-flow list for emissions and resources. Pick the candidate that supplies what the line item consumes (inputs) or names the substance and compartment released or extracted (emissions, resources), or say that none fits. Rules:

1. Prefer the dataset that matches the substance, the physical form and the technology stated in the line item (e.g. "50% in H2O, production mix" for an unspecified caustic soda; "at plant" for a purchased chemical; "burned in industrial furnace" for a fuel that is combusted on site rather than delivered).
2. Prefer a *unit process* over a candidate marked `aggregated` (those are themselves sealed inventories); if only an aggregated candidate fits, choose it and set `dependency` = true.
3. Location: prefer the process's own location (CH), then RER/Europe, then CH, then GLO. If the candidate list shows several locations, name the one you choose.
4. Never map a chemical to a similarly spelled different chemical. If no candidate is the right substance, set `chosen` to null and explain in `reason`; the code will report the line as missing.
5. For emissions and resources, choose the flow whose substance matches and whose compartment is the one stated (air / water / soil / resources); prefer the 'unspecified' sub-compartment unless the excerpt says otherwise; copy the compartment string into `compartment`. Geogenic (carbonate) CO2 is characterised as fossil CO2 in EF 3.1.
6. `reason` must say why the chosen candidate beats the runner-up, in one sentence.

Line items and their candidates:

- item: Cement plant (infrastructure)  (input)
  quote: technosphere    cement plant                                        CH            1                    unit      2.73E-11        2.73E-11     2.73E-11       1               3.00
  search: cement plant
  candidates:
    - Cement plant [CH] (unit, 4 inputs)
    - CEM I cement, at plant [CH] (kilogram, 10 inputs)
    - Cement ZN, D, at plant [CH] (kilogram, 0 inputs, aggregated)
    - White cement, at plant [CH] (kilogram, 32 inputs)
    - Cement mortar, at plant [CH] (kilogram, 8 inputs)
    - Cement plaster, at plant [CH] (kilogram, 12 inputs)
    - CEM II, A cement, at plant [CH] (kilogram, 12 inputs)
    - CEM II, B cement, at plant [CH] (kilogram, 13 inputs)
- item: Clinker  (input)
  quote: clinker (data from ecoinvent v3.2), at plant        CH            0                     kg        6.88E-1        7.10E-1       7.88E-1       1               1.31
  search: clinker at plant
  candidates:
    - Clinker, at plant [CH] (kilogram, 25 inputs)
    - Planting [CH] (hectare, 4 inputs)
    - Cement plant [CH] (unit, 4 inputs)
    - Ceramic plant [CH] (unit, 3 inputs)
    - Brass, at plant [CH] (kilogram, 8 inputs)
    - Potato planting [CH] (hectare, 4 inputs)
    - Rock wool plant [CH] (unit, 4 inputs)
    - Bronze, at plant [CH] (kilogram, 8 inputs)
- item: Electricity, medium voltage  (input)
  quote: electricity, medium voltage, at grid                CH            0                    kWh        3.42E-2        3.42E-2       3.13E-2       1               1.31
  search: electricity medium voltage grid
  candidates:
    - Electricity, medium voltage, at grid [CH] (kilowatt hour, 3 inputs)
    - Electricity, medium voltage, SBB, at grid [CH] (kilowatt hour, 3 inputs)
    - Electricity, medium voltage, import AT, at grid [CH] (kilowatt hour, 3 inputs)
    - Electricity, medium voltage, import DE, at grid [CH] (kilowatt hour, 3 inputs)
    - Electricity, medium voltage, import FR, at grid [CH] (kilowatt hour, 3 inputs)
    - Electricity, medium voltage, import IT, at grid [CH] (kilowatt hour, 3 inputs)
    - Electricity, medium voltage, import ENTSO, at grid [CH] (kilowatt hour, 3 inputs)
    - Electricity, medium voltage, production CH, at grid [CH] (kilowatt hour, 3 inputs)
- item: Ethylene glycol (grinding aid)  (input)
  quote: ethylene glycol, at plant                           RER           0                     kg        2.10E-4        2.10E-4       2.12E-4       1               1.13
  search: ethylene glycol plant
  candidates:
    - Ethylene glycol, at plant [RER] (kilogram, 8 inputs, aggregated)
    - Ethylene glycol monoethyl ether, at plant [RER] (kilogram, 7 inputs)
    - xx Ethylene glycol diethyl ether, at plant [RER] (kilogram, 8 inputs)
    - xx Ethylene glycol dimethyl ether, at plant [RER] (kilogram, 7 inputs)
    - Ethylene oxide, at plant [RER] (kilogram, 7 inputs)
    - Ethylenediamine, at plant [RER] (kilogram, 8 inputs)
    - Ethylene bromide, at plant [RER] (kilogram, 6 inputs)
    - Diethylene glycol, at plant [RER] (kilogram, 3 inputs)
- item: Gypsum, mineral  (input)
  quote: gypsum, mineral, at mine                            CH            0                     kg        2.11E-2        2.11E-2       4.64E-2       1               1.30
  search: gypsum mineral mine
  candidates:
    - Gypsum, mineral, at mine [CH] (kilogram, 7 inputs)
    - Adhesive, mineral, matured [CH] (kilogram, 2 inputs)
    - Adhesive, mineral, at plant [CH] (kilogram, 15 inputs)
    - xx Cover coat, mineral, at plant [CH] (kilogram, 9 inputs)
    - Mineral plaster, in sorting plant [CH] (kilogram, 1 inputs)
    - Lightweight plaster, mineral, matured [CH] (kilogram, 2 inputs)
    - Lightweight plaster, mineral, at plant [CH] (kilogram, 15 inputs)
    - xx Disposal, building, mineral wool, to recycling [CH] (kilogram, 0 inputs)
- item: Waste heat  (emission to air)
  quote: air, unspecified Heat, waste                                         -               -                  MJ        1.23E-1        1.23E-1       1.13E-1       1               1.22
  candidates (flow name [compartment]):
    - Waste Heat  [air] (megajoule, ef-3.1-biosphere)
    - Energy, waste heat, air  [resources / in air] (megajoule, bafu-2026-residual)
    - Waste Heat  [soil] (megajoule, ef-3.1-biosphere)
    - Waste Heat  [water] (megajoule, ef-3.1-biosphere)
    - Heat, waste  [emissions to water / groundwater, long-term] (megajoule, bafu-2026-residual)
    - Waste water/m3  [emissions to water / unspecified] (cubic meter, bafu-2026-residual)
    - Waste water  [emissions to water / ocean] (kilogram, bafu-2026-residual)
    - Waste water  [emissions to water / river] (kilogram, bafu-2026-residual)
- item: Steel, low-alloyed (grinding media)  (input)
  quote: technosphere    steel, low-alloyed, at plant                        RER           0                     kg        4.00E-5        4.00E-5       4.04E-5       1               1.22
  search: steel low-alloyed plant
  candidates:
    - Steel, electric, low-alloyed, at plant [CH] (kilogram, 23 inputs)
    - Steel, low-alloyed, at plant [RER] (kilogram, 3 inputs)
    - Steel, converter, low-alloyed, at plant [RER] (kilogram, 21 inputs)
    - Steel, electric, un- and low-alloyed, at plant [RER] (kilogram, 16 inputs)
    - Steel, electric, low-alloyed, at plant, best plants (min. values) [RER] (kilogram, 16 inputs)
    - Steel, electric, low-alloyed, at plant, worst plants (max. values) [RER] (kilogram, 17 inputs)
    - Steel, electric, un- and low-alloyed, for reinforcing steel, import to CH, at plant [DE] (kilogram, 16 inputs)
    - Steel, electric, un- and low-alloyed, for reinforcing steel, import to CH, at plant [FR] (kilogram, 16 inputs)
- item: Limestone, crushed, for mill  (input)
  quote: limestone, crushed, for mill                        CH            0                     kg        1.51E-1        2.69E-1       1.61E-1       1               1.22
  search: limestone crushed mill
  candidates:
    - Limestone, crushed, for mill [CH] (kilogram, 6 inputs)
    - Limestone, crushed, washed [CH] (kilogram, 6 inputs)
    - Limestone, milled, loose, at plant [CH] (kilogram, 6 inputs)
    - Limestone, milled, packed, at plant [CH] (kilogram, 3 inputs)
    - Granite, natural stone council, crushed, for mill [CH] (kilogram, 5 inputs)
- item: Transport, lorry 20-28t  (input)
  quote: transport, lorry 20-28t, fleet average              CH            0                    tkm        4.44E-2        2.00E-2       2.00E-2       1               2.05
  search: transport freight lorry 16t-32t
  candidates:
    - Transport, freight, lorry, 16t-32t gross weight, fleet average [CH] (ton kilometer, 33 inputs)
    - Transport, freight, lorry, 16t-32t gross weight, fleet average [RER] (ton kilometer, 36 inputs)
    - Transport, freight, lorry, 32t-40t gross weight, fleet average [CH] (ton kilometer, 11 inputs)
    - Transport, freight, lorry, 7.5t-16t gross weight, fleet average [CH] (ton kilometer, 11 inputs)
    - Transport, freight, lorry, diesel, 32t gross weight, 2010, EURO-V, long haul [CH] (ton kilometer, 11 inputs)
    - Transport, freight, lorry, diesel, 32t gross weight, 2006, EURO-IV, long haul [CH] (ton kilometer, 11 inputs)
    - Transport, freight, lorry, diesel, 32t gross weight, 2020, EURO-VI, long haul [CH] (ton kilometer, 11 inputs)
    - Transport, freight, lorry, diesel, 32t gross weight, fleet average, long haul [CH] (ton kilometer, 4 inputs)
- item: Transport, rail  (input)
  quote: transport, freight, rail                            RER           0                    tkm        1.50E-4        1.50E-4       1.23E-3       1               2.05
  search: transport freight rail
  candidates:
    - Transport, freight, rail, electricity with shunting [CH] (ton kilometer, 10 inputs)
    - Transport, freight, rail, diesel, with particle filter [CH] (ton kilometer, 9 inputs)
    - Transport, freight, rail, electricity without shunting [CH] (ton kilometer, 9 inputs)
    - Transport, freight, rail, diesel, without particle filter [CH] (ton kilometer, 9 inputs)
    - Transport, freight, rail, electricity with shunting, Betrieb [CH] (ton kilometer, 2 inputs)
    - Transport, freight, rail, electricity with shunting, Fahrzeug [CH] (ton kilometer, 5 inputs)
    - Transport, freight, rail, electricity with shunting, Infrastruktur [CH] (ton kilometer, 3 inputs)
    - Transport, freight, rail [RER] (ton kilometer, 10 inputs)

Return only the JSON object described by the schema.
