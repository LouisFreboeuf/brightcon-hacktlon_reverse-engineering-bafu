---
description: Draft specs for every system-terminated BAFU dataset in results/system_terminated.csv, using this Claude Code session as the model for the locate / extract / map prompts
argument-hint: [--only <codes>] [--project <name>]
---

Run the reverse-bafu batch drafter over `results/system_terminated.csv`, this session being the model. `$ARGUMENTS` may pass `--only <comma-separated codes or 8-char prefixes>` and `--project <name>`; pass them through unchanged. Loop until nothing is pending; never edit amounts, add inputs or read the hand-written specs — those are the reviewer's decisions.

1. `uv run reverse-bafu draft-all --dry-run --by "claude-code:<the model you are running as>" $ARGUMENTS`. It writes `results/drafting_status.csv`; each row's `status` says how far that dataset got.
2. For every row whose status is `prompt-0-written`: read `specs/evidence/<code>/prompt-0-locate.md` in full and answer it with one JSON object satisfying `schema-0-locate.json` (the page range of the inventory table, or `found: false` with the reason); write it to `response-0-locate.json` with the Write tool.
3. For every row whose status is `prompt-1-written`: read `prompt-1-extract.md` and answer per its eight rules (verbatim quotes, raw values, no inputs the excerpt does not mention — those go into `gaps`); write `response-1-extract.json`.
4. For every row whose status is `prompt-2-written`: read `prompt-2-map.md`; every `chosen` must be one of the listed candidates or null with a reason; write `response-2-map.json`.
5. Rerun step 1. Ingested responses are validated; fix and rerun any the command rejects. Repeat 1–5 until every row is `drafted`, `pages-not-found`, `no-pdf` or `error`.
6. Report the final status counts, and for each `drafted` dataset the spec path and the model's `gaps`. Then run `uv run reverse-bafu run specs/<code>-<slug>.draft.json` for each drafted spec and report the check summaries. Do not run `--apply`.
