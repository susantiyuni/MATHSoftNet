# MATHSoftNet: A Multi-View Dataset of Mathematical Research Software Relationships (2026)

_MATHSoftNet_ is a multi-view dataset of mathematical research software that integrates expert-curated software metadata with networks of software relationships, community assignments, publication associations, and mathematical subject classifications. The dataset supports a broad range of research directions for systematics investigation of software and its connections to mathematical research ecosystem. 

MATHSoftNet is published on Zenodo: [DOI:10.5281/zenodo.23666256](https://doi.org/10.5281/zenodo.23666256); sample data are available on GitHub.

## Contents

- [Dataset Sizes and Statistics](#dataset-sizes-and-statistics)
- [Key Features and Data Samples](#key-features-and-data-samples)
- [Data Construction, Validation, Usage](#data-construction-validation-usage)
  - [Prerequisites](#prerequisites)
  - [Data Construction](#data-construction)
  - [Data Validation](#data-validation)
  - [Data Usage](#data-usage)
- [License](#license)
- [Citation](#citation)
- [Contact and Maintenance](#contact-and-maintenance)

## Dataset Sizes and Statistics

The following statistics are reported as of October 2026:

- Software records: 45,210
- Software relationship graph
  - Software nodes: 32,978
  - Edges: 313,364
  - Connected components: 12,402
- Software community
  - Community partitions: 197
  - Software--community links: 32,978
  - Connected components: 12,402
- Software--publication links: 324,467
- Software--MSC links: 138,973
  
## Key Features and Data Samples

- **Curated Mathematical Software Metadata Records**  
  Expert-curated software records, containing package-level metadata, including _names, authors, descriptions, homepages, keywords, dependencies, programming languages, supported operating systems, licenses, source-code links_ and more. A sample of 200 records is available here: [data/software_sample.csv](./data/software_sample.csv). 

- **Software Relationship Graph**  
  An undirected software relationship graph annotated by human-expert. We provide a sample of 200 records of the graph edges here: [data/software_edges_sample.csv](./data/software_edges_sample.csv). 

- **Software Community Assignments**  
  Software community assignments for each software node in the software relationship graphs, derived using Louvain community detection algorithm. A sample of 200 records is available here: [data/software_communities_sample.csv](./data/software_communities_sample.csv). 

- **Software–Publication Associations**  
  We link each software to the mathematical publications associated with the software. A sample of 200 records is available here: [data/software_publications_sample.csv](./data/software_publications_sample.csv). The publication lookup examples are provided here: [data/paper_lookup_sample.csv](./data/paper_lookup_sample.csv)
  
- **Software–_Mathematical Subject Classification_ (MSC) Association**  
  We link each software to their mathematical subject classification (MSC); a sample of 200 records is available here: [data/software_msc_sample.csv](./data/software_msc_sample.csv). 
  
## Data Construction, Validation, Usage

### Prerequisites

- Python 3.12+  
- Python libraries: see [requirements.txt](requirements.txt)

Install the dependencies:

```bash
pip install -r requirements.txt
```

### Data Construction

Process the dataset by running:

```bash
python src/preprocess.py
```

The detailed source code for the construction are provided in [./src/ directory](./src/).

### Data Validation

Validate the dataset by running the following script, which will check the dataset's structural consistency and metadata completeness coverage.
```bash
python src/validate.py
```

Note: To reproduce validation on sample data, update the input and output file paths in [src/validate.py](./src/validate.py) before execution.

## Data Usage

The dataset supports a broad range of research directions for systematics investigation of software and its connections to mathematical research ecosystem. To demonstrate its potential usage, we conducted a preliminary use-case study examining the extent to which expert-annotated software relationships align with relationships reflected in the scientific literature. Details are available in the [./use-case/ directory](./use-case/).

## Citation

```
@dataset{mathsoftnet2026,
  author       = {Susanti, Yuni and Azzouz-Thuderoz, Maxence and Schubotz, Moritz},
  title        = {MATHSoftNet: A Multi-View Dataset of Mathematical Research Software Relationships},
  month        = oct,
  year         = 2026,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.23666257},
  url          = {https://doi.org/10.5281/zenodo.23666257},
}
```

## License

MATHSoftNet is distributed under the [CC-BY-SA 4.0.](https://creativecommons.org/licenses/by-sa/4.0/) license, in accordance with the licensing terms of the underlying data source, refer to the detail [here](https://oai.zbmath.org/). The source code accompanying MATHSoftNet is distributed under the [MIT license](LICENSE).

## Contact and Maintenance:

MATHSoftNet is maintained by FIZ Karlsruhe, and planned to be updated annually, subject to the availability of the underlying data stream, resource and infrastructure constraint.

📧 yuni.susanti@fiz-karlsruhe.de
