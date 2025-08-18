# OBITOOLS 4

## Setup

Follow the official installation guide: [OBITOOLS4 Documentation](https://obitools4.metabarcoding.org/docs/installation/)

## Execution 

Run the script:

```bash
./run_ecotag_v4.sh
```


This script will:

1. Download the NCBI Taxonomy.
2. Convert CSV files to FASTA format using table_to_fasta.R.
3. Build the database and perform queries on the trainset and testset.
4. Run ecotag to assign taxonomy to the testset.





