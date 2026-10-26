from pathlib import Path
import json
import warnings

import pandas as pd
import numpy as np
import networkx as nx

# ============================================================
# Configuration
# ============================================================

DATA_DIR = Path("data/processed")
OUT_DIR = DATA_DIR / "validation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "software": "software.csv",
    "edges": "software_edges.csv",
    "communities": "software_communities.csv",
    "community_summary": "software_community_summary.csv",
    "software_publications": "software_publications.csv",
    "software_msc": "software_msc.csv",
    "software_summary": "software_summary.csv",
    "paper_lookup": "paper_lookup.csv",
}

MISSING_MARKERS = {
    "", "nan", "none", "null", "n/a", "na", "-"
}

report = []


def add_check(category, check, status, observed, details=""):
    report.append({
        "category": category,
        "check": check,
        "status": status,
        "observed": observed,
        "details": details,
    })


def load_csv(key):
    path = DATA_DIR / FILES[key]
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    df = pd.read_csv(path, low_memory=False)
    print(f"Loaded {FILES[key]}: {len(df):,} rows")
    return df


def find_col(df, candidates, required=True):
    """Case-insensitive column detection."""
    lookup = {str(c).strip().lower(): c for c in df.columns}

    for name in candidates:
        if name.lower() in lookup:
            return lookup[name.lower()]

    if required:
        raise ValueError(
            f"Cannot find any of {candidates}. "
            f"Available columns: {list(df.columns)}"
        )
    return None


def normalize_id(series):
    """Normalize IDs to strings for cross-file comparison."""
    result = series.astype("string").str.strip()
    return result.mask(result.str.lower().isin(MISSING_MARKERS))


def is_present(series):
    """Treat empty strings and common textual null markers as missing."""
    values = series.astype("string").str.strip()
    return (
        values.notna()
        & ~values.str.lower().isin(MISSING_MARKERS)
    )


def record_set(df, col):
    return set(normalize_id(df[col]).dropna())


def check_status(condition):
    return "PASS" if condition else "REVIEW"


# ============================================================
# 1. Load all files
# ============================================================

data = {key: load_csv(key) for key in FILES}

software = data["software"]
edges = data["edges"]
communities = data["communities"]
community_summary = data["community_summary"]
pubs = data["software_publications"]
msc = data["software_msc"]
software_summary = data["software_summary"]
papers = data["paper_lookup"]

# Identify key columns. Edit candidates if your schema differs.
sid = find_col(software, ["id", "software_id", "sw_id"])

edge_u = find_col(
    edges, ["source", "src", "source_id", "software_id_1", "from"]
)
edge_v = find_col(
    edges, ["target", "dst", "target_id", "software_id_2", "to"]
)

community_sid = find_col(
    communities, ["software_id", "id", "node_id"]
)
community_col = find_col(
    communities, ["community_id", "community", "partition"]
)

pub_sid = find_col(
    pubs, ["software_id", "id", "sw_id"]
)
pub_pid = find_col(
    pubs, ["paper_id", "publication_id", "document_id", "zbmath_id"]
)

msc_sid = find_col(
    msc, ["software_id", "id", "sw_id"]
)
msc_code = find_col(
    msc, ["msc", "msc_code", "classification", "category", "code"]
)

paper_id = find_col(
    papers, ["paper_id", "publication_id", "document_id", "zbmath_id", "id"]
)

summary_sid = find_col(
    software_summary, ["software_id", "id", "sw_id"], required=False
)

# Normalize identifier columns.
for df, col in [
    (software, sid),
    (edges, edge_u),
    (edges, edge_v),
    (communities, community_sid),
    (pubs, pub_sid),
    (pubs, pub_pid),
    (msc, msc_sid),
    (papers, paper_id),
]:
    df[col] = normalize_id(df[col])

if summary_sid:
    software_summary[summary_sid] = normalize_id(
        software_summary[summary_sid]
    )

# ============================================================
# 2. Structural integrity
# ============================================================

software_ids = record_set(software, sid)
edge_nodes = (
    record_set(edges, edge_u)
    | record_set(edges, edge_v)
)
community_ids = record_set(communities, community_sid)
publication_software_ids = record_set(pubs, pub_sid)
msc_software_ids = record_set(msc, msc_sid)
paper_ids = record_set(papers, paper_id)
publication_paper_ids = record_set(pubs, pub_pid)

add_check(
    "Structure", "Software IDs unique",
    check_status(software[sid].nunique() == len(software)),
    software[sid].nunique(),
    f"{len(software) - software[sid].nunique():,} duplicate or missing-ID rows"
)

for key, df in data.items():
    n_duplicates = int(df.duplicated().sum())
    add_check(
        "Structure", f"Exact duplicate rows: {FILES[key]}",
        "PASS" if n_duplicates == 0 else "REVIEW",
        n_duplicates,
        "Exact duplicate rows"
    )

for key, df in data.items():
    missing_cols = [
        str(c) for c in df.columns
        if df[c].isna().all()
    ]
    add_check(
        "Structure", f"Entirely empty columns: {FILES[key]}",
        "PASS" if not missing_cols else "REVIEW",
        len(missing_cols),
        ", ".join(missing_cols) if missing_cols else "None"
    )

