from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from claims_intelligence.pipeline import run_pipeline

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--claims", type=int, default=120000)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    result = run_pipeline(n_claims=args.claims, seed=args.seed, project_root=ROOT)
    print("Pipeline complete")
    print(result["evaluation"])
