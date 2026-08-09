#!/usr/bin/env python3
"""2026 current-stress threshold and reserve-resilience analyses.

The 2026 inputs are stress-scenario ranges, not forecasts:
- claims: Rp16.0-16.5 T/month
- financing gap: Rp2.0-2.5 T/month
"""

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "jkn_monthly_2024_2025.csv"
THRESH_OUT = ROOT / "outputs" / "tables" / "japp_2026_stress_thresholds.csv"
RESERVE_OUT = ROOT / "outputs" / "tables" / "japp_secondary_outcomes_2026_stress.csv"

SEED = 20260809
N_SIM = 250_000
HORIZON = 12
BLOCK_LENGTHS = [2, 3, 4, 6]
EFF_GRID = np.arange(0.05, 0.501, 0.005)
TRANSFER_RATES = [0.25, 0.50, 0.75, 1.00]
PROB_LEVELS = [0.50, 0.80, 0.90, 0.95]
MBG_BUDGET = 248.0
STARTING_NET_ASSETS = 33.17


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


def paired_circular_bootstrap(claims, gaps, block_len, n_sim, horizon, rng):
    pairs = np.column_stack([claims, gaps])
    n = len(pairs)
    blocks = np.array([
        [pairs[(i + j) % n] for j in range(block_len)]
        for i in range(n)
    ])
    n_blocks = int(np.ceil(horizon / block_len))
    idx = rng.integers(0, n, size=(n_sim, n_blocks))
    return blocks[idx].reshape(n_sim, n_blocks * block_len, 2)[:, :horizon, :]


def threshold_table(df):
    # Reproduce the same random-stream order used in the historical threshold analysis.
    rng = np.random.default_rng(SEED)
    nonfood_share = rng.uniform(5/15, 5/13, N_SIM)
    gaps = df["gap"].to_numpy()

    for L in BLOCK_LENGTHS:
        _ = circular_block_bootstrap(gaps, L, N_SIM, HORIZON, rng)

    stress_gap = rng.uniform(2.0, 2.5, N_SIM) * HORIZON

    rows = []
    for transfer in TRANSFER_RATES:
        probs = []
        for efficiency in EFF_GRID:
            savings = MBG_BUDGET * nonfood_share * efficiency * transfer
            probs.append(np.mean(savings >= stress_gap))
        probs = np.asarray(probs)

        for target in PROB_LEVELS:
            idx = np.flatnonzero(probs >= target)
            threshold = EFF_GRID[idx[0]] if len(idx) else np.nan
            rows.append({
                "Transfer rate": f"{int(transfer*100)}%",
                "Coverage probability": f"{int(target*100)}%",
                "Required non-food efficiency (%)": (
                    np.nan if np.isnan(threshold) else round(float(100*threshold), 1)
                ),
            })
    return pd.DataFrame(rows)


def reserve_table(df):
    # Reproduce the random-stream order used for the reserve analysis.
    rng = np.random.default_rng(SEED)
    traj = paired_circular_bootstrap(
        df["claim"].to_numpy(),
        df["gap"].to_numpy(),
        3,
        N_SIM,
        HORIZON,
        rng,
    )
    nonfood_share = rng.uniform(5/15, 5/13, N_SIM)

    stress_monthly_claim = rng.uniform(16.0, 16.5, N_SIM)
    stress_monthly_gap = rng.uniform(2.0, 2.5, N_SIM)
    stress_annual_gap = stress_monthly_gap * HORIZON

    rows = []
    for efficiency in [0.20, 0.30, 0.40]:
        gross = MBG_BUDGET * nonfood_share * efficiency
        for transfer_rate in [0.50, 0.75, 1.00]:
            transfer = gross * transfer_rate
            end_assets = STARTING_NET_ASSETS - stress_annual_gap + transfer
            resilience = end_assets / stress_monthly_claim

            rows.append({
                "Non-food efficiency": f"{int(efficiency*100)}%",
                "Transferred": f"{int(transfer_rate*100)}%",
                "Median end assets (Rp T)": round(float(np.median(end_assets)), 2),
                "Median resilience (months)": round(float(np.median(resilience)), 2),
                "P(resilience >= 3 months)": f"{100*np.mean(resilience >= 3):.1f}%",
                "P(end assets < 0)": f"{100*np.mean(end_assets < 0):.1f}%",
            })
    return pd.DataFrame(rows)


def main():
    df = pd.read_csv(DATA)
    THRESH_OUT.parent.mkdir(parents=True, exist_ok=True)

    thresholds = threshold_table(df)
    thresholds.to_csv(THRESH_OUT, index=False)

    reserve = reserve_table(df)
    reserve.to_csv(RESERVE_OUT, index=False)

    print("2026 stress thresholds")
    print(thresholds.to_string(index=False))
    print("\n2026 stress reserve outcomes")
    print(reserve.to_string(index=False))
    print(f"\nWrote {THRESH_OUT.relative_to(ROOT)}")
    print(f"Wrote {RESERVE_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
