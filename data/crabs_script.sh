mkdir taxonomy/
mkdir database/
crabs --download-taxonomy --output taxonomy/
crabs --download-mitofish --output database/mitofish.fasta
crabs --download-midori --output database/midori.fasta --gb-number 261_2024-06-15 --gene srRNA --gb-type total

crabs --import --import-format mitofish --input database/mitofish.fasta --names taxonomy/names.dmp --nodes taxonomy/nodes.dmp --acc2tax taxonomy/nucl_gb.accession2taxid --output database/mitofish.txt --ranks 'superkingdom;phylum;class;order;family;genus;species'
crabs --import --import-format midori --input database/midori.fasta --names taxonomy/names.dmp --nodes taxonomy/nodes.dmp --acc2tax taxonomy/nucl_gb.accession2taxid --output database/midori.txt --ranks 'superkingdom;phylum;class;order;family;genus;species'

crabs --merge --input 'database/midori.txt;database/mitofish.txt' --uniq --output database/merged.txt


crabs --in-silico-pcr --input database/merged.txt --output markers/teleo/teleo.csv --forward ACACCGCCCGTCACTCT --reverse CTTCCGGTACACTTACCATG --mismatch 3
crabs --in-silico-pcr --input database/merged.txt --output markers/mifish/mifish.csv --forward GTCGGTAAAACTCGTGCCAGC --reverse CATAGTGGGGTATCTAATCCCAGTTTG --mismatch 3
crabs --in-silico-pcr --input database/merged.txt --output markers/berry/berry.csv --forward GACCCTATGGAGCTTTAGAC --reverse CGCTGTTATCCCTADRGTAACT --mismatch 3
crabs --in-silico-pcr --input database/merged.txt --output markers/ac16/ac16.csv --forward CCTTTTGCATCATGATTTAGC --reverse CAGGTGGCTGCTTTTAGGC --mismatch 3



