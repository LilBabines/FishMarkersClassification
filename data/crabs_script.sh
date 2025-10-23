mkdir taxonomy/
mkdir database/
crabs --download-taxonomy --output taxonomy/

crabs --download-mitofish --output database/mitofish.fasta
crabs --download-midori --output database/midori_12S.fasta --gb-number 261_2024-06-15 --gene srRNA --gb-type total


crabs --import --import-format mitofish --input database/mitofish.fasta --names taxonomy/names.dmp --nodes taxonomy/nodes.dmp --acc2tax taxonomy/nucl_gb.accession2taxid --output database/mitofish.txt --ranks 'superkingdom;phylum;class;order;family;genus;species'
crabs --import --import-format midori --input database/midori_12S.fasta --names taxonomy/names.dmp --nodes taxonomy/nodes.dmp --acc2tax taxonomy/nucl_gb.accession2taxid --output database/midori_12S.txt --ranks 'superkingdom;phylum;class;order;family;genus;species'
crabs --merge --input 'database/midori_12S.txt;database/mitofish.txt' --uniq --output database/merged_12S.txt


crabs --in-silico-pcr --input database/merged_12S.txt --output data/teleo/teleo.csv --forward ACACCGCCCGTCACTCT --reverse CTTCCGGTACACTTACCATG --mismatch 3
crabs --in-silico-pcr --input database/merged_12S.txt --output data/mifish/mifish.csv --forward GTCGGTAAAACTCGTGCCAGC --reverse CATAGTGGGGTATCTAATCCCAGTTTG --mismatch 3

crabs --download-midori --output database/midori_16S.fasta --gb-number 261_2024-06-15 --gene lrRNA --gb-type total
crabs --import --import-format midori --input database/midori_16S.fasta --names taxonomy/names.dmp --nodes taxonomy/nodes.dmp --acc2tax taxonomy/nucl_gb.accession2taxid --output database/midori_16S.txt --ranks 'superkingdom;phylum;class;order;family;genus;species'

crabs --in-silico-pcr --input database/midori_16S.txt --output data/berry/berry.csv --forward GACCCTATGGAGCTTTAGAC --reverse CGCTGTTATCCCTADRGTAACT --mismatch 3
crabs --in-silico-pcr --input database/midori_16S.txt --output data/ac16/ac16.csv --forward CCTTTTGCATCATGATTTAGC --reverse CAGGTGGCTGCTTTTAGGC --mismatch 3



