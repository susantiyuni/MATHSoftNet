import matplotlib.pyplot as plt

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx


# ============================================================
# Configuration
# ============================================================

# Change this to the directory containing your output CSV files.
DATA_DIR = Path("data/processed")

# Figures will be saved here.
FIG_DIR = DATA_DIR / "figures"

FIG_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "axes.titlesize": 12,
    "axes.labelsize": 10,
})


# ============================================================
# CSV loading helpers
# ============================================================

def load_csv(filename, required=False):
    """Load a CSV; return an empty DataFrame if optional and missing."""
    path = DATA_DIR / filename

    if not path.exists():
        message = f"File not found: {path}"
        if required:
            raise FileNotFoundError(message)
        warnings.warn(message)
        return pd.DataFrame()

    df = pd.read_csv(path, low_memory=False)
    print(f"Loaded {filename}: {len(df):,} rows")
    return df


def normalize_id(series):
    """Normalize IDs as strings for consistent joins."""
    return series.astype("string").str.strip()


def nonempty(series):
    """Treat nulls, blank strings, and empty collections as missing."""
    def check(value):
        if value is None:
            return False

        if isinstance(value, (list, dict, tuple, set)):
            return len(value) > 0

        if pd.isna(value):
            return False

        if isinstance(value, str):
            return bool(value.strip())

        return True

    return series.map(check)


def save_figure(fig, filename):
    """Save and close a Matplotlib figure."""
    path = FIG_DIR / filename
    fig.savefig(path)
    plt.close(fig)
    print(f"Saved {path}")


# ============================================================
# Load all datasets directly
# ============================================================

software = load_csv("software.csv", required=True)
edges = load_csv("software_edges.csv", required=True)
communities = load_csv("software_communities.csv", required=True)
community_summary = load_csv("software_community_summary.csv")
pub_software = load_csv("software_publications.csv")
software_msc = load_csv("software_msc.csv")
software_summary = load_csv("software_summary.csv")
paper_lookup = load_csv("paper_lookup.csv")


# ============================================================
# Validate columns and normalize identifiers
# ============================================================

if not {"source", "target"}.issubset(edges.columns):
    raise ValueError(
        "software_edges.csv must contain 'source' and 'target' columns."
    )

if not {"software_id", "community_id"}.issubset(communities.columns):
    raise ValueError(
        "software_communities.csv must contain "
        "'software_id' and 'community_id'."
    )

for frame in [software, communities, software_summary, software_msc, pub_software]:
    if "software_id" in frame.columns:
        frame["software_id"] = normalize_id(frame["software_id"])

edges["source"] = normalize_id(edges["source"])
edges["target"] = normalize_id(edges["target"])

# Normalize the software IDs in publication links if present.
if not pub_software.empty:
    if "paper_id" not in pub_software.columns:
        # Some versions of the file may use publication_id.
        if "publication_id" in pub_software.columns:
            pub_software = pub_software.rename(
                columns={"publication_id": "paper_id"}
            )

    if "paper_id" in pub_software.columns:
        pub_software["paper_id"] = normalize_id(pub_software["paper_id"])

# Use one community assignment per software package.
community_assignments = (
    communities[["software_id", "community_id"]]
    .dropna(subset=["software_id", "community_id"])
    .drop_duplicates("software_id", keep="first")
)

# Use a simple software name lookup where available.
if {"software_id", "name"}.issubset(software.columns):
    name_map = (
        software.dropna(subset=["software_id"])
        .drop_duplicates("software_id")
        .set_index("software_id")["name"]
        .to_dict()
    )
else:
    name_map = {}


# ============================================================
# Build the graph
# ============================================================

G = nx.from_pandas_edgelist(
    edges.dropna(subset=["source", "target"]),
    source="source",
    target="target",
    create_using=nx.Graph(),
)

# Include software records with no network edges.
if "software_id" in software.columns:
    G.add_nodes_from(software["software_id"].dropna().unique())

