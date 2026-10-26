# MATHSoftNet: A Multi-View Dataset of Mathematical Research Software Relationships (2026)

_MATHSoftNet_ is a multi-view dataset of mathematical software integrating expert-curated and automatically generated networks of software relationships, situated within the broader landscape of mathematical research.

**IMPORTANT**: MATHSoftNet is archived on Zenodo for long-term preservation and accessibility; we provide a sample of approximately 200 records of the data on GitHub.

---
## Contents

- [Dataset Sizes and Statistics](#dataset-sizes-and-statistics)
- [Key Features and Data Samples](#key-features-and-data-samples)
- [Data Construction, Validation, Usage](#data-construction-validation-usage)
  - [Prerequisites](#prerequisites)
  - [Data Harvesting and Construction](#data-harvesting-and-construction)
  - [Data Preprocessing and Validation](#data-preprocessing-and-validation)
  - [Data Usage](#data-usage)
- [License](#license)
- [Citation](#citation)
- [Contact and Maintenance](#contact-and-maintenance)

## Dataset Sizes and Statistics

The following statistics are reported as of October 2026:

- **Software records**: 45,210
- **Software relationship graph**
  - Software nodes: 32,978
  - Edges: 313,364
  - Connected components: 12,402
- **Software community**
  - Community partitions: 197
  - Software--community links: 32,978
  - Connected components: 12,402
- **Software--publication links**: 324,467
- **Software--MSC links**: 138,973
- **Software--MSC links (unique)**: 35,456
  
## Key Features and Data Samples

- **Curated Mathematical Software Metadata Records**  
  Expert-curated software records, containing package-level metadata, including _names, authors, descriptions, homepages, keywords, dependencies, programming languages, supported operating systems, licenses, source-code links, mathematical subject classifications, publication references_, etc. A sample of 200 records is available here: [`data/software-records-sample.csv`](./data/software-records-sample.csv). 

- **Software Relationship Graph**  
  An undirected software relationship graph from the _related software_ associations curated by human-expert. We provide a sample of 200 records of the graph edges here: [`data/software-edges-sample.csv`](./data/software-edges-sample.csv). 

- **Software Community Assignments**  
  Software community assignments for each software node in the software relationship graphs, derived using Louvain community detection algorithm. A sample of 200 records is available here: [`data/software-community-sample.csv`](./data/software-community-sample.csv). 

- **Software–Publication Associations**  
  We link each software to the publication records associated with the software in the data source. A sample of 200 records is available here: [`data/software-publication-sample.csv`](./data/software-publication-sample.csv). The publication lookup examples are provided here: [`data/publication-records-sample.csv`](./data/publication-records-sample.csv)
  
- **Software–_Mathematical Subject Classification_ (MSC) Association**  
  We link each software to the subject classification (MSC) codes; a sample of 200 records is available here: [`data/software-msc-sample.csv`](./data/software-msc-sample.csv). 
  
## Data Construction and Validation

### Prerequisites

- Python 3.12+  
- Python libraries: `networkx`, `numpy`, and others (see [`requirements.txt`](requirements.txt))

Install the dependencies:

```bash
pip install -r requirements.txt
```

### Data Harvesting and Construction

For details on data harvesting and construction, see [to be added].

### Data Preprocessing and Validation

Preprocess the dataset by running:

```bash
python src/preprocess.py
```

Validate the dataset by running the following script, which will check the dataset's structural consistency and metadata completeness coverage.
```bash
python src/validate.py
```

Note: To reproduce validation on sample data, update the input and output file paths in [`src/validate.py`](./src/validate.py) before execution.

## Data Usage

The dataset supports a broad range of research directions for systematics investigation of software and its connections to mathematical research ecosystem. To demonstrate its potential usage, we conducted a preliminary use-case study examining the extent to which expert-annotated software relationships align with relationships reflected in the scientific literature. Details are available in the [`use-case directory`](./use-case/).

## Citation

```to be added```

## License

All generated content is distributed under the [CC-BY-SA 4.0.](https://creativecommons.org/licenses/by-sa/4.0/) license, in accordance with the licensing terms of the underlying data source, specified [here](https://oai.zbmath.org/).

## Contact and Maintenance:

MATHSoftNet is maintained by FIZ Karlsruhe, and planned to be updated annually, subject to the availability of the underlying data stream, resource and infrastructure constraint.

📧 yuni.susanti@fiz-karlsruhe.de
