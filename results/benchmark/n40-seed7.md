# Benchmark `n40-seed7`: 40 synthetic aggregated datasets, seed 7

Ground truth = BAFU unit processes (3-30 inputs, stratified over categories); target = their cumulative inventory.

| scenario | median \|Δ score\| | categories within ±10 % (of 25) | climate \|Δ\| median | material amounts within ±20 % | material inputs chosen / true | false pos. | false neg. | residual share median |
|---|---|---|---|---|---|---|---|---|
| oracle | 0.0 % | 25 | 0.0 % | 202/220 | 4 / 4 | 0 | 0 | 0.0 % |
| bounded | 0.0 % | 25 | 0.0 % | 204/220 | 4 / 4 | 0 | 0 | 0.0 % |
| partial | 0.1 % | 25 | 0.1 % | 149/185 | 4 / 5 | 0 | 2 | 0.1 % |
| distractors | 0.0 % | 25 | 0.0 % | 188/220 | 4 / 4 | 0 | 0 | 0.0 % |

Medians over cases. 'Material' inputs are those whose true contribution reaches 1 % of the target score in some category. `partial` removes the 30 % of inputs with the smallest climate contribution before fitting; `distractors` adds 10 random frequently-used processes; `blind` offers every process used ≥ 30 times and no direct flows.

