## MATHSoftNet Use Case Example

#### RQ: _To what extent do expert-annotated software relationships align with associations observed in the scientific literature?_

To demonstrate the dataset utility, we conducted a preliminary use-case study combining two dataset views: the software relationship graph and software–publication associations. The analysis examines whether expert-annotated software relationships correspond to bibliographic co-occurrence.

Thus, the analysis compares two independent signals:
- Software relationship graph: whether a pair of software is connected by a related software edge.
- Software-publication association as the "bibliographic evidence": whether the two software are both associated with at least one common publication.

For each edge in the software relationship graph, we checked whether the two connected software nodes shared at least one associated publication. We compared the results with a total of 1,566,820 randomly sampled software pairs not connected by an edge in the graph.

To reproduce this, run the following script:

```bash
python alignment.py
```

This will calculate the alignment statistics and compares expert-defined edges with a random sample of non-edges. The script also exports pair-level results for further investigation, see [`publication_cooccurrence_pairs.csv`](publication_cooccurrence_pairs.csv) and [`edge_alignment.csv`](edge_alignment.csv). 

Note: To reproduce the use case on sample data, update the input and output file paths in [`alignment.py`](alignment.py) before execution.

**Result Summary:** Of the 313,364 edges connecting 32,978 software nodes in MATHSoftNet, 166,242 (53.05%) linked software pairs sharing at least one associated publication. In contrast, fewer than 0.1% of the randomly sampled non-edge pairs shared a publication, yielding a difference of 53.02 percentage points.
