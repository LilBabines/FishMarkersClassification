# -*- coding: utf-8 -*-
# Copyright (c) 2022, Tencent Inc. All rights reserved.
# Author: chenchenqin
# Data: 2022/12/14 19:15
import torch
from torch import Tensor
import torch.nn as nn
import pytorch_lightning as pl
from transformers import get_cosine_schedule_with_warmup
from .gpt import GPT, LayerNorm
from torchmetrics.classification import MulticlassAccuracy, MulticlassF1Score
from torch.optim import AdamW
from sklearn.metrics import precision_recall_fscore_support as prf


class DNAGPT(GPT):
    """ DNAGPT gene sequence model

    References:
        1) the official GPT-2 TensorFlow implementation released by OpenAI:
        https://github.com/openai/gpt-2/blob/master/src/model.py
        2) huggingface/transformers PyTorch implementation:
        https://github.com/huggingface/transformers/blob/main/src/transformers/models/gpt2/modeling_gpt2.py
    """

    def __init__(self,
                 vocab_size=7,
                 max_len=1024,
                 num_layers=3,
                 num_heads=3,
                 embedding_dim=48,
                 bias=True,
                 num_classes=None
                 ):
        super().__init__(vocab_size,
                         max_len,
                         num_layers,
                         num_heads,
                         embedding_dim,
                         bias=bias,
                         include_head=False)
        self.number_embedding = nn.Sequential(
            nn.Linear(1, self.embedding_dim, bias=bias),
            nn.SiLU(inplace=True),
            LayerNorm(self.embedding_dim, bias=bias),
            nn.Linear(self.embedding_dim, self.embedding_dim, bias=bias)
        )
        self.mlm_head = nn.Sequential(
            nn.Linear(self.embedding_dim, self.embedding_dim, bias=bias),
            nn.SiLU(inplace=True),
            LayerNorm(self.embedding_dim, bias=bias),
            nn.Linear(self.embedding_dim, vocab_size, bias=bias)
        )
        self.num_regression = nn.Sequential(
            nn.Linear(self.embedding_dim, self.embedding_dim, bias=bias),
            nn.SiLU(inplace=True),
            LayerNorm(self.embedding_dim, bias=bias),
            nn.Linear(self.embedding_dim, 1, bias=bias)
        )
        
        self.num_classes = num_classes

        if self.num_classes is not None:
            self.classification_head = nn.Sequential(
                nn.Linear(self.embedding_dim, self.embedding_dim, bias=bias),
                nn.SiLU(inplace=True),
                LayerNorm(self.embedding_dim, bias=bias),
                nn.Linear(self.embedding_dim, num_classes, bias=bias)
            )

    def _embedding_impl(self,
                        tokens):
        bs, _ = tokens.size()
        token_emb = self.transformer.wte(tokens)
        
        seq_len = token_emb.shape[1]
        pos = torch.arange(0, seq_len,
                           dtype=torch.long,
                           device=token_emb.device).unsqueeze(0)
        pos_emb = self.transformer.wpe(pos)
        emb = token_emb + pos_emb
        return emb

    def _transformer_impl(self, embeddings):
        x = self.transformer.drop(embeddings)
        for block in self.transformer.h:
            x = block(x)

        return self.transformer.ln_f(x)

    def _head_impl(self, hiddens):
        mlm = self.mlm_head(hiddens)
       
        return mlm


    def forward(self, token_ids, mode="mlm"):
        x = self._embedding_impl(token_ids)
        x = self._transformer_impl(x)

        if self.num_classes is not None and mode == "classification":
            pooled = x[:, -1, :]  # ou x.mean(dim=1) si plus adapté
            return self.classification_head(pooled)  # [B, num_classes]

        return self._head_impl(x)  # [B, T, vocab_size]

    @classmethod
    def from_name(cls, name, vocab_size,num_classes):
        model_cfgs = {
            'dna_gpt0.1b_h': dict(vocab_size=vocab_size,
                                  max_len=4096,
                                  num_layers=12,
                                  num_heads=12,
                                  embedding_dim=768,
                                  bias=False,
                                  num_classes=num_classes),
            'dna_gpt0.1b_m': dict(vocab_size=vocab_size,
                                  max_len=512,
                                  num_layers=12,
                                  num_heads=12,
                                  embedding_dim=768,
                                  bias=False,
                                  num_classes=num_classes),
            'dna_gpt3b_m': dict(vocab_size=vocab_size,
                                max_len=512,
                                num_layers=60,
                                num_heads=64,
                                embedding_dim=2048,
                                bias=False,
                                num_classes=num_classes)
        }
        assert name in model_cfgs, f"unkown model name, only suport: {list(model_cfgs.keys())}"
        cfg = model_cfgs[name]
        return cls(**cfg)


