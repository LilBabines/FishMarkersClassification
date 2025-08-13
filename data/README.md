# DATA pre-process

Download, marker extraction,  cleanning and prepare data can be done by executing `download_markerExtraction_cleaning_prepare_data.sh`.

We can also download resulting data from ####TODO###.

## Data Used

* [MIDORI](https://www.reference-midori.info/download.php)
* [MitoFish](https://mitofish.aori.u-tokyo.ac.jp/)

## Download & Marker Extraction via CRABS

* [CRABS](https://doi.org/10.1111/1755-0998.13741) v.1.7.7.0 / DOCKER IMAGE ID : 9fd9821ce055. CRABS instalation [github](https://github.com/gjeunen/reference_database_creator?tab=readme-ov-file#installing-crabs), command used :
    * `crabs --download-taxonomy`
    * `crabs --import`
    * `crabs --download-midori ` , `crabs --download-mitofish`
    * `crabs --in-silico-pcr`

## Cleaning & Preparing Data via Python

Processing steps from the two remaining `output_pga_3.tsv` ([pre_process.py functions](pre_process.py) ) :
1. `pre_process(mitophish, ncbi)`, clean raw data by fill Nan values, keep only fish, remove short ( less than 20 ) or uncertain (contains nucleotide `N`) sequences
2. `fold_6_data(data_path, n_splits=6)`, build a 6 fold partition, stratified at genus level (genus in val or test are not in train)
3. `def get_repartition(data_path)`, check fold repartition
4. `build_file(data_path)`, save 6_fold dataset with `train.csv`, `val.csv`, `test.csv` and `test_genus.json` (json list contains genus in val and test)
5. `mutate_data_fold(data_path)`, mutate data for deep-learning, mutate ratio are based genetic diversity analyse.

