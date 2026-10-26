# MATHSoftNet

## Overview

MATHSoftNet is a multi-view dataset designed to support systematic investigations of the software ecosystem and its connections to the broader landscape of mathematical research. MATHSoftNet integrates expert-curated and automatically generated networks of software relationships with software-specific metadata and bibliographic information. Additionally, it includes software communities derived from graph topology, supporting the exploration of the mathematic software ecosystem's structure and organization.

**Update**: MATHSoftNet is archived on Zenodo for long-term preservation and accessibility; we provide a sample of the data on GitHub.

---
## Contents

- [Dataset Sizes and Statistics](#dataset-sizes-and-statistics)
- [Key Features](#key-features)
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
  
## Key Features

- **Curated Mathematical Software Metadata Records**  
  Compliant with RDF and Semantic Web standards, the zbMATH Open KG is built entirely from RDF triples using widely adopted ontologies and vocabularies. A sample of 200 records is available here: [`data/subset-200.ttl`](./data/subset-200-v2.ttl). 

- **Software Relationship Graph**  
  In addition to standard bibliographic metadata, the KG incorporates annotated mathematical publications.

- **Software Community Assignment**  
  Its comprehensive and long-term coverage enable long-range intellectual analysis such as historically-grounded retrieval.

- **Software--Publication Associations**  
  A SPARQL endpoint (temporarily at [**SPARQL endpoint url**](http://212.227.170.235:8890/sparql)) 
  
- **Software-–_Mathematical Subject Classification_ (MSC) Association**  
URI resolution for core entities (i.e., publications, scholars, software references). 
  
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
