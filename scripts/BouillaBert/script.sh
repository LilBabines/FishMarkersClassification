#!/bin/bash

source ~/python-venv/teleo/bin/activate


for cfg in config_teleo ; do

  for tn in train_augment_0.15.csv; do
    python experiments/fine_tune_taxa/main.py --config-name=$cfg data.train_name=$tn hydra.run.dir=experiments/fine_tune_taxa/outputs/test_augment/${cfg}/${tn}
  done
done
