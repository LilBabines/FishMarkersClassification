# Data Pre-processing

Data download, marker extraction, cleaning, and preparation can be performed by executing `crabs_script.sh` and `pre_process.py`.  
Please note that the resulting dataset may differ from the one originally used in the study due to database updates, as well as some taxonomy cleaning that was manually supervised.  
For reproducibility, we recommend to directly use [data](data/).

## Data Used

* [MIDORI](https://www.reference-midori.info/download.php)
* [MitoFish](https://mitofish.aori.u-tokyo.ac.jp/)

## Download & Marker Extraction via CRABS

* [CRABS](https://doi.org/10.1111/1755-0998.13741) v.1.7.7.0 / DOCKER IMAGE ID : 9fd9821ce055. CRABS instalation [github](https://github.com/gjeunen/reference_database_creator?tab=readme-ov-file#installing-crabs), command used :
    * `crabs --download-taxonomy`
    * `crabs --import`
    * `crabs --download-midori ` , `crabs --download-mitofish`
    * `crabs --in-silico-pcr`
    * `crabs --merge`

## Cleaning & Preparing Data via Python

Processing steps from the two remaining crabs `csv` outputs ([pre_process.py functions](pre_process.py) ) :
1. `pre_process(mitophish, ncbi)`, clean raw data by fill Nan values, keep only fish, remove short ( less than 20 ) or uncertain (contains nucleotide `N`) sequences
2. `fold_6_data(data_path, n_splits=6)`, build a 6 fold partition, stratified at genus level (genus in val or test are not in train)
3. `get_repartition(data_path)`, check fold repartition
4. `build_file(data_path)`, save 6_fold dataset with `train.csv`, `val.csv`, `test.csv` and `test_genus.json` (json list contains genus in val and test)
5. `mutate_data_fold(data_path)`, mutate data for deep-learning

