#!/usr/bin/env python3
"""Run the complete JKN-MBG reproducibility pipeline in manuscript order."""

from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
SCRIPTS = [
    "01_construct_monthly_jkn.py",
    "02_descriptive_analysis.py",
    "03_block_bootstrap.py",
    "04_monte_carlo_thresholds.py",
    "05_reserve_resilience.py",
    "06_2026_stress_test.py",
    "07_make_figures.py",
]


def main():
    start = time.time()
    print("Reproducing JKN-MBG fiscal-space analysis\n")

    for script in SCRIPTS:
        path = ROOT / "src" / script
        print("=" * 78)
        print(f"Running {script}")
        subprocess.run([sys.executable, str(path)], cwd=ROOT, check=True)

    print("=" * 78)
    print(f"Completed successfully in {time.time() - start:.1f} seconds.")
    print("\nFinal figures:")
    for name in [
        "Figure_1_JKN_Monthly_Financing_2024_2025_600dpi.tif",
        "Figure_1_JKN_Monthly_Financing_2024_2025.eps",
        "Figure_2_Efficiency_Threshold_90pct_600dpi.tif",
        "Figure_2_Efficiency_Threshold_90pct.eps",
        "Figure_3_Fund_Resilience_Scenarios_600dpi.tif",
        "Figure_3_Fund_Resilience_Scenarios.eps",
    ]:
        print(f"  outputs/figures/{name}")


if __name__ == "__main__":
    main()
