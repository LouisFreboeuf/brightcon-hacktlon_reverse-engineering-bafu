# Benchmark `flow-n8-seed7`: 8 synthetic aggregated datasets, seed 7

Ground truth = BAFU unit processes (3-30 inputs, stratified over categories); target = their cumulative inventory.

| scenario | flows within ±10 % | median \|Δ flow\| | flows missing | material amounts within ±20 % | material inputs chosen / true | false pos. | false neg. |
|---|---|---|---|---|---|---|---|
| oracle | 89% | 2.7 % | 0 | 27/49 | 4 / 4 | 0 | 0 |
| bounded | 90% | 2.1 % | 0 | 26/49 | 5 / 4 | 0 | 0 |
| partial | 86% | 3.5 % | 0 | 21/37 | 3 / 5 | 0 | 2 |
| distractors | 93% | 2.6 % | 0 | 31/49 | 12 / 4 | 6 | 0 |
| blind | 8% | 121.8 % | 0 | 0/39 | 144 / 4 | 144 | 4 |

Medians over cases; no impact assessment — agreement is counted per elementary flow of the target's cumulative inventory. 'Material' inputs are those whose true contribution reaches 1 % of the target amount of some flow. `partial` removes the 30 % of inputs that explain the fewest flows before fitting; `distractors` adds 10 random frequently-used processes; `blind` offers every process used ≥ 30 times and no direct flows.

