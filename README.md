# Fish Marker Family Assignment Benchmark

This repository contains the code and data used for the benchmark study on fish marker family assignment, as described in the paper "Benchmarking Deep Learning Methods for Fish Marker Family Assignment".

## Data

For this study, we utilized the [MIDORI2 Reference](https://www.reference-midori.info/download.php) and [MitoFish](https://mitofish.aori.u-tokyo.ac.jp/) databases. Teleo, Mifish, Berry and Ac16 markers extraction was performed using the [CRABS tool](https://doi.org/10.1111/1755-0998.13741) via Docker execution (details provided in [data/README.md](data/README.md))


## Deep Classification

We pre-trained and fine-tuned various models, including [DNABERT-2](https://doi.org/10.48550/arXiv.2306.15006), with more to come soon. To reproduce the results from the paper or to fine-tune/infer using your own data, please follow the instructions in the [BerTeleo directory](./scripts/BERTeleo/README.md).

### Libraries
Here is an overview of the main Python librairies used in this project.

* [![PyTorch](https://img.shields.io/badge/PyTorch-%23ee4c2c.svg?logo=pytorch&logoColor=white)](https://pytorch.org/) - To handle deep learning loops and dataloaders

* [![Hydra](https://img.shields.io/badge/Hydra-%23729DB1.svg?logo=hydra&logoColor=white)](https://hydra.cc/docs/intro/) - To handle models' hyperparameters and custom experiments
* [![Model on HF](https://huggingface.co/datasets/huggingface/badges/resolve/main/model-on-hf-sm.svg)](https://huggingface.co/) - To load, build and train models


## Other methods (Obitools, MMseq2, Kmer)

## Team 

**Lab :** UMR MARBEC - Montpellier France 

**Project :** Fish Predict 

**Author :** 
- Auguste Verdier - auguste.verdier@umontpellier.fr
- Morgane Bruno - morgane.bruno@cefe.cnrs.fr
- Simon Bettinger - sbettinger33@gmail.com

