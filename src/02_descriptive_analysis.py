#!/usr/bin/env python3
"""Create descriptive statistics for the reconstructed monthly JKN series."""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "jkn_monthly_2024_2025.csv"
OUT = ROOT / "outputs" / "tables" / "japp_descriptive_summary.csv"


def main():
    df = pd.read_csv(DATA)
    df["month"] = pd.to_datetime(df["month"])

    rows = []
    for label, d in [
        ("Mar 2024-Dec 2025", df),
        ("2024 (Mar-Dec)", df[df["month"].dt.year == 2024]),
        ("2025", df[df["month"].dt.year == 2025]),
    ]:
        rows.append({
            "Period": label,
            "Months": len(d),
            "Contribution revenue (Rp T)": round(d["iuran"].sum(), 2),
            "Benefit expenditure (Rp T)": round(d["claim"].sum(), 2),
            "Financing gap (Rp T)": round(d["gap"].sum(), 2),
            "Mean monthly gap (Rp T)": round(d["gap"].mean(), 2),
            "Median monthly gap (Rp T)": round(d["gap"].median(), 2),
            "Months with positive gap": int((d["gap"] > 0).sum()),
            "Mean monthly claim ratio": round(d["claim_ratio"].mean(), 4),
        })

    out = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print(out.to_string(index=False))
    print(f"\nWrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