class DNAGPT_LT(pl.LightningModule):
    
    def __init__(self, total_steps, warmup_steps, vocab_size,num_classes ):
        
        super().__init__()
        
        self.model = DNAGPT.from_name('dna_gpt0.1b_m', vocab_size=vocab_size,num_classes=num_classes)
        self.criterion = torch.nn.CrossEntropyLoss()
        self.lr = 3e-5
        self.weight_decay = 1e-1
        self.total_steps = total_steps
        self.warmup_steps = warmup_steps
        
        # Metrics
        self.train_acc = MulticlassAccuracy(num_classes=num_classes, average='macro')
        self.val_acc = MulticlassAccuracy(num_classes=num_classes, average='macro')
        self.test_acc = MulticlassAccuracy(num_classes=num_classes, average='macro')

        self.train_f1 = MulticlassF1Score(num_classes=num_classes, average='macro')
        self.val_f1 = MulticlassF1Score(num_classes=num_classes, average='macro')
        self.test_f1 = MulticlassF1Score(num_classes=num_classes, average='macro')

    def forward(self, x: Tensor) -> Tensor:
        return self.model(x, mode="classification")

    def training_step(self, batch: tuple[Tensor, Tensor], batch_idx: int) -> Tensor:

        x, y = batch
        logits = self.forward(x)
        loss = self.criterion(logits, y)
    
        preds = torch.argmax(logits, dim=1)
        self.train_acc.update(preds, y)
        self.train_f1.update(preds, y)
    
        self.log("train_loss", loss, prog_bar=False)

        # Log du learning rate
        lr = self.lr_schedulers().get_last_lr()[0]
        self.log("lr", lr, prog_bar=False, on_step=True, on_epoch=False)
        
        return loss
    
    def on_training_epoch_end(self):
        self.log("train_macro_acc", self.train_acc.compute(), prog_bar=False)
        self.log("train_macro_f1", self.train_f1.compute(), prog_bar=False)
        self.train_acc.reset()
        self.train_f1.reset()

        return loss
    
    def validation_step(self, batch: tuple[Tensor, Tensor], batch_idx: int) -> Tensor:
        
        x, y = batch
        logits = self.forward(x)
        loss = self.criterion(logits, y)
        preds = torch.argmax(logits, dim=1)
    
        self.val_acc.update(preds, y)
        self.val_f1.update(preds, y)
    
        self.log("val_loss", loss, prog_bar=False)
        return loss
    
    def on_validation_epoch_end(self):
        self.log("val_macro_acc", self.val_acc.compute(), prog_bar=False)
        self.log("val_macro_f1", self.val_f1.compute(), prog_bar=False)
        self.val_acc.reset()
        self.val_f1.reset()

    def on_test_epoch_start(self):
        self.test_preds = []
        self.test_labels = []
        
    def test_step(self, batch: tuple[Tensor, Tensor], batch_idx: int) -> Tensor:
        x, y = batch
        logits = self.forward(x)
        preds = torch.argmax(logits, dim=1)
        loss = self.criterion(logits, y)
    
        self.test_acc.update(preds, y)
        self.test_f1.update(preds, y)

        self.test_preds.append(preds.cpu())
        self.test_labels.append(y.cpu())
    
        return loss
    
    
    def on_test_epoch_end(self):
        
        self.log("test_macro_acc", self.test_acc.compute())
        self.log("test_macro_f1", self.test_f1.compute())
        self.test_acc.reset()
        self.test_f1.reset()

        p,r,f,s = prf(self.test_labels,self.test_preds,average='macro',zero_division=0)
        
        self.log("test_sklearn_precision", p)
        self.log("test_sklearn_recall", r)
        self.log("test_sklearn_f1", f)

        # Stockage pour consultation après test

        self.final_test_preds = torch.cat(self.test_preds).numpy()
        self.final_test_labels = torch.cat(self.test_labels).numpy()
        
        self.test_preds.clear()
        self.test_labels.clear()


    def configure_optimizers(self):
        optimizer = AdamW(self.parameters(), lr=self.lr, weight_decay=self.weight_decay)
        scheduler = get_cosine_schedule_with_warmup(
            optimizer,
            num_warmup_steps=self.warmup_steps,
            num_training_steps=self.total_steps
        )
        return {
            'optimizer': optimizer,
            'lr_scheduler': {
                'scheduler': scheduler,
                'interval': 'step',
                'frequency': 1
            }
        }
