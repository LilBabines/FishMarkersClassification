# MMseqs2 

## Setup

1. Follow the official installation guide: [MMseqs2 Documentation](https://mmseqs.com/latest/userguide.pdf)
via brew ([install brew](https://brew.sh/))  : brew install mmseqs2`



2. Prepare Data

```bash
cp -R data/markers scripts/MMseqs2/data
cd scripts/MMseqs2
source scripts/BouillaBert/.venv/bin/activate
python table_to_fasta.py 
```

Move data and Convert data csv to .fasta file (package required : pandas, numpy, ete3, you can use the venv created for [BouillaBert](../BouillaBert/requirements.txt) )

## Execution 

Run the script:

```bash
./run_mmseqs2.sh
```