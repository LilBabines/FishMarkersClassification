#!/bin/bash

for cfg in config_teleo config_mifish config_ac16 config_berry ; do

  python experiments/masking_training/main.py --config-name=$cfg trainer.kwargs.num_train_epochs=1

done
