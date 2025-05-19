#!/bin/bash

color() {
    STARTCOLOR="\e[$2";
    ENDCOLOR="\e[0m";
    export "$1"="$STARTCOLOR%b$ENDCOLOR" 
}
color info 94m 

input_dir="teleov2_no_cefe/folds/"
output_dir="result/teleov2_no_cefe/folds/"

if [ ! -f ncbi-taxdump/names.dmp ]; then

    mkdir ncbi-taxdump && cd ncbi-taxdump
    wget ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz
    tar xzvf taxdump.tar.gz
    cd -
fi


for fold in $(eval echo {1..6}); do

    printf $info "::Info:: Start  taxonomic classification for fold ${fold} ...\n"

    ## Input dataset
    db="${input_dir}fold_${fold}/train.fasta"
    query="${input_dir}fold_${fold}/test.fasta"

    mkdir -p ${input_dir}fold_${fold}/targetDB
    target_db="${input_dir}fold_${fold}/targetDB/targetDB"

    mkdir -p ${input_dir}fold_${fold}/queryDB
    query_db="${input_dir}fold_${fold}/queryDB/queryDB"

    tmp="${input_dir}fold_${fold}/tmp"

    mmseqs createdb $db $target_db
    mmseqs createdb $query $query_db

    mappingT="${input_dir}fold_${fold}/train_tax.tsv"

    
    mmseqs createtaxdb $target_db $tmp --ncbi-tax-dump ncbi-taxdump --tax-mapping-file $mappingT

    rm -rf $tmp

    mkdir -p ${output_dir}fold_${fold}/tax_out
    out="${output_dir}fold_${fold}/tax_out/tax_out"

    rm -rf $out

    mmseqs easy-taxonomy $query $target_db $out $tmp --search-type 3 -e 1e-5 --lca-mode 4 #--min-seq-id 0.1 -e 1e-5  --search-type 3 # --cov-mode 0  --orf-filter 0 -c 1

    rm -rf $tmp
    # out_tsv="${input_dir}fold_${fold}/tax_out/tax_out.tsv"
    # in_tsv="${input_dir}fold_${fold}/tax_out/tax_out_lca.tsv"
    # mmseqs createtsv $query_db $target_db $in_tsv $out_tsv

    rm -rf ${input_dir}fold_${fold}/targetDB
    rm -rf ${input_dir}fold_${fold}/queryDB
done



    