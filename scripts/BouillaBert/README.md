# Deep Teleo DNA Classification

## Prepare Data

```bash
cp -R data/markers scripts/BouillaBert/experiments/fine_tune_taxa/data
cp -R data/markers scripts/BouillaBert/experiments/masking_training/data
```

## Python Virtual Environment Setup

The code was tested with **Python 3.13.6**.  
To create and activate the environment:

0. `cd scripts/BouillaBert`
1. `python3.13 -m venv .venv`
2. `source .venv/bin/activate`  
3. `pip install -r requirements.txt`  
4. `pip uninstall triton` (due to version incompatibility with DNABERT2)


## Execution

To pretrained BouillaBert-transductive on token masking task, run :
```bash
source .venv/bin/activate
./script_mlm
```
To follow training process : 
```bash
tensorboard --logdir="experiments/masking_training/outputs"
```

To finetune BouillaBert-transductive, run:

```bash
source .venv/bin/activate
./script_transductive.sh
```

To follow training process : 
```bash
tensorboard --logdir="experiments/fine_tune_taxa/outputs/transductive"
```


To finetune BouillaBert from DNABERT2 weights :
```bash
source .venv/bin/activate
./script_from_dnabert2.sh
```

