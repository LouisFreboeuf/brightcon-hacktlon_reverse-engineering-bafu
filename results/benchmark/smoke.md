# Benchmark `smoke`: 6 synthetic aggregated datasets, seed 1

Ground truth = BAFU unit processes (3-30 inputs, stratified over categories); target = their cumulative inventory.

| scenario | median \|Δ score\| | categories within ±10 % (of 25) | climate \|Δ\| median | amounts within ±20 % | inputs chosen / true | false pos. | false neg. | residual share median |
|---|---|---|---|---|---|---|---|---|
| oracle | 0.0 % | 25 | 0.0 % | 37/39 | 3 / 4 | 0 | 0 | 0.0 % |
| bounded | 0.0 % | 25 | 0.0 % | 37/39 | 3 / 4 | 0 | 0 | 0.0 % |
| partial | 1.0 % | 24 | 0.9 % | 15/27 | 2 / 4 | 0 | 2 | 1.0 % |
| distractors | 0.0 % | 25 | 0.0 % | 11/39 | 4 / 4 | 0 | 0 | 0.0 % |

Medians over cases. `partial` removes the 30 % of inputs with the smallest climate contribution before fitting; `distractors` adds 10 random frequently-used processes; `blind` offers every process used ≥ 30 times and no direct flows.