# A simple undirected graph collapses repeated edges.
print("\nGraph overview")
print(f"Nodes: {G.number_of_nodes():,}")
print(f"Edges: {G.number_of_edges():,}")
print(f"Connected components: {nx.number_connected_components(G):,}")

degrees = pd.Series(dict(G.degree()), name="degree")


# ============================================================
# 1. Community size distribution
# ============================================================

if not community_assignments.empty:
    sizes = (
        community_assignments.groupby("community_id")["software_id"]
        .nunique()
        .sort_values(ascending=False)
    )

    if not sizes.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(np.arange(1, len(sizes) + 1), sizes.values)

        if (sizes > 0).all():
            ax.set_yscale("log")

        ax.set_xlabel("Community rank (largest to smallest)")
        ax.set_ylabel("Number of software packages")
        ax.set_title("Software community size distribution")
        save_figure(fig, "community_sizes.pdf")


# ============================================================
# 2. Network subgraph of high-degree software
# ============================================================

if G.number_of_nodes() > 0 and G.number_of_edges() > 0:
    top_nodes = (
        degrees.sort_values(ascending=False)
        .head(min(250, len(degrees)))
        .index.tolist()
    )

    H = G.subgraph(top_nodes).copy()

    community_map = (
        community_assignments.set_index("software_id")["community_id"]
        .astype(str)
        .to_dict()
    )

    node_communities = [
        community_map.get(node, "unassigned")
        for node in H.nodes()
    ]

    # Map community labels to categorical color indices.
    unique_communities = sorted(set(node_communities))
    community_index = {
        label: i for i, label in enumerate(unique_communities)
    }
    node_colors = [
        community_index[label] for label in node_communities
    ]

    pos = nx.spring_layout(
        H,
        seed=42,
        iterations=80,
    )

    fig, ax = plt.subplots(figsize=(12, 9))

    nx.draw_networkx_edges(
        H, pos, ax=ax, alpha=0.15, width=0.5
    )
    nx.draw_networkx_nodes(
        H,
        pos,
        ax=ax,
        node_size=20,
        node_color=node_colors,
        cmap=plt.cm.tab20,
    )

    ax.set_title(
        "High-degree software subgraph "
        "(up to 250 nodes; colors represent communities)"
    )
    ax.axis("off")
    save_figure(fig, "network_high_degree_subgraph_2.pdf")


# ============================================================
# 3. Network degree distribution
# ============================================================

positive_degrees = degrees[degrees > 0]

if not positive_degrees.empty:
    degree_counts = positive_degrees.value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(degree_counts.index, degree_counts.values, s=18)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Degree (number of software neighbors)")
    ax.set_ylabel("Number of software packages")
    ax.set_title("Software network degree distribution")

    save_figure(fig, "degree_distribution.pdf")


# ============================================================
# 4. Top 20 software by degree
# ============================================================

if not degrees.empty:
    top_degree = degrees.sort_values(ascending=False).head(20)

    labels = [
        str(name_map.get(sid) or sid)[:45]
        for sid in top_degree.index
    ]

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(labels[::-1], top_degree.values[::-1])

    ax.set_xlabel("Degree")
    ax.set_title("Top 20 software packages by network degree")

    save_figure(fig, "top_software_by_degree.pdf")


# ============================================================
# 5. Top 20 software by publication count
# ============================================================

if {
    "software_id", "publication_count"
}.issubset(software_summary.columns):
    summary = software_summary.copy()

    summary["publication_count"] = pd.to_numeric(
        summary["publication_count"], errors="coerce"
    )

    top_publications = (
        summary.dropna(subset=["publication_count"])
        .sort_values("publication_count", ascending=False)
        .head(20)
    )

    if not top_publications.empty:
        labels = [
            str(name_map.get(sid) or sid)[:45]
            for sid in top_publications["software_id"]
        ]

        fig, ax = plt.subplots(figsize=(10, 7))
        ax.barh(
            labels[::-1],
            top_publications["publication_count"].to_numpy()[::-1],
        )

        ax.set_xlabel("Number of distinct linked publications")
        ax.set_title("Top 20 software packages by publication count")

        save_figure(fig, "top_software_by_publications.pdf")


