# BERTAX

This directory provides an adaptation of [rnajena/bertax_training](https://github.com/rnajena/bertax_training) to fit the specific data and taxonomy constraints of this study.


## Move data
`cp -R data/markers scripts/BERTax/data`

## Python Virtual Environment Setup

The code was tested with **Python 3.9.23**.  
To create and activate the environment:

0. `cd scripts/BERTax`
1. `python3.9 -m venv bertax_venv`  
2. `source bertax_venv/bin/activate`  
3. `pip install -r requirements.txt`  

## Download Pre-trained BERTAX Weights

Bertax's author wieghts download link: [BERTAX pre-training](https://github.com/rnajena/bertax/releases/latest/download/big_trainingset_all_fix_classes_selection.h5)

And put `big_trainingset_all_fix_classes_selection.h5` weights file at `scripts/BERTax`


## Execution

To finetune BERTAX on this study’s dataset (4 markers and 6 folds), run:

```bash
python -m models.bert_nc_finetune big_trainingset_all_fix_classes_selection.h5 --use_defined_train_test_set --store_train_data --multi_tax --store_predictions
```