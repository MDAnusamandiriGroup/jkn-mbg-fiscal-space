#!/usr/bin/env python3
"""Moving-block bootstrap robustness analysis for 12-month JKN financing gaps."""

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "jkn_monthly_2024_2025.csv"
OUT = ROOT / "outputs" / "tables" / "japp_bootstrap_robustness.csv"

SEED = 20260809
N_SIM = 250_000
HORIZON = 12
BLOCK_LENGTHS = [2, 3, 4, 6]
MBG_BUDGET = 248.0


def circular_block_bootstrap(g, block_len, n_sim, horizon, rng):
    n = len(g)
    blocks = np.array([
        [g[(i + j) % n] for j in range(block_len)]
        for i in range(n)
    ])
    n_blocks = int(np.ceil(horizon / block_len))
    idx = rng.integers(0, n, size=(n_sim, n_blocks))
    trajectories = blocks[idx].reshape(n_sim, n_blocks * block_len)[:, :horizon]
    return trajectories.sum(axis=1)


def main():
    df = pd.read_csv(DATA)
    gaps = df["gap"].to_numpy()

    # Keep the random stream aligned with the manuscript simulation pipeline.
    rng = np.random.default_rng(SEED)
    _ = rng.uniform(5/15, 5/13, N_SIM)  # non-food-share draws used downstream

    rows = []
    for L in BLOCK_LENGTHS:
        annual_gap = circular_block_bootstrap(gaps, L, N_SIM, HORIZON, rng)
        rows.append({
            "Block length (months)": L,
            "Median 12m gap (Rp T)": round(float(np.median(annual_gap)), 2),
            "2.5th pct (Rp T)": round(float(np.quantile(annual_gap, .025)), 2),
            "97.5th pct (Rp T)": round(float(np.quantile(annual_gap, .975)), 2),
            "P(gap > 0)": round(float(100 * np.mean(annual_gap > 0)), 1),
        })

    out = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print(out.to_string(index=False))
    print(f"\nWrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
