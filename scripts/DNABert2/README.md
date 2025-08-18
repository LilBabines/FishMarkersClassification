# Deep Teleo DNA Classification


## Python Virtual Environment Setup

The code was tested with **Python 3.13.6**.  
To create and activate the environment:

1. `python3.13 -m venv dnabert2_venv`
2. `source dnabert2_venv/bin/activate`  
3. `pip install -r requirements.txt`  
4. `pip uninstall triton` (due to version incompatibility with DNABERT2)

## Execution

To pretrained DNABERT2 on token masking task, run :
```bash
python experiments/masking_training/main.py
```
To finetune DNABERT2 on this study’s dataset (4 markers and 6 folds), run:

```bash
python experiments/fine_tune_taxa/main.py
```