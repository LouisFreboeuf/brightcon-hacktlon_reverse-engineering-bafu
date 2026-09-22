# Benchmark `flow-n10-seed7`: 10 synthetic aggregated datasets, seed 7

Ground truth = BAFU unit processes (3-30 inputs, stratified over categories); target = their cumulative inventory.

| scenario | flows within ±10 % | median \|Δ flow\| | flows missing | material amounts within ±20 % | material inputs chosen / true | false pos. | false neg. |
|---|---|---|---|---|---|---|---|
| oracle | 94% | 0.0 % | 0 | 49/63 | 4 / 4 | 0 | 0 |
| bounded | 94% | 0.0 % | 0 | 53/63 | 4 / 4 | 0 | 0 |
| partial | 87% | 0.8 % | 0 | 24/47 | 4 / 5 | 0 | 2 |
| distractors | 82% | 1.3 % | 0 | 25/63 | 7 / 4 | 4 | 1 |

Medians over cases; no impact assessment — agreement is counted per elementary flow of the target's cumulative inventory. 'Material' inputs are those whose true contribution reaches 1 % of the target amount of some flow. `partial` removes the 30 % of inputs that explain the fewest flows before fitting; `distractors` adds 10 random frequently-used processes; `blind` offers every process used ≥ 30 times and no direct flows.

