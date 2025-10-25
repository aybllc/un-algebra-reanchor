import pandas as pd
from .uha import resolve_uha_address

def un_CT1_cosmology(df_h0: pd.DataFrame, uha_address: str):
    """
    Expect df_h0 with columns: label, H0, uncertainty_U, frame
    Anchor is loaded from UHA address (JSON schema provided).
    Returns (summary_dict, per_row_results_df).
    """
    anchor = resolve_uha_address(uha_address)
    a_val = float(anchor["value"])
    a_u = float(anchor["u"])
    tmap = anchor.get("t_interframe", {}) or {}
    default_T = float(tmap.get("default", 0.0))

    rows = []
    for _, r in df_h0.iterrows():
        h0 = float(r["H0"])
        u = float(r["uncertainty_U"])
        frame = str(r.get("frame",""))
        T = float(tmap.get(frame, default_T))
        diff = abs(h0 - a_val)
        rhs = u + a_u + T
        hold = diff <= rhs
        rows.append({
            "label": r["label"],
            "frame": frame,
            "anchor_id": anchor.get("anchor_id","UHA"),
            "diff": diff, "rhs": rhs, "gap": diff - rhs,
            "holds": bool(hold), "T_used": T,
            "H0": h0, "U": u, "anchor_value": a_val, "anchor_U": a_u
        })
    res = pd.DataFrame(rows)
    summary = {
        "anchor": {
            "anchor_id": anchor.get("anchor_id"),
            "quantity": anchor.get("quantity"),
            "value": a_val, "u": a_u, "units": anchor.get("units"),
            "frame": anchor.get("frame")
        },
        "counts": {
            "n": int(len(res)),
            "holds": int(res["holds"].sum()),
            "fails": int((~res["holds"]).sum())
        }
    }
    return summary, res
