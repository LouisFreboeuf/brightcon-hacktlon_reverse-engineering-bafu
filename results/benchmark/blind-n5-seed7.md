# Benchmark `blind-n5-seed7`: 5 synthetic aggregated datasets, seed 7

Ground truth = BAFU unit processes (3-30 inputs, stratified over categories); target = their cumulative inventory.

| scenario | median \|Δ score\| | categories within ±10 % (of 25) | climate \|Δ\| median | material amounts within ±20 % | material inputs chosen / true | false pos. | false neg. | residual share median |
|---|---|---|---|---|---|---|---|---|
| blind | 43.8 % | 5 | 22.6 % | 0/23 | 25 / 4 | 24 | 4 | 43.8 % |

Medians over cases. 'Material' inputs are those whose true contribution reaches 1 % of the target score in some category. `partial` removes the 30 % of inputs with the smallest climate contribution before fitting; `distractors` adds 10 random frequently-used processes; `blind` offers every process used ≥ 30 times and no direct flows.

