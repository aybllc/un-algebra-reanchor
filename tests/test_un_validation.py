import pandas as pd, yaml
from src.un_reanchor.un_validation import run_all

def test_smoke():
    # minimal synthetic
    df = pd.DataFrame({
        "part_id":[1,1,2],
        "nominal":[10,10,10],
        "tol_lower":[0.05,0.05,0.05],
        "tol_upper":[0.05,0.05,0.05],
        "measured":[10.01,9.99,10.06],
        "true_value":[10.00,10.00,""],
        "uncertainty_U":[0.01,0.01,0.01],
        "instrument_id":["A","B","A"],
        "accepted":[1,1,0]
    })
    cfg = yaml.safe_load(open("configs/config.sample.yaml"))
    report, decisions = run_all(df, cfg)
    assert set(report.keys()) == {"UN-T1","UN-T2","UN-T3","UN-T4","UN-T5","UN-T6"}
