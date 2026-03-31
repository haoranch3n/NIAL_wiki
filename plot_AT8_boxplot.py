#!/usr/bin/env python3
"""Generate AT8 Positive Ratio boxplot by Group with statistical tests."""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from pathlib import Path

CSV_PATH = "/media/core/core_operations/ImageAnalysis/Core/Haoran/core_projects/multi-scale-cellpose/output_Jimin_20X/AT8_roi_noncell_summary_new.csv"
OUTPUT_DIR = Path(__file__).parent
OUTPUT_PATH = OUTPUT_DIR / "AT8_positive_ratio_boxplot_2std.png"

df = pd.read_csv(CSV_PATH)

groups = ["PS19", "Control"]
data_by_group = [df.loc[df["group"] == g, "AT8_positive_ratio_2std"].values for g in groups]

f_stat, anova_p = stats.f_oneway(*data_by_group)
kw_stat, kw_p = stats.kruskal(*data_by_group)

colors = ["#66C2A5", "#FC8D62"]

fig, ax = plt.subplots(figsize=(7, 5))

bp = ax.boxplot(data_by_group, positions=[1, 2], widths=0.6, patch_artist=True,
                medianprops=dict(color="black", linewidth=1.5),
                whiskerprops=dict(color="black"),
                capprops=dict(color="black"),
                flierprops=dict(marker="none"))

for patch, color in zip(bp["boxes"], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

for i, (g, color) in enumerate(zip(groups, colors)):
    vals = data_by_group[i]
    x = np.random.normal(i + 1, 0.08, size=len(vals))
    ax.scatter(x, vals, alpha=0.5, color="gray", s=20, zorder=3, edgecolors="none")

ax.set_xticks([1, 2])
ax.set_xticklabels(groups, fontsize=12, rotation=45)
ax.set_ylabel("AT8 Positive Ratio", fontsize=13)
ax.set_xlabel("Group", fontsize=13)
ax.set_title(
    f"AT8 Positive Ratio by Group\n"
    f"ANOVA p = {anova_p:.2e}, Kruskal\u2013Wallis p = {kw_p:.2e}",
    fontsize=13,
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=150, bbox_inches="tight")
print(f"Saved: {OUTPUT_PATH}")
