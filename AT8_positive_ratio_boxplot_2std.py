import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

df = pd.read_csv("AT8_roi_noncell_summary_new.csv")

groups = ["PS19", "Control"]
colors = {"PS19": "#66C2A5", "Control": "#FC8D62"}
metric = "AT8_positive_ratio_2std"

data_by_group = [df.loc[df["group"] == g, metric].values for g in groups]

f_stat, anova_p = stats.f_oneway(*data_by_group)
h_stat, kw_p = stats.kruskal(*data_by_group)

fig, ax = plt.subplots(figsize=(6, 5))

bp = ax.boxplot(
    data_by_group,
    positions=[1, 2],
    widths=0.6,
    patch_artist=True,
    showfliers=False,
    medianprops=dict(color="black", linewidth=1.5),
    whiskerprops=dict(color="black"),
    capprops=dict(color="black"),
)

for patch, grp in zip(bp["boxes"], groups):
    patch.set_facecolor(colors[grp])
    patch.set_alpha(0.7)

rng = np.random.default_rng(42)
for i, grp in enumerate(groups):
    vals = data_by_group[i]
    jitter = rng.uniform(-0.15, 0.15, size=len(vals))
    ax.scatter(
        np.full_like(vals, i + 1) + jitter,
        vals,
        color="gray",
        alpha=0.5,
        s=20,
        zorder=3,
    )

ax.set_xticks([1, 2])
ax.set_xticklabels(groups, fontsize=12)
ax.set_ylabel("AT8 Positive Ratio", fontsize=12)
ax.set_xlabel("Group", fontsize=12)
ax.set_title(
    f"AT8 Positive Ratio by Group\n"
    f"ANOVA p = {anova_p:.2e}, Kruskal-Wallis p = {kw_p:.2e}",
    fontsize=12,
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
fig.savefig("AT8_positive_ratio_boxplot_2std.png", dpi=300, bbox_inches="tight")
plt.show()
