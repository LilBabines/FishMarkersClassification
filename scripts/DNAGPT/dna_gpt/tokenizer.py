# -*- coding: utf-8 -*-
# Copyright (c) 2023, Tencent Inc. All rights reserved.
# Author: chenchenqin
# Data: 2023/9/4 12:01
import itertools as it
import re
from typing import Optional, Union

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset
import pytorch_lightning as pl
import pandas as pd


class KmerTokenizer:

    def __init__(self,
                 k=3,
                 reserved_tokens=None,
                 dynamic_kmer=True):
        self.k = k
        if reserved_tokens is None:
            reserved_tokens = []
        assert len(reserved_tokens) == len(set(reserved_tokens)), "duplicated token in list"
        self.reserved_tokens = [f"<{t}>" for t in reserved_tokens]
        # N is unkown base in reference seqence
        self.bases = 'NAGCT'
        self.kmers = self.get_base_kmers(self.k, dynamic_kmer=dynamic_kmer)
        self.idx_to_token = self.reserved_tokens + self.kmers
        self.token_to_idx = {token: idx for idx, token in enumerate(self.idx_to_token)}
        self.pad_id = self.token_to_idx['<P>']
        self.unk_id = 0

    def get_base_kmers(self, k, dynamic_kmer=True):
        kmers = []
        start = 1 if dynamic_kmer else k
        for i in range(start, k + 1):
            kmers += list(it.product(self.bases, repeat=i))
        return [''.join(m) for m in kmers]

    def __len__(self):
        return len(self.idx_to_token)

    def piece_to_id(self, token: str):
        return self.token_to_idx.get(token, self.unk_id)

    def id_to_piece(self, token_id):
        assert 0 <= token_id < len(self), f"out of range of token id {token_id}, max {len(self)}"
        return self.idx_to_token[token_id]

    def _encode(self, token):
        if not isinstance(token, (list, tuple, np.ndarray)):
            return self.piece_to_id(token)
        return [self._encode(t) for t in token]

    def tokenize(self, text):
        tokens = re.split(r"[<>]", text)
        new_tokens = []
        n = self.k
        for t in tokens:
            if not t:
                continue

            if f"<{t}>" in self.reserved_tokens:
                new_tokens.append(f"<{t}>")
            else:
                seq = t
                # split kmers
                chunks = [seq[i:i + n] for i in range(0, len(seq), n)]
                new_tokens += chunks
        return new_tokens

    def encode(self,
               text,
               max_len: int = -1,
               pad: bool = False,
               device: Optional[torch.device] = None,
               to_tensor=True):
        pieces = self.tokenize(text)
        tokens = self._encode(pieces)
        if max_len > 0:
            tokens = tokens[:max_len]

        if pad and len(tokens) < max_len:
            tokens += [self.pad_id] * (max_len - len(tokens))

        if to_tensor:
            tokens = torch.tensor(tokens, dtype=torch.long, device=device)

        return tokens

    def decode(self, token_ids: Union[torch.Tensor, np.ndarray]) -> str:
        if isinstance(token_ids, (torch.Tensor, np.ndarray)):
            token_ids = token_ids.tolist()

        seq = "".join([self.id_to_piece(tid) for tid in token_ids])
        return seq

    def __call__(self,
             text,
             padding=False,
             truncation=False,
             max_length=None,
             return_tensors=None,
             **kwargs):
        if isinstance(text, str):
            texts = [text]
        else:
            texts = text  # batch mode
    
        encodings = []
        for t in texts:
            tokens = self.encode(
                t,
                max_len=max_length if truncation else -1,
                pad=padding,
                to_tensor=False
            )
            encodings.append(tokens)
    
        # Padding à la main si batch et padding demandé
        if padding:
            max_len = max(len(seq) for seq in encodings)
            encodings = [
                seq + [self.pad_id] * (max_len - len(seq)) for seq in encodings
            ]
    
        result = {
            "input_ids": torch.tensor(encodings, dtype=torch.long)
        }
    
        if padding:
            attention_masks = [
                [1 if token != self.pad_id else 0 for token in seq]
                for seq in encodings
            ]
            result["attention_mask"] = torch.tensor(attention_masks, dtype=torch.long)
    
        if return_tensors == "pt":
            return result
        return {k: v.tolist() for k, v in result.items()}



class DNADataset(Dataset):
    def __init__(self, df, tokenizer, label2id, pad= False, max_len=256):
        self.sequences = df['sequence'].tolist()
        self.labels = df['family'].map(label2id).tolist()
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.pad = pad

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        seq = self.sequences[idx]
        label = self.labels[idx]
        ids = self.tokenizer.encode(seq, pad=self.pad, max_len=self.max_len)
        return ids, label
        

class DNALightningDataModule(pl.LightningDataModule):
    def __init__(self, marker, fold, label2id, batch_size=32, num_workers=3, max_len=256):
        super().__init__()
        self.marker = marker
        self.fold = fold
        # Use same tokenizer spec as training
        special_tokens = (['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
                  + ["+", '-', '*', '/', '=', "&", "|", "!"]
                  + ['M', 'B'] + ['P']
                  + ['R', 'I', 'K', 'L', 'O', 'Q', 'S', 'U', 'V']
                  + ['W', 'Y', 'X', 'Z'])
        self.tokenizer = KmerTokenizer(k=6, reserved_tokens=special_tokens, dynamic_kmer=True)
        self.label2id = label2id
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.max_len = max_len

        self.train_csv = f"data/{marker}/folds/fold_{fold}/train_low_augment.csv"
        self.val_csv = f"data/{marker}/folds/fold_{fold}/val.csv"
        self.test_csv = f"data/{marker}/folds/fold_{fold}/test.csv"

    def setup(self, stage=None):
        self.df_train = pd.read_csv(self.train_csv)
        self.df_val = pd.read_csv(self.val_csv)
        self.df_test = pd.read_csv(self.test_csv)

        self.train_dataset = DNADataset(self.df_train, self.tokenizer, self.label2id, pad=True, max_len=self.max_len)
        self.val_dataset = DNADataset(self.df_val, self.tokenizer, self.label2id, pad=True, max_len=self.max_len)
        self.test_dataset = DNADataset(self.df_test, self.tokenizer, self.label2id, pad=True, max_len=self.max_len)

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=True, num_workers=self.num_workers)

    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=self.batch_size, shuffle=False, num_workers=self.num_workers)

    def test_dataloader(self):
        return DataLoader(self.test_dataset, batch_size=1, shuffle=False, num_workers=self.num_workers)