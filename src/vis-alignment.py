
# --------------------- Alignment visualization ---------------------

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

FIG_DIR = OUT / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Load results written by the main analysis.
edge_alignment = pd.read_csv(OUT / "edge_alignment.csv")
nonedges = pd.read_csv(OUT / "sampled_non_edges.csv")

edge_alignment["has_shared_publication"] = (
    edge_alignment["shared_publications"] > 0
)
nonedges["has_shared_publication"] = (
    nonedges["shared_publications"] > 0
)

edge_rate = edge_alignment["has_shared_publication"].mean()
nonedge_rate = nonedges["has_shared_publication"].mean()

# Figure 1: Fraction of pairs with bibliographic overlap.
fig, ax = plt.subplots(figsize=(6.5, 4.5))

labels = ["Expert-defined edges", "Sampled non-edges"]
rates = [edge_rate, nonedge_rate]
bars = ax.bar(labels, rates, width=0.58)

ax.yaxis.set_major_formatter(PercentFormatter(1.0))
ax.set_ylabel("Pairs sharing ≥1 publication")
ax.set_title("Expert–literature alignment")
ax.set_ylim(0, min(1.0, max(rates) * 1.25 + 0.05))
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)

for bar, rate, n in zip(
    bars,
    rates,
    [len(edge_alignment), len(nonedges)],
):
    ax.annotate(
        f"{rate:.1%}\n(n={n:,})",
        (bar.get_x() + bar.get_width() / 2, bar.get_height()),
        xytext=(0, 5),
        textcoords="offset points",
        ha="center",
        va="bottom",
    )

fig.tight_layout()
fig.savefig(FIG_DIR / "alignment_overlap_rate.pdf", bbox_inches="tight")
fig.savefig(FIG_DIR / "alignment_overlap_rate.png", dpi=300, bbox_inches="tight")
plt.close(fig)

# Figure 2: Distribution of shared-publication counts.
# Use log-scaled counts to show both the large mass at zero and the tail.
edge_counts = edge_alignment["shared_publications"].clip(lower=0)
nonedge_counts = nonedges["shared_publications"].clip(lower=0)

fig, ax = plt.subplots(figsize=(7, 4.5))

bins = np.arange(
    0,
    max(
        int(edge_counts.max()) if len(edge_counts) else 0,
        int(nonedge_counts.max()) if len(nonedge_counts) else 0,
    ) + 2,
) - 0.5

if len(bins) > 80:
    # Keep the histogram legible for long-tailed distributions.
    upper = max(edge_counts.quantile(0.99), nonedge_counts.quantile(0.99))
    upper = max(1, int(np.ceil(upper)))
    bins = np.arange(0, upper + 2) - 0.5

ax.hist(
    edge_counts,
    bins=bins,
    density=True,
    alpha=0.6,
    label="Expert-defined edges",
)
ax.hist(
    nonedge_counts,
    bins=bins,
    density=True,
    alpha=0.6,
    label="Sampled non-edges",
)

ax.set_yscale("log")
ax.set_xlabel("Number of shared publications")
ax.set_ylabel("Fraction of software pairs (log scale)")
ax.set_title("Distribution of bibliographic overlap")
ax.legend(frameon=False)
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)

fig.tight_layout()
fig.savefig(FIG_DIR / "alignment_shared_publications.pdf", bbox_inches="tight")
fig.savefig(FIG_DIR / "alignment_shared_publications.png", dpi=300, bbox_inches="tight")
plt.close(fig)

# Print the exact statistics represented by Figure 1.
print("\nFIGURE STATISTICS")
print("-----------------")
print(f"Expert-edge overlap: {edge_rate:.2%} "
      f"({edge_alignment['has_shared_publication'].sum():,}/"
      f"{len(edge_alignment):,})")
print(f"Sampled non-edge overlap: {nonedge_rate:.2%} "
      f"({nonedges['has_shared_publication'].sum():,}/"
      f"{len(nonedges):,})")
print(f"Absolute difference: {edge_rate - nonedge_rate:.2%}")
print(f"Figures saved in: {FIG_DIR.resolve()}")
