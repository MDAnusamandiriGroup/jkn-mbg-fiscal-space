#!/usr/bin/env python3
"""Reconstruct monthly JKN financing flows from official cumulative YTD values.

Output
------
data/jkn_monthly_2024_2025.csv

The 2024 public series begins with a Feb-2024 cumulative value. Feb is used only
as the baseline for differencing; the analytical monthly series begins in Mar-2024.
No Jan-Feb 2024 monthly split is imputed.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "jkn_monthly_2024_2025.csv"

# Rp trillion. Values transcribed from the DJSN monitoring reports used in the paper.
YTD_2024 = pd.DataFrame({
    "month": pd.to_datetime([
        "2024-02-01","2024-03-01","2024-04-01","2024-05-01","2024-06-01",
        "2024-07-01","2024-08-01","2024-09-01","2024-10-01","2024-11-01",
        "2024-12-01"
    ]),
    "iuran_ytd": [25.70,38.60,52.30,66.10,80.68,94.84,108.90,122.57,133.45,150.30,165.25],
    "claim_ytd": [28.80,43.30,57.40,71.93,87.08,101.82,117.38,131.78,146.28,160.07,175.07],
})

YTD_2025 = pd.DataFrame({
    "month": pd.to_datetime([
        "2025-01-01","2025-02-01","2025-03-01","2025-04-01","2025-05-01",
        "2025-06-01","2025-07-01","2025-08-01","2025-09-01","2025-10-01",
        "2025-11-01","2025-12-01"
    ]),
    "iuran_ytd": [12.90,27.66,41.88,56.46,71.20,85.40,100.04,115.04,129.90,144.56,159.75,176.70],
    "claim_ytd": [14.60,29.68,47.00,60.18,75.60,91.20,107.28,123.39,139.40,156.10,172.59,192.70],
})


def reconstruct() -> pd.DataFrame:
    # 2024: Feb is baseline only; monthly analytical observations begin in March.
    d24 = YTD_2024.copy()
    d24["iuran"] = d24["iuran_ytd"].diff()
    d24["claim"] = d24["claim_ytd"].diff()
    d24 = d24.iloc[1:].copy()

    # 2025: January YTD is itself January's monthly value.
    d25 = YTD_2025.copy()
    d25["iuran"] = d25["iuran_ytd"].diff()
    d25["claim"] = d25["claim_ytd"].diff()
    d25.loc[d25.index[0], "iuran"] = d25.loc[d25.index[0], "iuran_ytd"]
    d25.loc[d25.index[0], "claim"] = d25.loc[d25.index[0], "claim_ytd"]

    monthly = pd.concat([
        d24[["month","iuran","claim"]],
        d25[["month","iuran","claim"]],
    ], ignore_index=True)

    # Keep monetary values at the precision available in the source reports.
    monthly["iuran"] = monthly["iuran"].round(2)
    monthly["claim"] = monthly["claim"].round(2)
    monthly["gap"] = (monthly["claim"] - monthly["iuran"]).round(2)
    monthly["claim_ratio"] = monthly["claim"] / monthly["iuran"]
    monthly["month"] = monthly["month"].dt.strftime("%Y-%m")
    return monthly


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = reconstruct()
    df.to_csv(OUT, index=False)
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(df)} monthly observations).")
    print(f"2025 totals: iuran={df.loc[df.month.str.startswith('2025'),'iuran'].sum():.2f}, "
          f"claims={df.loc[df.month.str.startswith('2025'),'claim'].sum():.2f} Rp T")


if __name__ == "__main__":
    main()
