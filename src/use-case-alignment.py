"""
Inputs:
  data/processed/software_edges.csv
  data/processed/software_publications.csv
  data/processed/software.csv              (optional; for software names)

Outputs:
  data/processed/alignment_results/
      alignment_summary.csv
      edge_alignment.csv
      sampled_non_edges.csv
      publication_cooccurrence_pairs.csv
"""

from pathlib import Path
from itertools import combinations
from collections import Counter
import json
import random

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact

# --------------------------- Configuration ---------------------------

DATA = Path("data/processed")
OUT = DATA / "alignment_results"

EDGES_FILE = DATA / "software_edges.csv"
LINKS_FILE = DATA / "software_publications.csv"
SOFTWARE_FILE = DATA / "software.csv"

RANDOM_SEED = 42
NONEDGE_SAMPLE_MULTIPLIER = 5

# Publications associated with more than this many software records are
# excluded from pair generation. Raise this limit if appropriate.
MAX_SOFTWARE_PER_PUBLICATION = 100

# Optional explicit column overrides, e.g. EDGE_SOURCE = "source_id"
EDGE_SOURCE = None
EDGE_TARGET = None
LINK_SOFTWARE_ID = None
LINK_PUBLICATION_ID = None
SOFTWARE_ID = None
SOFTWARE_NAME = None

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
OUT.mkdir(parents=True, exist_ok=True)


def find_col(df, candidates, label, override=None):
    """Find a column case-insensitively using likely aliases."""
    if override:
        if override not in df.columns:
            raise ValueError(f"{label}: configured column {override!r} not found.")
        return override

    lookup = {str(c).strip().lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]

    raise ValueError(
        f"Cannot identify {label}. Available columns: {list(df.columns)}. "
        f"Set the corresponding override near the top of the script."
    )


def clean_id(series):
    """Normalize identifiers to strings and discard missing/blank IDs."""
    s = series.astype("string").str.strip()
    return s.mask(s.str.lower().isin(["", "nan", "none", "null", "<na>"]))


# ----------------------------- Load data -----------------------------

edges_df = pd.read_csv(EDGES_FILE, low_memory=False)
links_df = pd.read_csv(LINKS_FILE, low_memory=False)

src_col = find_col(
    edges_df,
    ["source", "source_id", "source_software_id", "software_id_1",
     "software1_id", "from", "node1"],
    "edge source",
    EDGE_SOURCE,
)
dst_col = find_col(
    edges_df,
    ["target", "target_id", "target_software_id", "software_id_2",
     "software2_id", "to", "node2"],
    "edge target",
    EDGE_TARGET,
)
link_sid_col = find_col(
    links_df,
    ["software_id", "sw_id", "softwareid", "mathsoftware_id"],
    "software ID in publication links",
    LINK_SOFTWARE_ID,
)
paper_col = find_col(
    links_df,
    ["publication_id", "paper_id", "document_id", "pub_id",
     "publicationid", "id_publication"],
    "publication ID",
    LINK_PUBLICATION_ID,
)

edges = pd.DataFrame({
    "u": clean_id(edges_df[src_col]),
    "v": clean_id(edges_df[dst_col]),
}).dropna()

links = pd.DataFrame({
    "software_id": clean_id(links_df[link_sid_col]),
    "publication_id": clean_id(links_df[paper_col]),
}).dropna().drop_duplicates()

# Canonicalize undirected edges without relying on pandas min/max behavior.
edge_pairs = {
    tuple(sorted((u, v)))
    for u, v in edges[["u", "v"]].itertuples(index=False, name=None)
    if u != v
}
edge_pairs = sorted(edge_pairs)

graph_nodes = set()
for u, v in edge_pairs:
    graph_nodes.add(u)
    graph_nodes.add(v)

# Restrict bibliographic analysis to the nodes in the expert-defined software relationship graph.
links = links[links["software_id"].isin(graph_nodes)].copy()

print("Loaded data")
print(f"  Unique graph nodes: {len(graph_nodes):,}")
print(f"  Unique undirected expert-defined edges: {len(edge_pairs):,}")
print(f"  Unique software-publication links in graph: {len(links):,}")
print(f"  Publications represented in graph: {links['publication_id'].nunique():,}")

# ----------------- Compute publication co-occurrence -----------------

# Each pair is counted at most once per publication because links were
# deduplicated before grouping.
software_by_paper = (
    links.groupby("publication_id")["software_id"]
    .agg(lambda s: sorted(set(s)))
)

cooccurrence_count = Counter()
skipped_large_papers = 0
papers_with_pairs = 0

