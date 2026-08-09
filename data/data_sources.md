# Data sources

This repository contains a reconstructed monthly JKN financing series used for the manuscript:

**Competing Social Priorities under Fiscal Constraints: A Probabilistic Counterfactual Analysis of Nutrition Spending and Universal Health Coverage in Indonesia**

## Primary JKN data

### Dewan Jaminan Sosial Nasional (DJSN)

Monthly JKN monitoring reports were used to extract cumulative year-to-date values for:

- contribution revenue (`pendapatan iuran`);
- benefit expenditure (`beban jaminan`);
- claim ratios;
- DJS Kesehatan net assets; and
- fund resilience, where reported.

Primary public sources include:

- DJSN Monthly Report Monitoring JKN, 31 December 2024  
  https://kesehatan.djsn.go.id/kesehatan/doc/laporan-bulanan/Monthly_Report_JKN_12_2024.pdf

- DJSN Monthly Report Monitoring JKN, 30 November 2025  
  https://kesehatan.djsn.go.id/kesehatan/doc/laporan-bulanan/Monthly_Report_JKN_11_2025.pdf

Monthly contribution and benefit-expenditure flows were reconstructed by differencing consecutive cumulative year-to-date observations. The analysis uses 22 consecutive reconstructed monthly observations from March 2024 to December 2025. January and February 2024 were not separated because the earliest public cumulative reporting did not permit reliable reconstruction of the two months individually. No imputation was used.

The financing gap is defined as:

`gap_t = benefit_expenditure_t - contribution_revenue_t`

Positive values therefore indicate that monthly benefit expenditure exceeded monthly contribution revenue.

## MBG budget and cost structure

### Badan Gizi Nasional (BGN)

The baseline analysis uses the narrower 2026 BGN-reported allocation of **Rp248 trillion specifically for MBG** within BGN's Rp268 trillion institutional budget.

Source:

- Kepala BGN: Pagu anggaran tahun ini 95,4 persennya untuk program pemenuhan gizi nasional  
  https://www.bgn.go.id/news/siaran-pers/kepala-bgn-pagu-anggaran-tahun-ini-954-persennya-untuk-program-pemenuhan-gizi-nasional

BGN also reported two per-portion cost structures:

- Rp13,000 total = Rp8,000 food + Rp3,000 operations + Rp2,000 facilities;
- Rp15,000 total = Rp10,000 food + Rp3,000 operations + Rp2,000 facilities.

Source:

- BGN ingatkan anggaran bahan makan MBG Rp8.000-Rp10.000, bukan Rp15.000  
  https://bgn.go.id/news/siaran-pers/bgn-ingatkan-anggaran-bahan-makan-mbg-rp8000-rp10000-bukan-rp15000

These imply documented non-food expenditure shares of:

- 5,000 / 15,000 = 33.33%;
- 5,000 / 13,000 = 38.46%.

The Monte Carlo model represents uncertainty in the realised national mix using a bounded uniform distribution between these two documented endpoints. Endpoint sensitivity analyses should also be reported.

The simulation **does not reduce the food allocation**. Efficiency scenarios apply only to the non-food component.

## 2026 current-stress scenario

A separate current-stress scenario uses mid-2026 financing conditions reported by BPJS Kesehatan to Commission IX of the Indonesian House of Representatives:

- claims: approximately Rp16-16.5 trillion per month;
- contributions: approximately Rp14 trillion per month;
- implied financing gap: approximately Rp2-2.5 trillion per month.

Source:

- DPR RI, 14 June 2026, *Jangan terus menerus tambal sulam JKN BPJS Kesehatan demi tutup defisit Rp2 triliun*  
  https://emedia.dpr.go.id/news/2026/06/14/jangan-terus-menerus-tambal-sulam-jkn-bpjs-kesehatan-demi-tutup-defisit-rp2-triliun

This is treated as a **stress scenario, not a forecast**.

## Licensing note

The reconstructed CSV is derived from publicly available Indonesian government reports. The MIT License in this repository applies to the repository's original code and documentation only. It does not relicense third-party source data or government publications. Users should consult the original sources for their applicable terms and authoritative values.
