# Handover — what "% of flows within ±10 %" actually counts

Branch `bench-run-10`, as of commit `b0663be`. Written to be picked up cold, by me in a later
session or by another agent. Every number below is reproducible; see **How to check any of this**.

---

## TL;DR

The headline benchmark number used to top out at **94 %** even when the algorithm was handed the
exactly correct answer. Two unrelated causes:

1. **A real bug** — the benchmark's ground truth silently dropped duplicate exchanges. Fixed.
2. **The metric, not the model** — ~120 of ~1,790 flows per process come out of the sparse solve
   as round-off. Comparing a model against them is meaningless. They are now excluded from the
   denominator and counted separately, so `oracle` reads **100 %**, which is the truth.

Nothing about the reconstruction changed for (2). It is a change to *what is counted*, and it
should be described that way in public — the model did not improve, the metric stopped punishing
it for noise.

---

## Why this came up

The `oracle` scenario of the calibration benchmark hands the fitter the exactly correct input
list. It scored 94 %, not 100 %. The question was simply: why?

The decisive move was to **skip the optimiser entirely and plug the true amounts in**. That also
scored 94 %, which proved the gap had nothing to do with the fit.

---

## Finding 1 — the duplicate-exchange bug (a real defect, now fixed)

`pick_cases` built the answer key with dict comprehensions:

```python
"inputs": {tuple(e["input"]): e["amount"] for e in techno}
```

A process can list the same input on several exchanges, and several elementary flows can map onto
one EF 3.1 flow. The comprehension keeps the **last** and silently drops the rest.

Measured on the ten seed-7 cases:

| case | what was lost |
|---|---|
| Panelling, aluminium | 1.335 kg of aluminium profile (anodised + powder-coated are the same dataset) |
| Disposal, sewer system | 1301 units |
| Ceramic plant | half its land occupation — "Occupation, industrial area, vegetation" and "…built up" both resolve to the EF flow *Industrial Area* |

With the true amounts those three scored 5.9 %, 5.3 % and 47.6 %. Summing duplicates puts them on
94 % like everyone else. Effect on published figures (n=10, seed 7):

- oracle amounts within ±20 %: 49/63 → **56/63**
- bounded: 53/63 → **62/63**
- distractors: flows 82 → 88 %, amounts 25/63 → 33/63

Fixed in `src/reverse_bafu/benchmark.py::pick_cases` (accumulates into `defaultdict(float)`).

> Related earlier fix in the same area: `Bench.blind_pool` was built from a `Counter` over
> `Database.load()` and never sorted, so `rng.sample` drew a different distractor set on every run
> and the `distractors` scenario was not reproducible. Sorting it moved distractors 73 % → 82 %.
> The full chain for that row is therefore **73 → 82 → 88 → 95 %**, across three separate changes.

---

## Finding 2 — the 94 % ceiling is the metric

### What is actually wrong with those flows

Computing a cumulative inventory solves *how much of each of the 11,983 processes is needed*. That
scaling vector `s` spans an absurd range, because supply chains loop (electricity → steel →
electricity …), so the answer is an infinite series with ever-smaller terms:

| ceramic plant | |
|---|---|
| largest entry of `s` | 3.861e+07 |
| smallest non-zero | 6.183e-52 |
| spread | **6.2e+58** |
| absolute error floor of the solve (`eps × max|s|`) | 8.573e-09 |
| entries of `s` below that floor | **1,821 of 6,057 non-zero** |

A double keeps ~16 *significant* digits relative to the largest number in the calculation.
Everything below the floor is whatever round-off landed there. Flows fed mainly by those entries
inherit the noise:

| the flow's dominant contributor, as a fraction of `max|s|` | |
|---|---|
| flows we score | 1.13e-03 |
| flows we exclude | **8.16e-22** |

### How it is detected

`src/reverse_bafu/lci.py::determined_flows` — solve, take **one step of iterative refinement**,
keep the flows that barely move:

```python
s  = lu.solve(D)
s2 = s + lu.solve(D - A @ s)
move = |B·s2 − B·s| / |B·s|
return move <= tol            # tol = 1e-2
```

| | median move under refinement |
|---|---|
| flows kept | ~1e-10 |
| flows excluded | **~1.00 (100 %)** |

The separation is not marginal — it is ten orders of magnitude. `tol` is insensitive: 1e-2 and
1e-3 give identical results.

---

## What was changed in the code

| file | change |
|---|---|
| `lci.py` | new `determined_flows(sys_, activity_id, tol=1e-2)`; `flow_agreement(target, model, scored=None)` takes an optional mask and additionally returns `n_scored` and `n_excluded` (`n_target` unchanged, so the old number is always reconstructable) |
| `check.py` | computes the mask for the target, passes it; report and console line print the excluded count |
| `benchmark.py` | `Bench.determined()` caches the mask per case; `run_case` passes it; CSV gains `n_scored_flows`, `n_excluded_flows`; `flows_within_10pct_share` now divides by `n_scored` |
| `runall.py` | `_summary` regex follows the new wording of the check report (**this is brittle — it parses prose; if you reword the check report, update the regex**) |

### Effect

| | before | after |
|---|---|---|
| calibration oracle / bounded | 94 % | **100 %** |
| calibration partial | 87 % | 93 % |
| calibration distractors | 88 % | 95 % |
| extraction benchmark, median | 73 % | 77 % |
| **the 11 rebuilt real datasets** | 2–19 % | **unchanged** |