# ============================================================
# 6. Research areas represented by software
# ============================================================

if {
    "software_id", "msc_category"
}.issubset(software_msc.columns):
    msc = software_msc.dropna(
        subset=["software_id", "msc_category"]
    ).copy()

    msc["msc_category"] = msc["msc_category"].astype(str).str.strip()
    msc = msc[msc["msc_category"] != ""]
    msc = msc.drop_duplicates(["software_id", "msc_category"])

    msc_counts = (
        msc.groupby("msc_category")["software_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(20)
    )

    if not msc_counts.empty:
        fig, ax = plt.subplots(figsize=(9, 6))
        ax.barh(
            msc_counts.index.astype(str)[::-1],
            msc_counts.values[::-1],
        )

        ax.set_xlabel("Number of software packages")
        ax.set_ylabel("Top-level MSC category")
        ax.set_title("Research areas represented by software")

        save_figure(fig, "top_msc_categories.pdf")


# ============================================================
# 7. Publication count vs. network degree
# ============================================================

if {
    "software_id", "publication_count"
}.issubset(software_summary.columns):
    metrics = software_summary[
        ["software_id", "publication_count"]
    ].copy()

    metrics["publication_count"] = pd.to_numeric(
        metrics["publication_count"], errors="coerce"
    )
    metrics["degree"] = metrics["software_id"].map(degrees)

    metrics = metrics.dropna(
        subset=["publication_count", "degree"]
    )

    if not metrics.empty:
        fig, ax = plt.subplots(figsize=(7, 6))
        ax.scatter(
            metrics["publication_count"],
            metrics["degree"],
            alpha=0.45,
            s=14,
        )

        ax.set_xlabel("Number of linked publications")
        ax.set_ylabel("Network degree")
        ax.set_title("Software publication count vs. network degree")

        save_figure(fig, "publications_vs_degree.pdf")


# ============================================================
# 8. Software metadata completeness
# ============================================================

metadata_fields = [
    "description",
    "homepage",
    "keywords",
    "dependencies",
    "programming_languages",
    "operating_systems",
    "license_terms",
    "source_code",
    "orms_id",
    "zbmath_url",
]

available_fields = [
    field for field in metadata_fields
    if field in software.columns
]

if not software.empty and available_fields:
    coverage = {
        field: nonempty(software[field]).mean() * 100
        for field in available_fields
    }

    coverage_series = pd.Series(coverage).sort_values()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(coverage_series.index, coverage_series.values)

    ax.set_xlim(0, 100)
    ax.set_xlabel("Records with non-missing values (%)")
    ax.set_title("Software metadata completeness")

    save_figure(fig, "software_metadata_coverage.pdf")


# ============================================================
# 9. Save visualization summary
# ============================================================

summary_lines = [
    f"Software records: {len(software):,}",
    f"Input edge rows: {len(edges):,}",
    f"Graph nodes: {G.number_of_nodes():,}",
    f"Graph edges after simple-graph construction: {G.number_of_edges():,}",
    f"Connected components: {nx.number_connected_components(G):,}",
    f"Community assignments: {len(community_assignments):,}",
    f"Software-publication links: {len(pub_software):,}",
    f"Software-MSC links: {len(software_msc):,}",
    f"Software summary rows: {len(software_summary):,}",
    f"Paper lookup rows: {len(paper_lookup):,}",
]

(FIG_DIR / "visualization_summary.txt").write_text(
    "\n".join(summary_lines) + "\n",
    encoding="utf-8",
)

print("\nVisualization complete.")
print(f"Figures and summary saved in: {FIG_DIR.resolve()}")
