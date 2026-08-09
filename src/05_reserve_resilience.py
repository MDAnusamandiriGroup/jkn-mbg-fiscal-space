#!/usr/bin/env python3
"""Historical counterfactual analysis of DJS Kesehatan net assets and fund resilience."""

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "jkn_monthly_2024_2025.csv"
OUT = ROOT / "outputs" / "tables" / "japp_secondary_outcomes_resilience.csv"

SEED = 20260809
N_SIM = 250_000
HORIZON = 12
BLOCK_LENGTH = 3
STARTING_NET_ASSETS = 33.17  # Rp T, Nov 2025
MBG_BUDGET = 248.0
EFFICIENCIES = [0.10, 0.20, 0.30, 0.40]
TRANSFER_RATES = [0.25, 0.50, 0.75, 1.00]


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


def historical_simulation():
    df = pd.read_csv(DATA)
    rng = np.random.default_rng(SEED)

    traj = paired_circular_bootstrap(
        df["claim"].to_numpy(),
        df["gap"].to_numpy(),
        BLOCK_LENGTH,
        N_SIM,
        HORIZON,
        rng,
    )
    annual_claims = traj[:, :, 0].sum(axis=1)
    annual_gap = traj[:, :, 1].sum(axis=1)
    mean_monthly_claim = annual_claims / HORIZON
    nonfood_share = rng.uniform(5/15, 5/13, N_SIM)

    return annual_gap, mean_monthly_claim, nonfood_share


def main():
    annual_gap, mean_monthly_claim, nonfood_share = historical_simulation()

    rows = []
    for efficiency in EFFICIENCIES:
        gross_saving = MBG_BUDGET * nonfood_share * efficiency

        for transfer_rate in TRANSFER_RATES:
            transfer = gross_saving * transfer_rate
            end_assets = STARTING_NET_ASSETS - annual_gap + transfer
            resilience = end_assets / mean_monthly_claim

            rows.append({
                "Non-food efficiency": f"{int(efficiency*100)}%",
                "Share saving transferred": f"{int(transfer_rate*100)}%",
                "Median transfer (Rp T)": round(float(np.median(transfer)), 2),
                "Median end net assets (Rp T)": round(float(np.median(end_assets)), 2),
                "Median fund resilience (months)": round(float(np.median(resilience)), 2),
                "P(end assets < 0)": f"{100*np.mean(end_assets < 0):.1f}%",
                "P(resilience < 1 month)": f"{100*np.mean(resilience < 1):.1f}%",
                "P(resilience >= 3 months)": f"{100*np.mean(resilience >= 3):.1f}%",
            })

    out = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print(out.to_string(index=False))

    # Useful baseline check reported in the manuscript.
    baseline_assets = STARTING_NET_ASSETS - annual_gap
    baseline_resilience = baseline_assets / mean_monthly_claim
    print("\nNo-transfer baseline:")
    print(f"  median ending assets = {np.median(baseline_assets):.2f} Rp T")
    print(f"  median resilience    = {np.median(baseline_resilience):.2f} months")
    print(f"  P(resilience < 1)    = {100*np.mean(baseline_resilience < 1):.1f}%")
    print(f"\nWrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