The last row is the best check on the method. A system process has **no technosphere inputs**, so
its cumulative inventory is just its own biosphere column — the solve is trivial, nothing is
round-off, nothing is excluded. The filter fires only where noise exists. Their 2–19 % figures are
real modelling gaps, not artefacts.

---

## Rejected alternatives, and the measurements that killed them

Worth knowing so nobody re-proposes them.

**A. Exclude flows with small amounts** (the intuitive first idea — cutoff relative to the largest
flow of each (unit, compartment) group). *Fails.* On copper oxide it dropped **34 named trace
pollutants** — 2,3,7,8-TCDD at 2.07e-17 kg, benzo[a]pyrene 2.06e-18, mercury 2.58e-15,
hexachlorobenzene 1.27e-18 — while **keeping Thorium-232 at −4.42e-26**, which is pure noise.
Size and meaninglessness are different axes: impact per kg varies by >10 orders of magnitude, so
any size rule discards the substances that are supposed to be tiny. By contrast the refinement
test keeps **640 of 650** named trace pollutants.

**B. Cancellation within our own model sum** (`|Σ contributions| / Σ|contributions|`). *Fails* —
the ratio is ~1 for agreeing and failing flows alike. The instability is in the target's solve,
not in our arithmetic.

**C. Per-row conditioning of the B-product** (`|B|·|s|` vs `B·s`). *Fails* — excludes nothing. The
noise is in `s` itself, not in the row sum.

### A wrong turn worth not repeating

I first "disproved" the round-off explanation by comparing `splu` against `scipy.sparse.linalg.spsolve`
and getting bit-identical results. **That test is invalid** — `spsolve` on a CSC matrix *is*
SuperLU, the same algorithm. Iterative refinement is the valid test.

---

## Validation: can the filter hide a real error?

Injected known errors into an otherwise perfect model:

| injected | score | |
|---|---|---|
| biggest input ×2 | 100 % → **0.7–58 %** | fully caught |
| smallest input ×10 | 100 % → **2.8–97.8 %** | caught where it matters |
| biggest input ×1.1 | 100 % → **100 %** | see below |

Then, inside the excluded set specifically, compared the size of the injected error against each
flow's own wobble. In most cases **0 of ~120** excluded flows carried a recoverable trace; in a few
up to 40 did, but the largest such trace was **3.3e-18 × the biggest flow** — eighteen orders of
magnitude below anything material.

**The ×1.1 blind spot is the ±10 % threshold, not the exclusion.** An error that moves flows by at
most 10 % cannot trip a ">10 %" test by construction. That is an independent knob.

---

## Open decisions (these are yours, nothing is blocked)

1. **Report both numbers in the headline?** e.g. *"100 % of the 1,670 determined flows; 120
   excluded as round-off"*. I recommend yes — it costs a clause and removes the "you're hiding
   things" objection entirely. `n_scored` / `n_excluded` are already in the CSV and the check report.
2. **Tighten the ±10 % tolerance?** It is insensitive to sub-10 % input errors (the ×1.1 case).
   Unrelated to the exclusion; decide on its own merits.
3. **`tol = 1e-2` in `determined_flows`.** Insensitive between 1e-2 and 1e-3, so unlikely to matter,
   but it is the one free parameter in the mechanism.

---

## Stale documentation — not yet updated

- **`README.md` §6 "What the latest run says"** still quotes `flow-n8-seed7`: *89 % of flows,
  27/49 amounts, blind 8 % / 144 false positives*. Those predate **all three** changes
  (blind_pool sort, duplicate fix, determined_flows) and are wrong now. `flow-n8-seed7.md` and
  `flow-n40-seed7.md` themselves were never re-run either.
- **`artifacts/method-explainer.html`** §7 quotes 44/49 and 27/49 material amounts from an older run.
- **`scripts/render_pages.py`** defaults to a Brightway project named `reverse-bafu`, which does not
  exist here (the real ones are `bafu-2026` and `bafu-2026-bench`). It exits without writing, so
  `artifacts/rebuilt-inventories.html` still shows only the original 3 of the 11 rebuilt datasets.

## Environment notes

- All runs in this thread used `--project bafu-2026-bench`, a copy of `bafu-2026` made to avoid
  colliding with a parallel session. Identical databases; results are not affected.
- `results/benchmark/*-detail.json` are the data the two HTML result pages embed; regenerate with
  `scripts/dump_calibration_detail.py` and `scripts/dump_extraction_detail.py`.

## How to check any of this

`scripts/verify_determined_flows.py` re-derives all four parts from scratch. It reports on the
*ceramic plant* case, so its per-case counts differ from the copper-oxide figures quoted above
(e.g. the magnitude cutoff drops 14 of 65 trace pollutants there, 34 of 51 on copper oxide); the
separation itself is the same everywhere.

```bash
# the whole argument, in one script
PYTHONPATH=$PWD/src ./.venv/bin/python scripts/verify_determined_flows.py

# re-run the calibration benchmark (~45 s)
PYTHONPATH=$PWD/src ./.venv/bin/python -m reverse_bafu.cli benchmark \
  --project bafu-2026-bench --n 10 --seed 7 \
  --scenarios oracle,bounded,partial,distractors --name flow-n10-seed7
```

## Commit trail

| commit | |
|---|---|
| `76707d1` | duplicate-exchange fix; first diagnosis of the 94 % ceiling |
| `a133386` | artifacts refreshed against the fixed run |
| `b0663be` | `determined_flows`, wired into check / benchmark / runall; artifacts and deck regenerated |
