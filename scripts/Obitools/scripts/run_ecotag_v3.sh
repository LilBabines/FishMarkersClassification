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
data_nfold=6
input_dir="data/teleov2_no_cefe/folds/"

#_main
## Download taxdump files and import in OBITools3 format
if [ ! -f taxdump/names.dmp ]; then
  printf $info "::Info:: Download taxdump files \n"
  mkdir -p taxdump
  wget ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz -P taxdump
  tar -zxvf taxdump/taxdump.tar.gz -C taxdump
fi
mkdir -p results/obi3/teleo/
obi import --taxdump taxdump/taxdump.tar.gz results/obi3/teleo/fish/taxonomy/my_tax

for fold in $(eval echo {1..$data_nfold}); do
  printf $info "::Info:: Start  taxonomic classification for fold ${fold} ...\n"
  
  ## Input dataset
  train="${input_dir}fold_${fold}/train.csv"
  test="${input_dir}fold_${fold}/test.csv"

  ## Convert datasets into fasta format
  intermediate="intermediate/teleo/fold_${fold}"
  mkdir -p $intermediate
  train_fa="${intermediate}/train.fasta"
  test_fa="${intermediate}/test.fasta"
  if [ ! -f $train_fa ]; then
    printf $info "::Info:: Convert datasets into OBITools extended fasta \n" 
    Rscript table_to_fasta.R -i $train -d ',' -n genus -s sequence -u TRUE -e TRUE -t taxid_ncbi -o $intermediate
    Rscript table_to_fasta.R -i $test -d ',' -n species -s sequence -u TRUE -o $intermediate
  fi
  ## Convert fasta into OBITools3 format
  train_fa3="${intermediate}/train_obi3.fasta"
  sed 's/taxid/TAXID/' $train_fa > $train_fa3
  
  ## Import train and test dataset
  printf $info "::Info:: Import datasets and build a reference database\n"
  train_pref="results/obi3/teleo/fish/train_f${fold}"
  test_pref="results/obi3/teleo/fish/test_f${fold}"
  obi import $train_fa3 $train_pref
  obi import $test_fa $test_pref

  ## Build reference database
  train_db="${train_pref}_db"
  obi build_ref_db --taxonomy results/obi3/teleo/fish/taxonomy/my_tax $train_pref $train_db

  ## Run ecotag
  printf $info "::Info:: Run ecotag \n"
  mkdir -p logs
  echo "::Info:: Run ecotag fold" $fold >> logs/ecotag_v3.log
  start_date_time="`date "+%Y-%m-%d %H:%M:%S"`"
  echo "Start:" $start_date_time >> logs/ecotag_v3.log
  ecotag_res="${test_pref}_assigned"
  obi ecotag --taxonomy results/obi3/teleo/fish/taxonomy/my_tax --ref-database $train_db $test_pref $ecotag_res
  end_date_time="`date "+%Y-%m-%d %H:%M:%S"`"
  echo "End:" $end_date_time >> logs/ecotag_v3.log

  ## Convert ecotag result
  ecotag_tsv="results/obi3/teleo/fold_${fold}_test_ecotag3.csv"
  if [ ! -f  $ecotag_tsv ]; then
    printf $info "::Info:: Convert ecotag result into csv \n"
    obi export --tab-output $ecotag_res > $ecotag_tsv
  fi
done
