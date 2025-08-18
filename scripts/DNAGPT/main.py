# Standard imports

import torch
import sys
import os

# Import local modules

from dna_gpt.tokenizer import DNALightningDataModule, KmerTokenizer
from dna_gpt.model import DNAGPT_LT
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.loggers import CSVLogger
from pytorch_lightning.callbacks import EarlyStopping


import torch
torch.set_float32_matmul_precision('high')
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.metrics import f1_score


markers = ["mifish",'berry','Ac16']



for marker in markers:
    print("MARKER : ",marker)
    
    # Get max len sequence
    train_csv = f"data/{marker}/folds/fold_1/train_low_augment.csv"
    val_csv = f"data/{marker}/folds/fold_1/val.csv"
    test_csv = f"data/{marker}/folds/fold_1/test.csv"
    
    df_train = pd.read_csv(train_csv)
    df_val = pd.read_csv(val_csv)
    df_test = pd.read_csv(test_csv)
    
    df_total = pd.concat([df_train, df_val, df_test], ignore_index=True)
    
    max_seq = max(df_total['sequence'], key=len)
    
    # Use same tokenizer spec as training
    special_tokens = (['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
              + ["+", '-', '*', '/', '=', "&", "|", "!"]
              + ['M', 'B'] + ['P']
              + ['R', 'I', 'K', 'L', 'O', 'Q', 'S', 'U', 'V']
              + ['W', 'Y', 'X', 'Z'])
    tokenizer = KmerTokenizer(k=6, reserved_tokens=special_tokens, dynamic_kmer=True)
    max_token_size = len(tokenizer.encode(max_seq, pad=False, max_len=1000))
    
    print("Max len : ",max_token_size)
    
                         
    all_families = sorted(df_train['family'].unique())
    label2id = {label: i for i, label in enumerate(all_families)}
    id2label = {i: label for label, i in label2id.items()}
    
    num_classes = len(label2id)
    
    batch_size = 8
    max_epochs = 20
    
    for fold in range(6):
        print("=============================")
        print(f"\nFold : {fold}\n")
        
    
        os.makedirs(f"results_pl/{marker}/fold_{fold}",exist_ok=True)
        
        datamodule = DNALightningDataModule(
            marker=marker,
            fold=fold+1,
            label2id=label2id,
            batch_size=batch_size,
            num_workers=1,
            max_len=max_token_size
        )
        datamodule.setup()
        dataloader = datamodule.train_dataloader()
        # Calcul du nombre d'étapes pour scheduler
        steps_per_epoch = len(dataloader)
        total_steps = steps_per_epoch * max_epochs
        warmup_steps = steps_per_epoch * 3  # warmup de 3 époques
            
        DNA_module = DNAGPT_LT(total_steps=total_steps, warmup_steps=warmup_steps,vocab_size= len(datamodule.tokenizer),num_classes=num_classes)
        
        
        # Load weights
        
        checkpoint_path = r"checkpoints/dna_gpt0.1b_m.pth"
        state_dict = torch.load(checkpoint_path, map_location='cpu')
        DNA_module.model.load_state_dict(state_dict, strict=False) # no classification head in pre-trained checkpoint
    
        checkpoint_callback = ModelCheckpoint(
            monitor="val_macro_f1",               # ou "val_accuracy" si tu l'utilises
            dirpath=f"results_pl/{marker}/fold_{fold}",
            filename="best_checkpoint",
            save_top_k=1,
            mode="max",                       # "min" pour loss, "max" pour accuracy
         #   every_n_train_steps=steps_per_epoch // 4  # tous les 25% d'une epoch
        )
        early_stop = EarlyStopping(monitor="val_macro_f1", patience=16, mode="max") # patience 16 = 4 epoch because 4 val per epoch
        
        logger = CSVLogger(save_dir=f"results_pl/{marker}/fold_{fold}", name="lightning_logs")
    
        trainer = Trainer(
            max_epochs=max_epochs,
            accelerator="auto",
            #precision=16,  # ou 32 selon ton hardware
            val_check_interval=0.25,  # 4 validations/epoch
            callbacks=[checkpoint_callback,early_stop],
            logger=logger,
            gradient_clip_val=1.0,
            enable_progress_bar=False# Optionnel mais utile avec AdamW
        )
        
        
        
        # Fit
        trainer.fit(DNA_module, datamodule=datamodule)
        
        # Test (en chargeant le meilleur modèle)
        trainer.test(DNA_module, datamodule=datamodule, ckpt_path=checkpoint_callback.best_model_path)






