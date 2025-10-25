import argparse, csv, random
from datetime import datetime, timedelta

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    random.seed(42)
    start = datetime(2024,1,1)
    rows = []
    for i in range(120):
        nominal = 10.0
        tol = 0.05
        true_val = random.gauss(nominal, 0.01)
        U = abs(random.gauss(0.01, 0.002))
        measured = random.gauss(true_val, U/2.0)
        inst = "A" if i%3!=0 else "B"
        part_id = i//2 if i%10==0 else i
        timestamp = (start + timedelta(days=i)).isoformat()
        LSL = nominal - tol
        USL = nominal + tol
        accepted = 1 if (LSL <= measured <= USL) else 0
        rows.append({
            "part_id": part_id,
            "nominal": nominal,
            "tol_lower": tol,
            "tol_upper": tol,
            "measured": measured,
            "true_value": true_val if i%5==0 else "",
            "uncertainty_U": U,
            "instrument_id": inst,
            "accepted": accepted,
            "timestamp": timestamp
        })

    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

if __name__ == "__main__":
    main()
