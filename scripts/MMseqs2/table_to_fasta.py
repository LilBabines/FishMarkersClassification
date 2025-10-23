from ete3 import NCBITaxa
ncbi = NCBITaxa()

import os 
print(os.getcwd())

import pandas as pd
import numpy as np


folds = [f'fold_{i}' for i in range(1, 7)]



def get_ncbi_id_from_taxon_name(taxon_name):
    if taxon_name=="Cepolidae":
        taxon_name = "Cepolidae (in: bony fishes)"

    return ncbi.get_name_translator([taxon_name])[taxon_name][0]

def get_lineage(taxon_id):
    return ncbi.get_lineage(taxon_id)

def get_rank(taxon_id):
    return ncbi.get_rank([taxon_id])

def get_taxon_name(taxon_id):
    return ncbi.get_taxid_translator([taxon_id])[taxon_id]

def get_taxon_name_from_lineage(lineage):
    return [get_taxon_name(taxon_id) for taxon_id in lineage]

def get_rank_from_lineage(lineage):
    return {taxon_id: rank for taxon_id, rank in get_rank(lineage).items()}


def csv_to_fasta(csv, fasta):
    with open(fasta, 'w') as f:
        for unique_family in csv['family'].unique():
            id = 1
            family_id = get_ncbi_id_from_taxon_name(unique_family)
            family_subset = csv[csv['family'] == unique_family]
            for index, row in family_subset.iterrows():
                csv.loc[index, 'unique_header'] = f'{unique_family}.{id}'
                unique_header = f'{unique_family}.{id}'
                f.write(f'>{unique_header}\n{row["sequence"]}\n')
                id += 1
    return csv

def test_csv_to_fasta(csv,fasta):
    with open(fasta, 'w') as f:
        
        for index, row in csv.iterrows():
            
            f.write(f'>{index}_test_{row["family"]}\n{row["sequence"]}\n')
    return csv

for markers in ["Ac16","berry","teleo","MiFish"]:
    for fold in folds:
        train = pd.read_csv(f'{markers}/folds/{fold}/train.csv')
        train['tax_id'] = train['family'].apply(get_ncbi_id_from_taxon_name)
        csv = csv_to_fasta(train, f'{markers}/folds/{fold}/train.fasta')
        csv_uniq_tax = csv[['unique_header', 'tax_id']]
        csv_uniq_tax.to_csv(f'{markers}/folds/{fold}/train_tax.tsv',sep=' ', index=False)
        test = pd.read_csv(f'{markers}/folds/{fold}/test.csv')
        test_csv_to_fasta(test, f'{markers}/folds/{fold}/test.fasta')