# ============================================================
# 3. Metadata completeness table
# ============================================================

# This reports every metadata column, not just selected fields.
completeness_rows = []

for col in software.columns:
    present = is_present(software[col])
    n_present = int(present.sum())
    n_missing = int(len(software) - n_present)

    completeness_rows.append({
        "field": str(col),
        "records_with_value": n_present,
        "records_missing_value": n_missing,
        "total_records": len(software),
        "completeness_percent": (
            round(100 * n_present / len(software), 2)
            if len(software) else np.nan
        ),
    })

completeness = pd.DataFrame(completeness_rows)
completeness = completeness.sort_values(
    "completeness_percent", ascending=True
)

completeness.to_csv(
    OUT_DIR / "metadata_completeness.csv", index=False
)

# Create a LaTeX table ready for inclusion in the paper.
latex_table = completeness.to_latex(
    index=False,
    escape=True,
    caption=(
        "Field-level completeness of the mathematical software "
        "metadata catalogue."
    ),
    label="tab:metadata-completeness",
    column_format="lrrrr",
    formatters={
        "completeness_percent": lambda x: f"{x:.2f}"
    },
    na_rep="--",
)

with open(
    OUT_DIR / "metadata_completeness.tex",
    "w",
    encoding="utf-8"
) as f:
    f.write(latex_table)

print("\nMetadata completeness:")
print(completeness.to_string(index=False))
print("\nSaved metadata completeness CSV and LaTeX table.")

# ============================================================
# 4. Graph integrity
# ============================================================

valid_edges = edges.dropna(subset=[edge_u, edge_v]).copy()
valid_edges = valid_edges[
    valid_edges[edge_u] != valid_edges[edge_v]
]

# Canonical undirected pairs.
pairs = pd.DataFrame({
    "u": valid_edges[[edge_u, edge_v]].min(axis=1),
    "v": valid_edges[[edge_u, edge_v]].max(axis=1),
})

n_self_loops = int(
    (edges[edge_u] == edges[edge_v]).fillna(False).sum()
)
n_duplicate_undirected_edges = int(
    pairs.duplicated(["u", "v"]).sum()
)

edge_endpoint_ids = (
    record_set(valid_edges, edge_u)
    | record_set(valid_edges, edge_v)
)
unknown_edge_nodes = edge_endpoint_ids - software_ids
outside_graph = software_ids - edge_endpoint_ids

add_check(
    "Graph", "Self-loops",
    check_status(n_self_loops == 0),
    n_self_loops,
    "Edges connecting a software item to itself"
)

add_check(
    "Graph", "Duplicate undirected edges",
    check_status(n_duplicate_undirected_edges == 0),
    n_duplicate_undirected_edges,
    "Duplicate pairs after canonicalizing edge direction"
)

add_check(
    "Graph", "Edge endpoints found in software catalogue",
    check_status(len(unknown_edge_nodes) == 0),
    len(unknown_edge_nodes),
    "Unknown endpoint IDs"
)

add_check(
    "Graph", "Software records outside relationship graph",
    "INFO",
    len(outside_graph),
    "Metadata records without a retained relationship edge"
)

# Build the graph using the actual edge list.
G = nx.Graph()
G.add_edges_from(pairs[["u", "v"]].itertuples(index=False, name=None))

n_components = nx.number_connected_components(G) if G else 0
n_isolates = nx.number_of_isolates(G) if G else 0

add_check(
    "Graph", "Unique graph nodes",
    "INFO", G.number_of_nodes(),
    "Nodes appearing in at least one retained edge"
)

add_check(
    "Graph", "Unique undirected graph edges",
    "INFO", G.number_of_edges(),
    "After duplicate pairs and self-loops are removed"
)

add_check(
    "Graph", "Connected components",
    "INFO", n_components,
    "Computed on the graph represented by the edge list"
)

add_check(
    "Graph", "Isolated nodes in edge-derived graph",
    "INFO", n_isolates,
    "An edge-list-only graph cannot contain nodes with degree zero"
)

# ============================================================
# 5. Community consistency
# ============================================================

community_rows = communities.dropna(
    subset=[community_sid, community_col]
).copy()

assignments_per_node = (
    community_rows.groupby(community_sid)[community_col].nunique()
)
conflicting_nodes = assignments_per_node[
    assignments_per_node > 1
]

duplicate_community_rows = int(
    community_rows.duplicated([community_sid, community_col]).sum()
)

missing_community_nodes = edge_endpoint_ids - community_ids
community_nodes_outside_graph = community_ids - edge_endpoint_ids

add_check(
    "Communities", "Graph nodes without community assignment",
    check_status(len(missing_community_nodes) == 0),
    len(missing_community_nodes),
    "Graph node IDs absent from the community file"
)

add_check(
    "Communities", "Community IDs absent from graph",
    check_status(len(community_nodes_outside_graph) == 0),
    len(community_nodes_outside_graph),
    "Community file IDs not represented in the edge list"
)

