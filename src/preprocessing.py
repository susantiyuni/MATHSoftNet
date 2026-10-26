from __future__ import annotations

import json
import re
import warnings
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path

# ----------------------------- CONFIGURATION -----------------------------

# ROOT = Path(__file__).resolve().parents[1]
ROOT = Path.cwd()
DATA = ROOT / "data"
RAW = DATA
OUT = DATA / "processed"
FIG = DATA / "visualizations"

EDGE_FILE = RAW / "edges.csv"
COMMUNITY_FILE = RAW / "communities.csv"
SOFTWARE_DIR = RAW / "software"
PUBLICATION_DIR = RAW / "publications"

EDGE_SOURCE_COL = "node_a"       # e.g. "node_a"
EDGE_TARGET_COL = "node_b"       # e.g. "node_b"
COMMUNITY_NODE_COL = "node"    # e.g. "software"
COMMUNITY_ID_COL = "partition"      # e.g. "partition"

PUBLICATION_SOFTWARE_KEYS = [
    "software_ids", "software", "software_packages", "cited_software",
    "software_citations", "tools", "software_references"
]

PUBLICATION_ID_KEYS = ["id", "zbmath_id", "document_id", "zbmath_document_id", "zbmath_url"]
SOFTWARE_ID_KEYS = ["id", "software_id", "orms_id", "zbmath_id", "zbmath_url"]
SOFTWARE_NAME_KEYS = ["name", "software_name", "title"]

# ----------------------------- FILE READING ------------------------------

def read_records(path: Path) -> list[dict[str, Any]]:
    """Read JSON array/object, JSONL, or a directory of JSON/JSONL files."""
    records: list[dict[str, Any]] = []
    if path.is_dir():
        files = sorted([*path.rglob("*.json"), *path.rglob("*.jsonl"), *path.rglob("*.ndjson")])
        for file in files:
            records.extend(read_records(file))
        return records

    if not path.exists():
        return records

    text = path.read_text(encoding="utf-8-sig").strip()
    if not text:
        return records

    try:
        obj = json.loads(text)
        if isinstance(obj, list):
            return [x for x in obj if isinstance(x, dict)]
        if isinstance(obj, dict):
            # Common wrappers used by data exports.
            for key in ("records", "data", "items", "results", "publications", "software"):
                if isinstance(obj.get(key), list):
                    return [x for x in obj[key] if isinstance(x, dict)]
            return [obj]
    except json.JSONDecodeError:
        pass

    # Fall back to JSON Lines.
    for line_no, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                records.append(obj)
            elif isinstance(obj, list):
                records.extend(x for x in obj if isinstance(x, dict))
        except json.JSONDecodeError as exc:
            warnings.warn(f"Skipping invalid JSON line {line_no} in {path}: {exc}")
    return records


