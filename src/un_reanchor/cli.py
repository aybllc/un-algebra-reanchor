import argparse, json, os, sys
import pandas as pd
import yaml
from .un_validation import run_all
from .un_ct1 import un_CT1_cosmology
from .net import fetch_to_cache

def _maybe_run_un_ct1(data_path: str, out_dir: str, uha_address: str):
    try:
        # If data_path is remote, download first
        if data_path.startswith("http://") or data_path.startswith("https://"):
            cached = fetch_to_cache(data_path)
            df = pd.read_csv(cached)
        else:
            df = pd.read_csv(data_path)
    except Exception:
        return None
    required = {"label","H0","uncertainty_U","frame"}
    if not required.issubset(set(df.columns)):
        return None
    if not uha_address:
        raise SystemExit("H0 dataset detected but --uha <ADDRESS> was not provided.")
    summary, res = un_CT1_cosmology(df, uha_address)
    os.makedirs(out_dir, exist_ok=True)
    res.to_csv(os.path.join(out_dir, "un_ct1_results.csv"), index=False)
    with open(os.path.join(out_dir, "un_ct1_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    return summary

def main():
    ap = argparse.ArgumentParser(prog="unreanchor", description="UN-Algebra retro-validation")
    sub = ap.add_subparsers(dest="cmd")

    runp = sub.add_parser("run", help="Run validation")
    runp.add_argument("--data", required=True, help="CSV file path or URL (generic metrology OR H0 table)")
    runp.add_argument("--config", required=True, help="YAML config for generic tests")
    runp.add_argument("--out", required=True, help="Output directory")
    runp.add_argument("--uha", default="", help="UHA address (file:/ doi:/ zenodo:/ https://) for cosmology UN-CT1")

    args = ap.parse_args()
    if args.cmd != "run":
        ap.print_help()
        sys.exit(1)

    # Try generic tests (metrology)
    try:
        # If --data is remote, fetch with auth if needed
        data_path = args.data
        if data_path.startswith("http://") or data_path.startswith("https://"):
            data_path = fetch_to_cache(data_path)
        df_generic = pd.read_csv(data_path)
        with open(args.config) as f:
            cfg = yaml.safe_load(f)
        report, decisions = run_all(df_generic, cfg)
        os.makedirs(args.out, exist_ok=True)
        with open(os.path.join(args.out, "report.json"), "w") as f:
            json.dump(report, f, indent=2)
        decisions.to_csv(os.path.join(args.out, "decisions.csv"), index=False)
        print(json.dumps(report, indent=2))
    except Exception as e:
        # Not a generic dataset; proceed silently
        pass

    # Cosmology test if H0 table detected
    ct1 = _maybe_run_un_ct1(args.data, args.out, args.uha)
    if ct1:
        print("\nUN-CT1 summary:")
        print(json.dumps(ct1, indent=2))
