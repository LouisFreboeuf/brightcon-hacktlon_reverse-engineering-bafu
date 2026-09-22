# Benchmark `flow-n100-seed7`: 100 synthetic aggregated datasets, seed 7

Ground truth = BAFU unit processes (3-30 inputs, stratified over categories); target = their cumulative inventory.

| scenario | flows within ±10 % | median \|Δ flow\| | flows missing | material amounts within ±20 % | material inputs chosen / true | false pos. | false neg. |
|---|---|---|---|---|---|---|---|
| oracle | 100% | 0.0 % | 0 | 614/803 | 6 / 6 | 0 | 0 |
| bounded | 100% | 0.0 % | 0 | 761/803 | 6 / 6 | 0 | 0 |
| partial | 91% | 1.1 % | 0 | 307/605 | 4 / 7 | 0 | 2 |
| distractors | 63% | 7.0 % | 0 | 256/803 | 10 / 6 | 5 | 1 |

Medians over cases; no impact assessment — agreement is counted per elementary flow of the target's cumulative inventory, over the flows the solve determines (about 120 of ~1,790 per process come out of the sparse solve as round-off and are not scored; see lci.determined_flows). 'Material' inputs are those whose true contribution reaches 1 % of the target amount of some flow. `partial` removes the 30 % of inputs that explain the fewest flows before fitting; `distractors` adds 10 random frequently-used processes; `blind` offers every process used ≥ 30 times and no direct flows.