def first_value(record: dict[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        value = record.get(key)
        if value is not None and value != "":
            return value
    return None


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def clean_id(value: Any) -> str | None:
    """Convert scalar or nested identifier values into a stable string."""
    if value is None:
        return None
    if isinstance(value, dict):
        value = first_value(value, ["id", "software_id", "document_id", "zbmath_id", "orms_id", "name", "url"])
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


def norm_label(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


def parse_nested_values(value: Any) -> list[str]:
    """Extract IDs/names from scalar, list, or simple nested reference objects."""
    values = []
    for item in as_list(value):
        val = clean_id(item)
        if val:
            values.append(val)
    return values


def normalize_msc(value: Any) -> list[str]:
    """Normalize MSC values while retaining their original code strings."""
    codes: list[str] = []
    for item in as_list(value):
        if isinstance(item, dict):
            item = first_value(item, ["code", "msc", "msc_code", "id", "classification"])
        if item is None:
            continue
        if isinstance(item, list):
            codes.extend(normalize_msc(item))
        else:
            s = str(item).strip()
            if s:
                codes.append(s)
    return sorted(set(codes))


def safe_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)

def load_software_records(software_dir: Path) -> list[dict[str, Any]]:
    """Load software records from partitioned JSON files."""

    records = []

    json_files = sorted(
        software_dir.glob("*.json"),
        key=lambda p: int(p.stem) if p.stem.isdigit() else float("inf")
    )

    if not json_files:
        raise FileNotFoundError(
            f"No JSON files found in {software_dir}"
        )

    for file_path in json_files:
        try:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict):
                # Your format: {"2": {...}, "3": {...}, ...}
                for key, rec in data.items():
                    if not isinstance(rec, dict):
                        warnings.warn(
                            f"Skipping invalid record {key!r} in {file_path.name}"
                        )
                        continue

                    # Use the dictionary key as the ID if the record lacks one.
                    rec.setdefault("id", key)
                    records.append(rec)

            elif isinstance(data, list):
                # Also support files containing a list of records.
                records.extend(
                    rec for rec in data if isinstance(rec, dict)
                )

            else:
                warnings.warn(
                    f"Unexpected JSON format in {file_path.name}; skipping."
                )

# ---------------------------- GRAPH / COMMUNITIES ------------------------
def read_edges(path: Path, alias_to_id: dict[str, str]) -> pd.DataFrame:
    if not path.exists():
        warnings.warn(f"Edge file not found: {path}")
        return pd.DataFrame(columns=["source", "target"])
    df = pd.read_csv(path, dtype=str)
    if df.empty:
        return pd.DataFrame(columns=["source", "target"])

    source_col = EDGE_SOURCE_COL or df.columns[0]
    target_col = EDGE_TARGET_COL or (df.columns[1] if len(df.columns) > 1 else None)
    if target_col is None or source_col not in df or target_col not in df:
        raise ValueError("Could not identify two edge columns. Set EDGE_SOURCE_COL and EDGE_TARGET_COL.")
    edges = df[[source_col, target_col]].copy()
    edges.columns = ["source", "target"]
    edges = edges.dropna()
    edges["source"] = edges["source"].astype(str).str.strip().map(lambda x: alias_to_id.get(x, x))
    edges["target"] = edges["target"].astype(str).str.strip().map(lambda x: alias_to_id.get(x, x))
    edges = edges[(edges.source != "") & (edges.target != "") & (edges.source != edges.target)]

    # Canonical ordering makes undirected edges unique.
    pairs = edges.apply(lambda r: sorted([r["source"], r["target"]]), axis=1, result_type="expand")
    pairs.columns = ["source", "target"]
    return pairs.drop_duplicates().sort_values(["source", "target"]).reset_index(drop=True)


def read_communities(path: Path, alias_to_id: dict[str, str]) -> pd.DataFrame:
    if not path.exists():
        warnings.warn(f"Community file not found: {path}")
        return pd.DataFrame(columns=["software_id", "community_id"])
    df = pd.read_csv(path, dtype=str)
    if df.empty:
        return pd.DataFrame(columns=["software_id", "community_id"])
    node_col = COMMUNITY_NODE_COL or df.columns[0]
    comm_col = COMMUNITY_ID_COL or (df.columns[1] if len(df.columns) > 1 else None)
    if comm_col is None or node_col not in df or comm_col not in df:
        raise ValueError("Could not identify community columns. Set COMMUNITY_NODE_COL and COMMUNITY_ID_COL.")
    out = df[[node_col, comm_col]].copy()
    out.columns = ["software_id", "community_id"]
    out = out.dropna()
    out["software_id"] = out["software_id"].astype(str).str.strip().map(lambda x: alias_to_id.get(x, x))
    out["community_id"] = out["community_id"].astype(str).str.strip()
    out = out.drop_duplicates()
    # A single hard partition should have one community per software node.
    counts = out.groupby("software_id")["community_id"].nunique()
    conflicts = counts[counts > 1]
    if len(conflicts):
        warnings.warn(f"{len(conflicts)} software IDs have multiple community labels; retaining all mappings.")
    return out.sort_values(["community_id", "software_id"]).reset_index(drop=True)


def make_community_summary(communities: pd.DataFrame, edges: pd.DataFrame) -> pd.DataFrame:
    if communities.empty:
        return pd.DataFrame(columns=["community_id", "software_count", "internal_edges"])
    sizes = communities.groupby("community_id")["software_id"].nunique().rename("software_count")
    edge_comm = edges.merge(
        communities.rename(columns={"software_id": "source", "community_id": "source_community"}),
        on="source", how="left"
    ).merge(
        communities.rename(columns={"software_id": "target", "community_id": "target_community"}),
        on="target", how="left"
    )
    internal = edge_comm[
        edge_comm["source_community"].notna()
        & (edge_comm["source_community"] == edge_comm["target_community"])
    ].groupby("source_community").size().rename("internal_edges")
    summary = sizes.to_frame().join(internal).fillna({"internal_edges": 0}).reset_index()
    summary["internal_edges"] = summary["internal_edges"].astype(int)
    return summary.sort_values("software_count", ascending=False).reset_index(drop=True)


def make_software_msc(software: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if software.empty:
        return pd.DataFrame(columns=["software_id", "msc_code"])
    for _, row in software.iterrows():
        try:
            codes = json.loads(row.get("classification") or "[]")
        except (TypeError, json.JSONDecodeError):
            codes = []
        for code in as_list(codes):
            rows.append({"software_id": row["software_id"], "msc_code": str(code)})
    return pd.DataFrame(rows, columns=["software_id", "msc_code"]).drop_duplicates()


        except (json.JSONDecodeError, OSError) as exc:
            warnings.warn(f"Could not load {file_path.name}: {exc}")

    print(f"Loaded {len(records):,} software records from {len(json_files)} files.")

    return records

OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

software_records = load_software_records(SOFTWARE_DIR)
software, alias_to_id = build_software_table(software_records)
# software.to_csv(
#     OUT / "software.csv",
#     index=False,
#     encoding="utf-8"
# )
print(software.shape)
display(software.head())
print(f"Loaded {len(software_records):,} software records")

edges = read_edges(EDGE_FILE, alias_to_id)
communities = read_communities(COMMUNITY_FILE, alias_to_id)
community_summary = make_community_summary(communities, edges)
software_msc = make_software_msc(software)

tables = {
    "software.csv": software,
    "software_edges.csv": edges,
    "software_communities.csv": communities,
    "software_msc.csv": software_msc,
    "community_summary.csv": community_summary,
}
for filename, df in tables.items():
    df.to_csv(OUT / filename, index=False, encoding="utf-8")
    print(f"Wrote {filename}: {len(df):,} rows")
