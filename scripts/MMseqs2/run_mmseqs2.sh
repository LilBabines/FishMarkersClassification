#!/bin/bash
set -euo pipefail

color() {
    STARTCOLOR="\e[$2";
    ENDCOLOR="\e[0m";
    export "$1"="$STARTCOLOR%b$ENDCOLOR" 
}
color info 94m 

# Markers to iterate over
markers=(mifish teleo ac16 berry)

input_dir="data/mifish/folds/"
output_dir="result/mifish/folds/"

# Download NCBI taxdump once
TAXDUMP_DIR="ncbi-taxdump"
if [ ! -f "$TAXDUMP_DIR/names.dmp" ]; then
    mkdir -p "$TAXDUMP_DIR"
    (
        cd "$TAXDUMP_DIR"
        wget -q ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz
        tar xzf taxdump.tar.gz
    )
fi



for marker in "${markers[@]}"; do
    input_dir="data/${marker}/folds/"
    output_dir="result/${marker}/folds/"

    for fold in $(eval echo {1..6}); do
        printf $info "::Info:: [${marker}] Start taxonomic classification for fold ${fold} ...\n"

        start=$(date +%s)

        # Input dataset
        db="${input_dir}fold_${fold}/train.fasta"
        query="${input_dir}fold_${fold}/test.fasta"

        mkdir -p "${input_dir}fold_${fold}/targetDB"
        target_db="${input_dir}fold_${fold}/targetDB/targetDB"

        mkdir -p "${input_dir}fold_${fold}/queryDB"
        query_db="${input_dir}fold_${fold}/queryDB/queryDB"

        tmp="${input_dir}fold_${fold}/tmp"

        mmseqs createdb "$db" "$target_db"
        mmseqs createdb "$query" "$query_db"

        mappingT="${input_dir}fold_${fold}/train_tax.tsv"

        mmseqs createtaxdb "$target_db" "$tmp" --ncbi-tax-dump "$TAXDUMP_DIR" --tax-mapping-file "$mappingT"

        rm -rf "$tmp"

        mkdir -p "${output_dir}fold_${fold}/tax_out"
        out="${output_dir}fold_${fold}/tax_out/tax_out"

        rm -rf "$out"

        mmseqs easy-taxonomy "$query" "$target_db" "$out" "$tmp" --search-type 3 -e 1e-5 --lca-mode 4
        rm -rf "$tmp"

        # Optional TSV creation (kept commented as in original)
        # out_tsv="${output_dir}fold_${fold}/tax_out/tax_out.tsv"
        # in_tsv="${output_dir}fold_${fold}/tax_out/tax_out_lca.tsv"
        # mmseqs createtsv "$query_db" "$target_db" "$in_tsv" "$out_tsv"

        rm -rf "${input_dir}fold_${fold}/targetDB"
        rm -rf "${input_dir}fold_${fold}/queryDB"

        end=$(date +%s)
        runtime=$((end - start))
        echo "[${marker}] fold ${fold} runtime: ${runtime} seconds"
    done
done



    
