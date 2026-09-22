# Benchmark `flow-n10-seed7`: 10 synthetic aggregated datasets, seed 7

Ground truth = BAFU unit processes (3-30 inputs, stratified over categories); target = their cumulative inventory.

| scenario | flows within ±10 % | median \|Δ flow\| | flows missing | material amounts within ±20 % | material inputs chosen / true | false pos. | false neg. |
|---|---|---|---|---|---|---|---|
| oracle | 94% | 0.0 % | 0 | 56/63 | 4 / 4 | 0 | 0 |
| bounded | 94% | 0.0 % | 0 | 62/63 | 4 / 4 | 0 | 0 |
| partial | 87% | 0.8 % | 0 | 26/47 | 4 / 5 | 0 | 2 |
| distractors | 88% | 0.8 % | 0 | 33/63 | 8 / 4 | 5 | 1 |

Medians over cases; no impact assessment — agreement is counted per elementary flow of the target's cumulative inventory. 'Material' inputs are those whose true contribution reaches 1 % of the target amount of some flow. `partial` removes the 30 % of inputs that explain the fewest flows before fitting; `distractors` adds 10 random frequently-used processes; `blind` offers every process used ≥ 30 times and no direct flows.

