#!/bin/bash

for cfg in config_teleo config_mifish config_ac16 config_berry ; do

  python experiments/fine_tune_taxa/main.py --config-name=$cfg trainer.kwargs.num_train_epochs=1 hydra.run.dir=experiments/fine_tune_taxa/outputs/transductive/${cfg}

done
