# Standard imports

import torch
import sys
import os

# Import local modules

from dna_gpt.tokenizer import KmerTokenizer
from dna_gpt.model import DNAGPT

# Instantiate model with config

# Use same tokenizer spec as training
special_tokens = (['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
                  + ["+", '-', '*', '/', '=', "&", "|", "!"]
                  + ['M', 'B'] + ['P']
                  + ['R', 'I', 'K', 'L', 'O', 'Q', 'S', 'U', 'V']
                  + ['W', 'Y', 'X', 'Z'])
tokenizer = KmerTokenizer(k=6, reserved_tokens=special_tokens, dynamic_kmer=True)

model = DNAGPT.from_name('dna_gpt0.1b_m', vocab_size=len(tokenizer))


# Load weights

checkpoint_path = r"checkpoints/dna_gpt0.1b_m.pth"
state_dict = torch.load(checkpoint_path, map_location='cpu')
model.load_state_dict(state_dict)
model.eval()
print(f"Checkpoint loaded from {checkpoint_path}")


# Example encode/decode test

example_sequence = "CCCCAACCCCTTTTCCCCACCTTTCTTCTCTCGACTAGTCTTCATTTCTATTTCCTAACCTCTTCTCCCGCTCACCTCACCTACCCCTTCCCATTTTCGTTTTCTTTCACAAGGGGAGACAAGTCGTAA"
encoded = tokenizer.encode(example_sequence, pad=False, max_len=32)
print(f"Encoded tokens: {encoded}")
decoded = tokenizer.decode(encoded)
print(f"Decoded sequence: {decoded}")



import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from tqdm import tqdm

train_csv = "data/fold_1/train_low_augment.csv"
val_csv = "data/fold_1/val.csv"
test_csv = "data/fold_1/test.csv"

df_train = pd.read_csv(train_csv)
df_val = pd.read_csv(val_csv)
df_test = pd.read_csv(test_csv)

all_families = sorted(df_train['family'].unique())
label2id = {label: i for i, label in enumerate(all_families)}
id2label = {i: label for label, i in label2id.items()}

# print(label2id)
num_classes = len(label2id)




class DNADataset(Dataset):
    def __init__(self, df, tokenizer, label2id, max_len=256):
        self.sequences = df['sequence'].tolist()
        self.labels = df['family'].map(label2id).tolist()
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        seq = self.sequences[idx]
        label = self.labels[idx]
        ids = self.tokenizer.encode(seq, pad=True, max_len=self.max_len)
        return ids, label
    

batch_size = 32
max_len = 16

train_ds = DNADataset(df_train, tokenizer, label2id, max_len=max_len)
val_ds = DNADataset(df_val, tokenizer, label2id, max_len=max_len)

train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)
optimizer = torch.optim.AdamW(model.parameters(), lr=5e-6)
criterion = torch.nn.CrossEntropyLoss()



from sklearn.metrics import f1_score


num_epochs = 15

losses = []
eval_losses = []
f1s = []

for epoch in range(num_epochs):
    model.train()
    total_loss = 0

    for batch in tqdm(train_loader, desc=f"Epoch {epoch+1}"):
        ids, labels = batch
        ids = ids.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        logits = model(ids)[:, -1, :]  # [B, vocab_size]
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    avg_loss = total_loss / len(train_loader)
    print(f"Epoch {epoch+1} avg loss: {avg_loss:.4f}")

    losses.append(avg_loss)

    # Validation
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for batch in val_loader:
            ids, labels = batch
            ids = ids.to(device)
            labels = labels.to(device)

            logits = model(ids)[:, -1, :]
            preds = logits.argmax(dim=-1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    
    eval_loss = criterion(logits, labels).item()
    eval_losses.append(eval_loss)

    # Compute f1
    f1 = f1_score(labels.cpu(), preds.cpu(), average='weighted')
    print(f"Validation loss: {eval_loss:.4f}, F1 score: {f1:.4f}")
    f1s.append(f1)



    print(total)