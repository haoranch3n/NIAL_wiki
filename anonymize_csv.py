"""
Generate a synthetic, publicly shareable version of AT8_roi_noncell_summary_new.csv.

Strategy:
  - sample_id: replaced with arbitrary sequential IDs (per original ID)
  - group, age: kept as-is (generic categorical labels, not identifying)
  - Numeric columns: perturbed by adding Gaussian noise scaled to each
    column's within-group std (default ±10%), then clipped to stay within
    plausible bounds. This preserves group-level distributions while making
    individual rows non-recoverable.
  - Ratio columns (0–1): clipped to [0, 1] after perturbation.
  - Count/voxel columns: rounded to int and clipped to ≥0.
"""

import pandas as pd
import numpy as np

NOISE_SCALE = 0.10  # fraction of within-group std used as noise magnitude
SEED = 2026

rng = np.random.default_rng(SEED)
df = pd.read_csv("AT8_roi_noncell_summary_new.csv")

# --- 1. Anonymize sample IDs ---
unique_ids = df["sample_id"].unique()
rng.shuffle(unique_ids)
id_map = {orig: f"S{i+1:03d}" for i, orig in enumerate(unique_ids)}
df["sample_id"] = df["sample_id"].map(id_map)

# --- 2. Classify numeric columns ---
ratio_cols = [c for c in df.columns if "ratio" in c.lower()]
count_cols = ["n_roi_noncell_voxels", "n_roi_noncell_nonzero",
              "total_cells", "AT8_positive_cells_2std",
              "AT8_positive_cells_mean", "AT8_positive_cells_1std"]
continuous_cols = ["mean_AT8", "std_AT8", "median_AT8"]
numeric_cols = ratio_cols + count_cols + continuous_cols

# --- 3. Perturb each numeric column (noise scaled per group) ---
for col in numeric_cols:
    noise = np.zeros(len(df))
    for grp in df["group"].unique():
        mask = df["group"] == grp
        group_std = df.loc[mask, col].std()
        noise[mask] = rng.normal(0, NOISE_SCALE * group_std, size=mask.sum())
    df[col] = df[col] + noise

# --- 4. Enforce plausible bounds ---
for col in ratio_cols:
    df[col] = df[col].clip(0, 1)

for col in count_cols:
    df[col] = df[col].clip(0).round().astype(int)

for col in continuous_cols:
    df[col] = df[col].clip(0).round(2)

# --- 5. Keep only columns used by the boxplot ---
df = df[["group", "AT8_positive_ratio_2std"]]

# --- 6. Save ---
out = "AT8_roi_noncell_summary_synthetic.csv"
df.to_csv(out, index=False)
print(f"Saved {out}  ({len(df)} rows)")
print(f"\nSample ID mapping (first 5): {dict(list(id_map.items())[:5])}")
print(f"\nHead of synthetic data:\n{df.head()}")
