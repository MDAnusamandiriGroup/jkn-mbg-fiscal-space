#!/usr/bin/env python3
"""Generate the manuscript figures using the exact filenames stored in outputs/figures/."""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "jkn_monthly_2024_2025.csv"
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"

SEED = 20260809
N_SIM = 250_000
HORIZON = 12
STARTING_NET_ASSETS = 33.17
MBG_BUDGET = 248.0

# Exact final output names.
F1_TIF = FIGURES / "Figure_1_JKN_Monthly_Financing_2024_2025_600dpi.tif"
F1_EPS = FIGURES / "Figure_1_JKN_Monthly_Financing_2024_2025.eps"
F2_TIF = FIGURES / "Figure_2_Efficiency_Threshold_90pct_600dpi.tif"
F2_EPS = FIGURES / "Figure_2_Efficiency_Threshold_90pct.eps"
F3_TIF = FIGURES / "Figure_3_Fund_Resilience_Scenarios_600dpi.tif"
F3_EPS = FIGURES / "Figure_3_Fund_Resilience_Scenarios.eps"


def save_figure(fig, tif_path, eps_path):
    # TIFF for journal submission; EPS retained as vector master.
    fig.savefig(
        tif_path,
        dpi=600,
        format="tiff",
        pil_kwargs={"compression": "tiff_lzw"},
        bbox_inches="tight",
        facecolor="white",
    )
    fig.savefig(
        eps_path,
        format="eps",
        bbox_inches="tight",
        facecolor="white",
    )
    plt.close(fig)


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


def figure_1(df):
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.plot(
        df["month"], df["iuran"],
        marker="o", linewidth=1.6,
        label="Contribution revenue",
    )
    ax.plot(
        df["month"], df["claim"],
        marker="s", linewidth=1.6, linestyle="--",
        label="Benefit expenditure",
    )
    ax.set_ylabel("Rp trillion per month")
    ax.set_xlabel("")
    ax.set_title("Monthly JKN contribution revenue and benefit expenditure, 2024–2025")
    ax.legend(frameon=False)
    ax.grid(alpha=0.2)
    fig.autofmt_xdate(rotation=45)
    fig.tight_layout()
    save_figure(fig, F1_TIF, F1_EPS)


def figure_2():
    historical = pd.read_csv(TABLES / "japp_threshold_sensitivity.csv")
    stress = pd.read_csv(TABLES / "japp_2026_stress_thresholds.csv")

    transfer_rates = [0.25, 0.50, 0.75, 1.00]

    hist90 = []
    for tr in transfer_rates:
        row = historical[
            (historical["Block"] == 3)
            & (historical["Transfer rate"] == tr)
            & (historical["Coverage probability"] == 0.90)
        ]
        val = row["Required non-food efficiency"].iloc[0]
        hist90.append(np.nan if pd.isna(val) else 100 * val)

    stress90 = []
    for tr in transfer_rates:
        row = stress[
            (stress["Transfer rate"] == f"{int(tr*100)}%")
            & (stress["Coverage probability"] == "90%")
        ]
        val = row["Required non-food efficiency (%)"].iloc[0]
        stress90.append(np.nan if pd.isna(val) else float(val))

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    x = np.arange(len(transfer_rates))
    ax.plot(x, hist90, marker="o", linewidth=1.6, label="Historical bootstrap")
    ax.plot(
        x, stress90, marker="s", linestyle="--", linewidth=1.6,
        label="2026 current-stress scenario",
    )
    ax.set_xticks(x, [f"{int(t*100)}%" for t in transfer_rates])
    ax.set_xlabel("Share of MBG savings transferred to JKN")
    ax.set_ylabel("Required non-food efficiency (%)")
    ax.set_title("Efficiency threshold for 90% probability of covering the JKN financing gap")
    ax.legend(frameon=False)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    save_figure(fig, F2_TIF, F2_EPS)


def figure_3(df):
    rng = np.random.default_rng(SEED)
    traj = paired_circular_bootstrap(
        df["claim"].to_numpy(),
        df["gap"].to_numpy(),
        3,
        N_SIM,
        HORIZON,
        rng,
    )
    annual_claims = traj[:, :, 0].sum(axis=1)
    annual_gap = traj[:, :, 1].sum(axis=1)
    mean_monthly_claim = annual_claims / HORIZON
    nonfood_share = rng.uniform(5/15, 5/13, N_SIM)

    scenarios = {
        "No transfer": (
            STARTING_NET_ASSETS - annual_gap
        ) / mean_monthly_claim,
        "20% efficiency,\n50% transfer": (
            STARTING_NET_ASSETS - annual_gap
            + MBG_BUDGET * nonfood_share * 0.20 * 0.50
        ) / mean_monthly_claim,
        "20% efficiency,\n100% transfer": (
            STARTING_NET_ASSETS - annual_gap
            + MBG_BUDGET * nonfood_share * 0.20
        ) / mean_monthly_claim,
        "30% efficiency,\n100% transfer": (
            STARTING_NET_ASSETS - annual_gap
            + MBG_BUDGET * nonfood_share * 0.30
        ) / mean_monthly_claim,
    }

    labels = list(scenarios)
    medians = np.array([np.median(v) for v in scenarios.values()])
    lo = np.array([np.quantile(v, .025) for v in scenarios.values()])
    hi = np.array([np.quantile(v, .975) for v in scenarios.values()])
    yerr = np.vstack([medians - lo, hi - medians])

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    x = np.arange(len(labels))
    ax.errorbar(x, medians, yerr=yerr, fmt="o", capsize=4, linewidth=1.3)
    ax.axhline(1, linestyle=":", linewidth=1)
    ax.axhline(3, linestyle="--", linewidth=1)
    ax.set_xticks(x, labels)
    ax.set_ylabel("Fund resilience (months of claims)")
    ax.set_title("Simulated JKN fund resilience under selected reallocation scenarios")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    save_figure(fig, F3_TIF, F3_EPS)


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA)
    df["month"] = pd.to_datetime(df["month"])

    figure_1(df)
    figure_2()
    figure_3(df)

    print("Generated:")
    for p in [F1_TIF, F1_EPS, F2_TIF, F2_EPS, F3_TIF, F3_EPS]:
        print(f"  {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
