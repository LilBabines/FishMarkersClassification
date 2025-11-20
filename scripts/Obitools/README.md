# OBITOOLS 4

## Setup

1. Follow the official installation guide: [OBITOOLS4 Documentation](https://obitools4.metabarcoding.org/docs/installation/)
2. Set Up R, [table_to_fasta.R](table_to_fasta.R) is executed during Obitools script. (required package : tidyverse, optparse, [phylotools](https://github.com/helixcn/phylotools), taxizedb)
3. Copy data : `cp -R data/markers scripts/Obitools/data`

## Execution 

Run the script:

```bash
cd scripts/Obitools
./run_ecotag_v4.sh
```

This script will:

1. Download the NCBI Taxonomy.
2. Convert CSV files to FASTA format using [table_to_fasta.R](table_to_fasta.R).
3. Build the database and perform queries on the trainset and testset.
4. Run ecotag to assign taxonomy to the testset.
