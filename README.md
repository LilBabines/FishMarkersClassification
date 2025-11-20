# Fish Marker Family Assignment Benchmark

This repository contains the code and data used for the benchmark study on fish marker family assignment, as described in the paper "Benchmarking Deep Learning Methods for Fish Marker Family Assignment".

## Data

For this study, we utilized the [MIDORI2 Reference](https://www.reference-midori.info/download.php) and [MitoFish](https://mitofish.aori.u-tokyo.ac.jp/) databases. Teleo, Mifish, Berry and Ac16 markers extraction was performed using the [CRABS tool](https://doi.org/10.1111/1755-0998.13741) via Docker execution (details provided in [data/README.md](data/README.md))


## Methods
Detailed information about the requirements and execution of each script is available in their respective directories under `scripts/`.  
All methods were tested on a Linux operating system. For use on other platforms, please refer to the original documentation provided by the authors (links below).
- [OBITOOLS 4](scripts/Obitools/README.md)  ( [code](https://github.com/metabarcoding/obitools4))
- [MMSEQS2](scripts/MMseqs2/README.md) ([code](https://github.com/soedinglab/MMseqs2)/[paper](https://www.nature.com/articles/nbt.3988))
- [BERTAX](scripts/BERTax/README.md)  ([code](https://github.com/rnajena/bertax)/[paper](https://doi.org/10.1073/pnas.2122636119))
- [BouillaBert](scripts/BouillaBert/README.md) ([code](https://github.com/MAGICS-LAB/DNABERT_2)/[paper](https://arxiv.org/abs/2306.15006))
- [DNAGPT](scripts/DNAGPT/README.md) ([code](https://github.com/TencentAILabHealthcare/DNAGPT)/[paper](https://www.biorxiv.org/content/10.1101/2023.07.11.548628v2.full.pdf)
)

## Results

To enable figure reproduction, the prediction [CSV file ](results/all_predictions_pre_compute.csv) is provided along with the corresponding scripts [script](results/figure_scripts.py).

## Team 

**Lab :** MARBEC X CEFE - Montpellier France 

**Project :** Fish Predict 

**Author :** 

- Simon Bettinger - sbettinger33@gmail.com
- Morgane Bruno - morgane.bruno@cefe.cnrs.fr
- Auguste Verdier - auguste.verdier@umontpellier.fr
