#!/usr/bin/env python3
"""Monte Carlo threshold analysis under historical JKN financing uncertainty."""

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "jkn_monthly_2024_2025.csv"
OUT = ROOT / "outputs" / "tables" / "japp_threshold_sensitivity.csv"

SEED = 20260809
N_SIM = 250_000
HORIZON = 12
BLOCK_LENGTHS = [2, 3, 4, 6]
TRANSFER_RATES = [0.25, 0.50, 0.75, 1.00]
PROB_LEVELS = [0.50, 0.80, 0.90, 0.95]
EFF_GRID = np.arange(0.05, 0.501, 0.005)
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


def threshold_from_probabilities(eff_grid, probs, target):
    idx = np.flatnonzero(probs >= target)
    return float(eff_grid[idx[0]]) if len(idx) else np.nan


def main():
    df = pd.read_csv(DATA)
    gaps = df["gap"].to_numpy()

    rng = np.random.default_rng(SEED)
    nonfood_share = rng.uniform(5/15, 5/13, N_SIM)

    rows = []
    for L in BLOCK_LENGTHS:
        annual_gap = circular_block_bootstrap(gaps, L, N_SIM, HORIZON, rng)

        for transfer in TRANSFER_RATES:
            probs = []
            for efficiency in EFF_GRID:
                transferable_savings = MBG_BUDGET * nonfood_share * efficiency * transfer
                probs.append(np.mean(transferable_savings >= annual_gap))
            probs = np.asarray(probs)

            for target in PROB_LEVELS:
                rows.append({
                    "Block": L,
                    "Transfer rate": transfer,
                    "Coverage probability": target,
                    "Required non-food efficiency": threshold_from_probabilities(
                        EFF_GRID, probs, target
                    ),
                })

    out = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print(out.to_string(index=False))
    print(f"\nWrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