for paper_id, software_ids in software_by_paper.items():
    if len(software_ids) < 2:
        continue

    if len(software_ids) > MAX_SOFTWARE_PER_PUBLICATION:
        skipped_large_papers += 1
        continue

    papers_with_pairs += 1
    for u, v in combinations(software_ids, 2):
        cooccurrence_count[(u, v)] += 1

cooccurrence_df = pd.DataFrame(
    [
        (u, v, count)
        for (u, v), count in cooccurrence_count.items()
    ],
    columns=["software_u", "software_v", "shared_publications"],
)

cooccurrence_df.to_csv(
    OUT / "publication_cooccurrence_pairs.csv", index=False
)

cooccurrence_lookup = dict(cooccurrence_count)
publication_count = links.groupby("software_id")["publication_id"].nunique().to_dict()

# ------------------- Score expert-defined software relationship graph edges --------------------

edge_records = []
for u, v in edge_pairs:
    shared = cooccurrence_lookup.get((u, v), 0)
    edge_records.append({
        "software_u": u,
        "software_v": v,
        "shared_publications": shared,
        "u_publication_count": publication_count.get(u, 0),
        "v_publication_count": publication_count.get(v, 0),
        "has_shared_publication": shared > 0,
    })

edge_alignment = pd.DataFrame(edge_records)
edge_alignment.to_csv(OUT / "edge_alignment.csv", index=False)

# ---------------- Random non-edges as a comparison baseline ----------

