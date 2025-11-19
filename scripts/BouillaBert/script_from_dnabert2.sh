#!/bin/bash

for cfg in config_teleo config_mifish config_ac16 config_berry ; do

  python experiments/fine_tune_taxa/main.py --config-name=$cfg hydra.run.dir=experiments/fine_tune_taxa/outputs/from_dnabert2/${cfg} model.local=False

done
