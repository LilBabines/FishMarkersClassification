#!/bin/bash

###############################################
# Script Name: run_ecotag_v3.sh
# Description:
#   Run ecotag to assign test sequences to taxa 
#   from the train dataset
# Args:
#   - config: yaml config file
# Requirements: OBITools3
# Author:  Morgane BRUNO
# Email: morgane.bruno@cefe.cnrs.fr
# Licence MIT
################################################

color() {
    STARTCOLOR="\e[$2";
    ENDCOLOR="\e[0m";
    export "$1"="$STARTCOLOR%b$ENDCOLOR" 
}
color info 94m 

## Read config file
marker="Ac16"
data_nfold=6
input_dir="data/${marker}/folds/"

#_main
## Download taxdump files and import in OBITools3 format
if [ ! -f taxo/names.dmp ]; then
  printf $info "::Info:: Download taxdump files \n"
  mkdir -p taxo
  wget ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz -P taxo
  tar -zxvf taxo/taxdump.tar.gz -C taxo
fi
mkdir -p results/obi4/${marker}/

for fold in $(eval echo {1..$data_nfold}); do

  mkdir results/obi4/${marker}/fold_${fold}

  printf $info "::Info:: Start  taxonomic classification for fold ${fold} ...\n"
  start=$(date +%s)

  
  
  ## Input dataset
  train="${input_dir}fold_${fold}/train.csv"
  test="${input_dir}fold_${fold}/test.csv"

  ## Convert datasets into fasta format
  intermediate="intermediate/${marker}/fold_${fold}"
  mkdir -p $intermediate
  train_fa="${intermediate}/train.fasta"
  test_fa="${intermediate}/test.fasta"
  if [ ! -f $train_fa ]; then
    printf $info "::Info:: Convert datasets into OBITools extended fasta \n" 
    Rscript table_to_fasta.R -i $train -d ',' -n genus -s sequence -u TRUE -e TRUE -t taxid_ncbi -o $intermediate
    Rscript table_to_fasta.R -i $test -d ',' -n species -s sequence -u TRUE -o $intermediate
  fi





  ## Index train datasets
  printf $info "::Info:: Index train.fasta \n"
  train_idx="${intermediate}/train_obi4_idx.fasta"
  obirefidx -t taxo $train_fa > $train_idx

  ## Run ecotag
  ecotag_res="results/obi4/${marker}/fold_${fold}/test.ecotag"
  if [ ! -f  $ecotag_res ]; then
    printf $info "::Info:: Run ecotag \n"
    mkdir -p logs
    echo "::Info:: Run ecotag fold" $fold >> logs/ecotag_v4.log
    start_date_time="`date "+%Y-%m-%d %H:%M:%S"`"
    echo "Start:" $start_date_time >> logs/ecotag_v4.log
    obitag --reference-db $train_idx --taxonomy taxo $test_fa > $ecotag_res
    end_date_time="`date "+%Y-%m-%d %H:%M:%S"`"
    echo "End:" $end_date_time >> logs/ecotag_v4.log
  fi
  end=$(date +%s)
  runtime=$((end - start))

  echo "Temps d'exécution : $runtime secondes"
done
