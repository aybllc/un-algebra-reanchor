import argparse, json, os, sys
import pandas as pd
import yaml
from .un_validation import run_all

def main():
    ap = argparse.ArgumentParser(prog="unreanchor", description="UN-Algebra retro-validation")
    sub = ap.add_subparsers(dest="cmd")

    runp = sub.add_parser("run", help="Run validation")
    runp.add_argument("--data", required=True)
    runp.add_argument("--config", required=True)
    runp.add_argument("--out", required=True)

    args = ap.parse_args()
    if args.cmd != "run":
        ap.print_help()
        sys.exit(1)

    os.makedirs(args.out, exist_ok=True)
    df = pd.read_csv(args.data)
    with open(args.config) as f:
        cfg = yaml.safe_load(f)
    report, decisions = run_all(df, cfg)
    with open(os.path.join(args.out, "report.json"), "w") as f:
        json.dump(report, f, indent=2)
    decisions.to_csv(os.path.join(args.out, "decisions.csv"), index=False)
    print(json.dumps(report, indent=2))
