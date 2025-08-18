# Deep Teleo DNA Classification

## Setup (tested on Ubuntu24.04)

**0.** Should set-up CUDA for pytorch training efficency.

**1.** Create python *venv* `python3.13 -m venv dnabert2_venv`


**2.** Install package depedency `pip install -r requirements.txt`
**3** Uninstall triton `pip uninstall triton` due to DNABERT2 version inconsistency




## Usage 

### Reproduicing paper results :
1. Prepare data :

2. Launch [experiments/BouillaBert/main.py](experiments/BouillaBert/main.py), it will fine_tune DNABERT-2 model than infer on test_set.