add_check(
    "Communities", "Nodes assigned to multiple communities",
    check_status(len(conflicting_nodes) == 0),
    len(conflicting_nodes),
    "Standard Louvain partitioning should assign one community per node"
)

add_check(
    "Communities", "Duplicate node-community rows",
    check_status(duplicate_community_rows == 0),
    duplicate_community_rows,
    "Repeated identical assignments"
)

# Recalculate community sizes from unique assignments.
# If conflicting assignments exist, do not silently choose one.
if len(conflicting_nodes) == 0:
    unique_assignments = community_rows.drop_duplicates(
        [community_sid, community_col]
    )

    recomputed_sizes = (
        unique_assignments.groupby(community_col)[community_sid]
        .nunique()
        .rename("recomputed_nodes")
        .reset_index()
    )

    add_check(
        "Communities", "Total nodes across unique community assignments",
        check_status(
            unique_assignments[community_sid].nunique()
            == len(edge_endpoint_ids)
        ),
        unique_assignments[community_sid].nunique(),
        "Should equal the number of graph nodes"
    )

    recomputed_sizes.to_csv(
        OUT_DIR / "recomputed_community_sizes.csv", index=False
    )
else:
    warnings.warn(
        "Conflicting community assignments detected. "
        "Community size validation is incomplete until resolved."
    )

# ============================================================
# 6. Publication association integrity
# ============================================================

duplicate_pub_links = int(
    pubs.duplicated([pub_sid, pub_pid]).sum()
)

unknown_pub_software = publication_software_ids - software_ids
unknown_papers = publication_paper_ids - paper_ids

add_check(
    "Publications", "Duplicate software-publication associations",
    check_status(duplicate_pub_links == 0),
    duplicate_pub_links,
    "Duplicate software_id-paper_id pairs"
)

add_check(
    "Publications", "Publication links to unknown software IDs",
    check_status(len(unknown_pub_software) == 0),
    len(unknown_pub_software),
    "Software IDs in software_publications.csv absent from software.csv"
)

add_check(
    "Publications", "Publication links to unknown paper IDs",
    check_status(len(unknown_papers) == 0),
    len(unknown_papers),
    "Paper IDs in software_publications.csv absent from paper_lookup.csv"
)

# Paper lookup checks.
add_check(
    "Publications", "Paper lookup IDs unique",
    check_status(papers[paper_id].nunique() == len(papers)),
    papers[paper_id].nunique(),
    "Expected one lookup record per paper ID"
)

# ============================================================
# 7. MSC integrity
# ============================================================

duplicate_msc_links = int(
    msc.duplicated([msc_sid, msc_code]).sum()
)

unknown_msc_software = msc_software_ids - software_ids

add_check(
    "MSC", "Duplicate software-MSC associations",
    check_status(duplicate_msc_links == 0),
    duplicate_msc_links,
    "Duplicate software_id-MSC pairs"
)

add_check(
    "MSC", "MSC links to unknown software IDs",
    check_status(len(unknown_msc_software) == 0),
    len(unknown_msc_software),
    "Software IDs in software_msc.csv absent from software.csv"
)

add_check(
    "MSC", "Missing MSC codes",
    check_status(not msc[msc_code].isna().any()),
    int(msc[msc_code].isna().sum()),
    "MSC mapping rows without a classification value"
)

# ============================================================
# 8. Summary-file consistency
# ============================================================

if summary_sid:
    summary_ids = record_set(software_summary, summary_sid)
    missing_summary_ids = software_ids - summary_ids
    unknown_summary_ids = summary_ids - software_ids

    add_check(
        "Summaries", "Software IDs missing from software_summary.csv",
        "INFO", len(missing_summary_ids),
        "Compare with intended inclusion rules for this summary"
    )

    add_check(
        "Summaries", "Unknown IDs in software_summary.csv",
        check_status(len(unknown_summary_ids) == 0),
        len(unknown_summary_ids),
        "Summary IDs absent from software.csv"
    )

# ============================================================
# 9. Save validation report
# ============================================================

validation = pd.DataFrame(report)
validation.to_csv(OUT_DIR / "validation_report.csv", index=False)

print("\n=== VALIDATION REPORT ===")
print(validation.to_string(index=False))

print("\nStatus counts:")
print(validation["status"].value_counts(dropna=False).to_string())

# Save a machine-readable summary.
summary = {
    "software_rows": len(software),
    "unique_software_ids": len(software_ids),
    "graph_nodes": G.number_of_nodes(),
    "graph_edges": G.number_of_edges(),
    "software_records_outside_graph": len(outside_graph),
    "connected_components": n_components,
    "community_rows": len(communities),
    "unique_community_software_ids": len(community_ids),
    "nodes_with_multiple_community_assignments": len(conflicting_nodes),
    "software_publication_rows": len(pubs),
    "software_msc_rows": len(msc),
    "paper_lookup_rows": len(papers),
}

with open(OUT_DIR / "validation_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\nSaved outputs to:", OUT_DIR.resolve())