# Draw random pairs from graph nodes, rejecting existing edges.
# Sampling is capped to avoid endless rejection in dense graphs.
edge_set = set(edge_pairs)
nodes = sorted(graph_nodes)
target_n = min(
    len(edge_pairs) * NONEDGE_SAMPLE_MULTIPLIER,
    max(0, len(nodes) * (len(nodes) - 1) // 2 - len(edge_set)),
)

nonedge_records = []
seen = set()
attempts = 0
max_attempts = max(100_000, target_n * 30)

while len(nonedge_records) < target_n and attempts < max_attempts:
    attempts += 1
    u, v = random.sample(nodes, 2)
    pair = tuple(sorted((u, v)))

    if pair in edge_set or pair in seen:
        continue

    seen.add(pair)
    shared = cooccurrence_lookup.get(pair, 0)

    nonedge_records.append({
        "software_u": pair[0],
        "software_v": pair[1],
        "shared_publications": shared,
        "u_publication_count": publication_count.get(pair[0], 0),
        "v_publication_count": publication_count.get(pair[1], 0),
        "has_shared_publication": shared > 0,
    })

nonedges = pd.DataFrame(nonedge_records)
nonedges.to_csv(OUT / "sampled_non_edges.csv", index=False)

# --------------------------- Statistics -----------------------------

n_edges = len(edge_alignment)
n_non_edges = len(nonedges)

edge_overlap_n = int(edge_alignment["has_shared_publication"].sum())
nonedge_overlap_n = int(nonedges["has_shared_publication"].sum())

edge_overlap_rate = edge_overlap_n / n_edges if n_edges else np.nan
nonedge_overlap_rate = (
    nonedge_overlap_n / n_non_edges if n_non_edges else np.nan
)

# Fisher's exact test compares overlap rates for observed edges and sampled
# non-edges. It does not adjust for node popularity or sampling dependence.
if n_edges and n_non_edges:
    contingency = [
        [edge_overlap_n, n_edges - edge_overlap_n],
        [nonedge_overlap_n, n_non_edges - nonedge_overlap_n],
    ]
    odds_ratio, fisher_p = fisher_exact(contingency)
else:
    odds_ratio, fisher_p = np.nan, np.nan

# Compare shared-publication counts across pairs, including zero-overlap pairs.
mean_edge_shared = (
    edge_alignment["shared_publications"].mean() if n_edges else np.nan
)
mean_nonedge_shared = (
    nonedges["shared_publications"].mean() if n_non_edges else np.nan
)

# Spearman-like rank correlation is not required for the core test.
# Report the median and upper tail to characterize the overlap distribution.
median_edge_shared = (
    edge_alignment["shared_publications"].median() if n_edges else np.nan
)
p90_edge_shared = (
    edge_alignment["shared_publications"].quantile(0.90) if n_edges else np.nan
)

summary = [
    ("graph_nodes", len(graph_nodes), "Unique software IDs appearing in an edge"),
    ("expert_edges", n_edges, "Unique undirected, non-self-loop edges"),
    ("software_publication_links", len(links), "Unique links restricted to graph nodes"),
    ("publications_in_graph", links["publication_id"].nunique(), "Unique linked publications"),
    ("publication_cooccurrence_pairs", len(cooccurrence_df), "Pairs sharing at least one publication, within configured paper-size limit"),
    ("papers_with_two_or_more_software", int((software_by_paper.map(len) >= 2).sum()), "Papers linked to at least two graph software records"),
    ("papers_used_for_pair_generation", papers_with_pairs, "Papers used to generate co-occurrence pairs"),
    ("papers_skipped_large", skipped_large_papers, f"Papers exceeding {MAX_SOFTWARE_PER_PUBLICATION} linked software records"),
    ("expert_edges_with_shared_publication", edge_overlap_n, "Edges whose endpoints share at least one linked publication"),
    ("expert_edge_overlap_rate", edge_overlap_rate, "Descriptive fraction of expert edges with publication overlap"),
    ("sampled_non_edges", n_non_edges, "Randomly sampled pairs absent from the expert graph"),
    ("sampled_non_edges_with_shared_publication", nonedge_overlap_n, "Sampled non-edges with publication overlap"),
    ("sampled_nonedge_overlap_rate", nonedge_overlap_rate, "Descriptive overlap fraction among sampled non-edges"),
    ("overlap_rate_difference", edge_overlap_rate - nonedge_overlap_rate if n_edges and n_non_edges else np.nan, "Edge overlap rate minus sampled non-edge overlap rate"),
    ("fisher_odds_ratio", odds_ratio, "Unadjusted odds ratio for overlap in edges versus sampled non-edges"),
    ("fisher_exact_p_value", fisher_p, "Unadjusted Fisher exact test; not popularity-adjusted"),
    ("mean_shared_publications_edges", mean_edge_shared, "Mean shared-publication count per expert edge"),
    ("mean_shared_publications_sampled_non_edges", mean_nonedge_shared, "Mean shared-publication count per sampled non-edge"),
    ("median_shared_publications_edges", median_edge_shared, "Median shared-publication count per expert edge"),
    ("p90_shared_publications_edges", p90_edge_shared, "90th percentile shared-publication count for expert edges"),
]

summary_df = pd.DataFrame(summary, columns=["statistic", "value", "interpretation"])
summary_df.to_csv(OUT / "alignment_summary.csv", index=False)

# Optional names for readable examples.
if SOFTWARE_FILE.exists():
    software_df = pd.read_csv(SOFTWARE_FILE, low_memory=False)
    try:
        sid_col = find_col(
            software_df,
            ["software_id", "id", "sw_id", "softwareid"],
            "software ID",
            SOFTWARE_ID,
        )
        name_col = find_col(
            software_df,
            ["name", "software_name", "title", "software_title"],
            "software name",
            SOFTWARE_NAME,
        )
        software_df["__sid"] = clean_id(software_df[sid_col])
        software_df["__name"] = software_df[name_col].astype("string")
        name_map = (
            software_df.dropna(subset=["__sid"])
            .drop_duplicates("__sid")
            .set_index("__sid")["__name"]
            .to_dict()
        )

        edge_alignment["software_u_name"] = edge_alignment["software_u"].map(name_map)
        edge_alignment["software_v_name"] = edge_alignment["software_v"].map(name_map)
        edge_alignment.to_csv(OUT / "edge_alignment.csv", index=False)
    except ValueError as e:
        print(f"Name lookup skipped: {e}")

# Print an empirical mini-report from this run.
print("\nALIGNMENT RESULTS")
print("-----------------")
print(f"Expert edges with shared publication: {edge_overlap_n:,}/{n_edges:,} "
      f"({edge_overlap_rate:.2%})" if n_edges else "No edges found.")
print(f"Sampled non-edges with shared publication: {nonedge_overlap_n:,}/{n_non_edges:,} "
      f"({nonedge_overlap_rate:.2%})" if n_non_edges else "No non-edges sampled.")
print(f"Difference in overlap rates: {edge_overlap_rate - nonedge_overlap_rate:.2%}"
      if n_edges and n_non_edges else "Difference unavailable.")
print(f"Fisher odds ratio: {odds_ratio:.3f}; p-value: {fisher_p:.3g}"
      if n_edges and n_non_edges else "Fisher test unavailable.")
print(f"Mean shared publications per edge: {mean_edge_shared:.3f}")
print(f"Mean shared publications per sampled non-edge: {mean_nonedge_shared:.3f}")
print(f"Papers skipped due to size limit: {skipped_large_papers:,}")
print(f"\nFiles written to: {OUT.resolve()}")
