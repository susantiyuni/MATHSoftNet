## MATHSoftNet Use Case

#### RQ: _To what extent do expert-annotated software relationships align with associations observed in the research literature?_

To demonstrate the dataset utility, we conducted a preliminary use-case study combining two dataset views: the software relationship graph and software–publication associations. The analysis examines whether expert-annotated software relationships correspond to bibliographic co-occurrence.

For each edge in the software relationship graph, we checked whether the two connected software nodes shared at least one associated publication. We compared the results with a total of 1,566,820 randomly sampled software pairs not connected by an edge in the graph.

To reproduce this, run the following script:

```bash
python alignment.py
```

This will calculate the. 

### Result summary

Of the 313,364 edges connecting 32,978 software nodes in MATHSoftNet, 166,242 (53.05%) linked software pairs sharing at least one associated publication. In contrast, fewer than 0.1% of the randomly sampled non-edge pairs shared a publication, yielding a difference of 53.02 percentage points.

Figure alignment illustrates the distribution of shared-publication counts for connected and unconnected software pairs, highlighting the difference in bibliographic overlap.

This preliminary analysis demonstrates the value of combining software relationship graphs with publication associations to investigate relationships between mathematical software and the scholarly literature.
