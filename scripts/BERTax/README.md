# BERTAX

This directory provides an adaptation of [rnajena/bertax_training](https://github.com/rnajena/bertax_training) to fit the specific data and taxonomy constraints of this study.

## Python Virtual Environment Setup

The code was tested with **Python 3.9.23**.  
To create and activate the environment:

1. `python3.9 -m venv bertax_venv`  
2. `source bertax_venv/bin/activate`  
3. `pip install -r requirements.txt`  

## Download Pre-trained BERTAX Weights

Follow the author’s instructions here: [BERTAX installation guide](https://github.com/rnajena/bertax?tab=readme-ov-file#local-pip-only-installation)

## Execution

To finetune BERTAX on this study’s dataset (4 markers and 6 folds), run:

```bash
python -m models.bert_nc_finetune path_to_pt_bertax/pre_trained.h5 \
    --use_defined_train_test_set \
    --store_train_data \
    --multi_tax \
    --store_predictions
```