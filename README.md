# MATHSoftNet: A Multi-View Dataset of Mathematical Research Software Relationships (2026)

## Overview

_MATHSoftNet_ is a multi-view dataset designed to support systematic investigations of the software ecosystem and its connections to the broader landscape of mathematical research. MATHSoftNet integrates expert-curated and automatically generated networks of software relationships with software-specific metadata and bibliographic information. Additionally, it includes software communities derived from graph topology, supporting the exploration of the mathematic software ecosystem's structure and organization.

**IMPORTANT**: MATHSoftNet is archived on Zenodo for long-term preservation and accessibility; we provide a sample of approximately 200 records of the data on GitHub.

---
## Contents

- [Dataset Sizes and Statistics](#dataset-sizes-and-statistics)
- [Key Features and Data Samples](#key-features-and-data-sample)
- [Construction and Setup](#construction-and-setup)
  - [Prerequisites](#prerequisites)
  - [Data Harvesting](#data-harvesting)
  - [RDF Construction](#rdf-construction)
  - [RDF Triple Store Setup](#rdf-triple-store-setup)
- [Repository Structure](#repository-structure)
- [License](#license)
- [Citation](#citation)
- [Contact and Maintenance](#contact-and-maintenance)

## Key Statistics

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
- Python libraries: `rdflib`, `SPARQLWrapper`, and others (see requirements.txt)  
  - We use [Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/) as an example for its simplicity  
  - *Note:* Production SPARQL endpoints use Virtuoso (See the [`zb-virtuoso`](./zb-virtuoso) directory for the complete Virtuoso setup.)

### Data Harvesting and Construction

To harvest data by zbMATH ID (e.g., ID list of zbMATH open access subset: [zbMATH OA subset](https://zenodo.org/records/8021789)), run:

```bash
python src/harvest-by-id.py 
```

For bulk download (via _sickle_), refers to: [zbMATHOpen Harvester](https://github.com/zbMATHOpen/mscHarvester)

### Data Preprocessing and Validation

Using raw `.jsonl` zbMATH data obtained from the API (see example: [`data/subset-200.jsonl`](./data/subset-200.jsonl)), run the following commands to automatically generate the RDF KG:

```bash
# Option 1: Run the Python script
python src/create-rdf-v2.py --inp data/subset-200.jsonl --out data/subset-200.ttl --nt 0

# Option 2: Run the shell script for batch processing
run-convert.sh

```

## Repository Structure

- [`data/`](./data) – `.jsonl` raw data and `.ttl` RDF KG (subset), ontology files (`.ttl`), etc.
- [`src/`](./src) – Source code for KG construction (data harvest, statistics calculation, RDF transformation, etc).
- [`src/`](./src) – Source code for KG construction (data harvest, statistics calculation, RDF transformation, etc).
- [`run-convert.sh`](./run-convert.sh) – Shell script to convert raw data into RDF format
- [`README.md`](./README.md) – Project documentation

## Citation

```to be added```

## License

All generated content is distributed under the [CC-BY-SA 4.0.](https://creativecommons.org/licenses/by-sa/4.0/) license, in accordance with the licensing terms of the underlying data source, as specified [here](https://oai.zbmath.org/).

## Contact and Maintenance:

The construction process is designed as a reproducible pipeline over the continuously maintained zbMATH Open platform. The knowledge graph is planned to be updated periodically, approximately twice per year subject to the availability of the underlying data stream, resource and infrastructure constraint.

📧 yuni.susanti@fiz-karlsruhe.de
