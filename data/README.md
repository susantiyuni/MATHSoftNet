## MATHSoftNet Dataset Contents

### 1. Software Metadata

The software metadata tables contain records describing mathematical research software, including package-level information such as names, authors, descriptions, homepages, keywords, dependencies, programming languages, supported operating systems, licenses, source-code links, mathematical subject classifications, and publication references, where available.

Files:

- `software.csv` — software metadata records.
- `software_summary.csv` — summary information about the software records.

### 2. Software Relationship Graph

The software relationship graph represents associations between software packages based on expert-curated *related software* relationships. The graph can be used to investigate the structure and connectivity of the mathematical software ecosystem.

File:

- `software_edges.csv` — edges representing relationships between software nodes.

### 3. Software Community Assignments

This component provides community assignments for software nodes in the software relationship graph. The communities were identified using the Louvain community detection algorithm.

Files:

- `software_communities.csv` — software-to-community assignments.
- `software_community_summary.csv` — summary information about the detected communities.

### 4. Software–Publication Associations

These records connect software packages to publication records associated with them in the underlying data source. A separate lookup table provides publication-level information for resolving publication references.

Files:

- `software_publications.csv` — software–publication associations.
- `paper_lookup.csv` — publication lookup records.

### 5. Software–Mathematical Subject Classification (MSC) Associations

This component links software packages to Mathematical Subject Classification (MSC) codes, providing a way to explore mathematical software by research area.

File:

- `software_msc.csv` — software–MSC associations.

## Dataset Statistics

The following statistics describe MATHSoftNet as of October 2026.

| Component | Statistic | Count |
|---|---|---:|
| Software metadata | Software records | 45,210 |
| Software relationship graph | Software nodes | 32,978 |
| Software relationship graph | Edges | 313,364 |
| Software relationship graph | Connected components | 12,402 |
| Software communities | Community partitions | 197 |
| Software communities | Software–community links | 32,978 |
| Software communities | Connected components in the underlying graph | 12,402 |
| Software–publication associations | Links | 324,467 |
| Software–MSC associations | Links | 138,973 |
| Software–MSC associations | Unique links | 35,456 |

**Note:** The software metadata contains 45,210 records, whereas the software relationship graph and community assignments cover only 32,978 software nodes. These nodes correspond to the subset of software items participating in at least one *related software* relationship. The remaining records are retained in the dataset to preserve the coverage of the broader software catalogue.

## File Formats

The dataset is distributed as CSV files. CSV is a widely supported, machine-readable format that can be processed using common data analysis tools and programming languages, including Python, R, and spreadsheet applications.

# License

## MATHSoftNet Dataset License

All generated content in the MATHSoftNet dataset is distributed under the **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)** license, in accordance with the licensing terms of the underlying data source (swMATH/zbMATH) specified [here](https://oai.zbmath.org/).

The CC BY-SA 4.0 license applies to the dataset as a whole. The dataset also contains bibliographic metadata and reference data derived from [I4OC (Initiative for Open Citations)](https://i4oc.org/), which are made available under the **CC0 1.0 Universal Public Domain Dedication**. The inclusion of these data does not change their underlying licensing status.

Certain third-party information, including publication abstracts, may be subject to licensing restrictions that prevent its redistribution under the dataset's license. Where such content could not be made available under a compatible license through the source API, it was omitted and replaced with the following placeholder string:

`zbMATH Open Web Interface contents unavailable due to conflicting licenses.`

This placeholder indicates that the corresponding content is unavailable due to conflicting licensing terms; it is not a substitute for the original content.

## Full License Text

The full text of the Creative Commons Attribution-ShareAlike 4.0 International license is available at:

https://creativecommons.org/licenses/by-sa/4.0/legalcode

The CC0 1.0 Universal Public Domain Dedication is available at:

https://creativecommons.org/publicdomain/zero/1.0/legalcode
