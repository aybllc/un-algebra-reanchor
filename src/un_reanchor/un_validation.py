import json, math
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
import pandas as pd
import numpy as np

@dataclass
class Config:
    columns: Dict[str, Optional[str]]
    params: Dict[str, Any]

def _col(df, name, cfg):
    c = cfg["columns"].get(name)
    return df[c] if c in df.columns else pd.Series([np.nan]*len(df))

def compute_spec_limits(df, cfg):
    nominal = _col(df, "nominal", cfg).astype(float)
    tl = _col(df, "tol_lower", cfg).astype(float)
    tu = _col(df, "tol_upper", cfg).astype(float)
    LSL = nominal - tl.abs()
    USL = nominal + tu.abs()
    tol = np.maximum(tl.abs(), tu.abs())
    return LSL, USL, tol

def compute_uncertainty_U(df, cfg):
    if cfg["columns"].get("uncertainty_U") and cfg["columns"]["uncertainty_U"] in df.columns:
        U = df[cfg["columns"]["uncertainty_U"]].astype(float)
    else:
        if "sigma" in df.columns:
            k = float(cfg["params"].get("coverage_k", 2.0))
            U = df["sigma"].astype(float) * k
        else:
            raise ValueError("Provide either 'uncertainty_U' column or 'sigma' + coverage_k in config.")
    return U

def un_T1_inequality_coverage(df, cfg):
    measured = _col(df, "measured", cfg).astype(float)
    truev = pd.to_numeric(_col(df, "true_value", cfg), errors='coerce')
    LSL, USL, tol = compute_spec_limits(df, cfg)
    U = compute_uncertainty_U(df, cfg)
    mask = ~truev.isna()
    if mask.sum() == 0:
        return {"n": 0, "coverage_rate": None}
    lhs = (measured - truev).abs()
    rhs = tol + U
    covered = lhs[mask] <= rhs[mask]
    return {"n": int(mask.sum()), "coverage_rate": float(covered.mean())}

def iso_guard_band_decision(measured, LSL, USL, U, gamma=1.0):
    if measured <= LSL - gamma*U or measured >= USL + gamma*U:
        return "nonconform"
    if measured >= LSL + gamma*U and measured <= USL - gamma*U:
        return "conform"
    return "indeterminate"

def un_T2_guard_band(df, cfg):
    measured = _col(df, "measured", cfg).astype(float)
    LSL, USL, tol = compute_spec_limits(df, cfg)
    U = compute_uncertainty_U(df, cfg)
    gamma = float(cfg["params"].get("gamma", 1.0))
    decisions = [iso_guard_band_decision(m, l, u, uu, gamma) for m,l,u,uu in zip(measured, LSL, USL, U)]
    out = pd.Series(decisions, name="decision")
    res = out.value_counts(normalize=True).to_dict()
    res_counts = out.value_counts().to_dict()
    acc_col = cfg["columns"].get("accepted")
    agree = None
    if acc_col and acc_col in df.columns:
        determ_mask = out.isin(["conform","nonconform"])
        if determ_mask.sum() > 0:
            mapping = {1:"conform", 0:"nonconform"}
            gold = df.loc[determ_mask, acc_col].map(mapping)
            agree = (out[determ_mask] == gold).mean()
    return {"share": res, "counts": res_counts, "agreement_with_archival": None if agree is None else float(agree)}, out

def un_T3_cross_instrument(df, cfg):
    inst_col = cfg["columns"].get("instrument_id")
    if not inst_col or inst_col not in df.columns:
        return {"n_pairs": 0, "exceed_rate": None}
    U = compute_uncertainty_U(df, cfg)
    measured = _col(df, "measured", cfg).astype(float)
    pid = _col(df, "part_id", cfg)
    pairs = []
    for part, g in df.groupby(pid):
        if g[inst_col].nunique() < 2: continue
        g = g.reset_index(drop=True)
        for i in range(len(g)):
            for j in range(i+1, len(g)):
                diff = abs(g.loc[i, cfg["columns"]["measured"]] - g.loc[j, cfg["columns"]["measured"]])
                u_sum = g.loc[i, "uncertainty_U"] + g.loc[j, "uncertainty_U"]
                pairs.append(diff > u_sum)
    if not pairs:
        return {"n_pairs": 0, "exceed_rate": None}
    exceed_rate = float(np.mean(pairs))
    return {"n_pairs": len(pairs), "exceed_rate": exceed_rate}

def un_T4_temporal_drift(df, cfg):
    cut = cfg["params"].get("calibration_cut")
    if not cut:
        return {"before_n": 0, "after_n": 0, "delta_mean": None}
    measured = _col(df, "measured", cfg).astype(float)
    ts_col = cfg["columns"].get("timestamp")
    if not ts_col or ts_col not in df.columns:
        return {"before_n": 0, "after_n": 0, "delta_mean": None}
    ts = pd.to_datetime(df[ts_col])
    before = measured[ts < pd.to_datetime(cut)]
    after = measured[ts >= pd.to_datetime(cut)]
    if len(before)==0 or len(after)==0:
        return {"before_n": int(len(before)), "after_n": int(len(after)), "delta_mean": None}
    return {"before_n": int(len(before)), "after_n": int(len(after)), "delta_mean": float(after.mean()-before.mean())}

def un_T5_edge_of_spec(df, cfg):
    measured = _col(df, "measured", cfg).astype(float)
    LSL, USL, tol = compute_spec_limits(df, cfg)
    delta = float(cfg["params"].get("edge_delta", 0.1))
    near = (abs(measured - LSL) <= delta) | (abs(USL - measured) <= delta)
    if near.sum()==0:
        return {"n_edge": 0, "indeterminate_rate": None}
    U = compute_uncertainty_U(df, cfg)
    gamma = float(cfg["params"].get("gamma", 1.0))
    decisions = [iso_guard_band_decision(m, l, u, uu, gamma) for m,l,u,uu in zip(measured[near], LSL[near], USL[near], U[near])]
    indec_rate = np.mean(pd.Series(decisions)=="indeterminate")
    return {"n_edge": int(near.sum()), "indeterminate_rate": float(indec_rate)}

def un_T6_interval_coverage(df, cfg):
    measured = _col(df, "measured", cfg).astype(float)
    truev = pd.to_numeric(_col(df, "true_value", cfg), errors='coerce')
    U = compute_uncertainty_U(df, cfg)
    mask = ~truev.isna()
    if mask.sum()==0:
        return {"n": 0, "coverage": None}
    covered = (truev[mask] >= measured[mask]-U[mask]) & (truev[mask] <= measured[mask]+U[mask])
    return {"n": int(mask.sum()), "coverage": float(covered.mean())}

def run_all(df, cfg):
    if "uncertainty_U" not in df.columns:
        if "sigma" in df.columns:
            df["uncertainty_U"] = df["sigma"] * float(cfg["params"].get("coverage_k", 2.0))
    report = {}
    report["UN-T1"] = un_T1_inequality_coverage(df, cfg)
    gb_res, decisions = un_T2_guard_band(df, cfg)
    report["UN-T2"] = gb_res
    report["UN-T3"] = un_T3_cross_instrument(df, cfg)
    report["UN-T4"] = un_T4_temporal_drift(df, cfg)
    report["UN-T5"] = un_T5_edge_of_spec(df, cfg)
    report["UN-T6"] = un_T6_interval_coverage(df, cfg)
    return report, decisions
