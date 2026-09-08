from __future__ import annotations

import argparse

from .pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(description="Healthcare Claims Intelligence pipeline")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="Generate synthetic data and run the full analytics pipeline")
    run.add_argument("--claims", type=int, default=120000)
    run.add_argument("--seed", type=int, default=42)
    run.add_argument("--output-dir", default="reports/latest")
    args = parser.parse_args()
    if args.command == "run":
        result = run_pipeline(n_claims=args.claims, seed=args.seed, output_dir=args.output_dir)
        print("Pipeline complete")
        print(result["evaluation"])

if __name__ == "__main__":
    main()
