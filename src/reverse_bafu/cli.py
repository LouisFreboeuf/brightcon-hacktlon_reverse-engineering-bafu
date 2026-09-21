"""``reverse-bafu resolve|calibrate|build|check|run <spec.json>``"""

from __future__ import annotations

import argparse
import sys
import warnings

from . import db, spec as spec_mod


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="reverse-bafu", description=__doc__)
    p.add_argument("command", choices=["resolve", "calibrate", "build", "check", "run", "benchmark"])
    p.add_argument("spec", nargs="?", help="spec JSON (see src/reverse_bafu/spec.py); not used by benchmark")
    p.add_argument("--n", type=int, default=30, help="benchmark: number of synthetic cases")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--scenarios", default="oracle,bounded,partial,distractors,blind")
    p.add_argument("--name", default=None, help="benchmark: output name (default n<N>-seed<S>)")
    p.add_argument("--project", default="reverse-bafu")
    p.add_argument("--apply", action="store_true", help="calibrate: write fitted amounts back into the spec")
    p.add_argument("--no-hybrid", action="store_true", help="build: skip the residual (hybrid) node")
    args = p.parse_args(argv)

    warnings.filterwarnings("ignore", message=".*pypardiso.*")
    db.set_project(args.project)
    if args.command == "benchmark":
        from . import benchmark
        benchmark.run(args.n, args.seed, args.scenarios.split(","), args.name or f"n{args.n}-seed{args.seed}")
        return 0
    if not args.spec:
        p.error("spec is required")
    spec = spec_mod.load(args.spec)
    print(f"== {args.command}: {spec.target_name} ({spec.target_code}) ==", file=sys.stderr)

    if args.command in ("resolve", "run"):
        from . import resolve
        if not resolve.run(spec):
            return 2
        spec_mod.save(spec)
    if args.command in ("calibrate", "run"):
        from . import calibrate
        calibrate.run(spec, apply=args.apply)
    if args.command in ("build", "run"):
        from . import build
        if args.command == "build":
            spec = spec_mod.load(args.spec)  # pick up codes written by resolve
        build.run(spec, hybrid=not args.no_hybrid)
    if args.command in ("check", "run"):
        from . import check
        check.run(spec_mod.load(args.spec))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
