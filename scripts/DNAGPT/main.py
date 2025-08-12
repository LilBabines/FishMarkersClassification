import hydra
from omegaconf import DictConfig
import os
import sys 
import pandas as pd

from dna_gpt.tokenizer import KmerTokenizer
from dna_gpt.model import DNAGPT
import json

from transformers import TrainingArguments, AutoModel, EarlyStoppingCallback, BertConfig
from transformers import Trainer, DataCollatorWithPadding
import torch
from torch.utils.data import Dataset, DataLoader

import numpy as np
import time


#set seeds

def set_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    os.environ['PYTHONHASHSEED'] = str(seed)





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
        encoded = self.tokenizer(
            seq,
            padding='max_length',
            truncation=True,
            max_length=self.max_len,
            return_tensors='pt'
        )
        
        item = {key: val.squeeze(0) for key, val in encoded.items()}  # remove batch dim
        item['labels'] = torch.tensor(label)
        return item
    

from torchmetrics.classification import MulticlassF1Score, MulticlassAccuracy
available_metrics = {
        'MulticlassF1Score': MulticlassF1Score,
        'MulticlassAccuracy': MulticlassAccuracy
    }

def define_metrics(num_classes,dict):
    metrics_family = {}
    metrics_order = {}

    if isinstance(num_classes, int):


        for metric_name, metric in dict.items():
        
            metric_class = available_metrics[metric.callable](num_classes=num_classes, **metric.kwargs)
        
            metrics_family[metric_name+'_family'] = metric_class
    else:
        for metric_name, metric in dict.items():
            
            metric_class = available_metrics[metric.callable](num_classes=num_classes[0], **metric.kwargs)
            metrics_order[metric_name+'_order'] = metric_class
            
            metric_class = available_metrics[metric.callable](num_classes=num_classes[1], **metric.kwargs)
            metrics_family[metric_name+'_family'] = metric_class
    return metrics_family




def define_trainer(model, train_dataset, val_dataset,num_classes,metrics, training_args, callbacks=[]):

    metrics_dict_family = define_metrics(num_classes,metrics)

    
    def to_tensor(data):
        if isinstance(data, np.ndarray):
            return torch.from_numpy(data)
        elif isinstance(data, torch.Tensor):
            return data
        elif isinstance(data, tuple):
            return tuple(to_tensor(d) for d in data)
        raise TypeError("Unsupported data type: {}".format(type(data)))
        
    def compute_metrics(eval_pred):

        predictions, labels = eval_pred.predictions, eval_pred.label_ids
        output = {}

        predictions = to_tensor(predictions)
        labels = to_tensor(labels)

        if labels.ndim == 2:
            labels_order, labels_family= labels[:, 0], labels[:, 1]
            predictions_order , predictions_family = predictions
            for key, func in metrics_dict_family.items():
                output[key] = func(preds =predictions_family, target =labels_family)

        else :
            if isinstance(predictions, tuple):
                predictions = predictions[0]
            
            for key, func in metrics_dict_family.items():
                output[key] = func(preds =predictions, target =labels)
        
        
        
        return output

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        callbacks=callbacks
    )

    return trainer, list(metrics_dict_family.keys())





@hydra.main(version_base="1.3",config_path="config", config_name="config")
def main(cfg: DictConfig):
    
    

    set_seed(42)    

    log_dir = hydra.core.hydra_config.HydraConfig.get().runtime.output_dir

    print("log_dir: ", log_dir)
    # Use same tokenizer spec as training
    special_tokens = (['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
                    + ["+", '-', '*', '/', '=', "&", "|", "!"]
                    + ['M', 'B'] + ['P']
                    + ['R', 'I', 'K', 'L', 'O', 'Q', 'S', 'U', 'V']
                    + ['W', 'Y', 'X', 'Z'])
    tokenizer = KmerTokenizer(k=6, reserved_tokens=special_tokens, dynamic_kmer=True)

    for fold in os.listdir(cfg.data.dataset_path):


        start_time = time.time()
        print('-----------------')
        print(f"Fold: {fold}")
        # if os.path.exists(os.path.join(log_dir,'checkpoints',fold)):
        #     print("Fold already trained")
        #     continue
        print('-----------------')
        print("Model Initialization")
        
        model = model = DNAGPT.from_name('dna_gpt0.1b_m', vocab_size=len(tokenizer))
        
        

        args = TrainingArguments(os.path.join(log_dir,'checkpoints',fold),
                                 **cfg.trainer.kwargs,
                                 save_safetensors=False, 
                                 logging_dir = os.path.join(log_dir,'logs',fold))
        


        train_csv = f"data/{fold}/train_low_augment.csv"
        val_csv = f"data/{fold}/val.csv"
        test_csv = f"data/{fold}/test.csv"

        df_train = pd.read_csv(train_csv)
        df_val = pd.read_csv(val_csv)
        df_test = pd.read_csv(test_csv)

        all_families = sorted(df_train['family'].unique())
        label2id = {label: i for i, label in enumerate(all_families)}
        id2label = {i: label for label, i in label2id.items()}

        # print(label2id)
        num_classes = len(label2id)

        max_len = 32
        batch_size = 32

        train_dataset = DNADataset(df_train, tokenizer, label2id, max_len=max_len)
        val_dataset = DNADataset(df_val, tokenizer, label2id, max_len=max_len)
        test_dataset = DNADataset(df_test, tokenizer, label2id, max_len=max_len)

        

        trainer, metrics_family = define_trainer(model, train_dataset, val_dataset, num_classes,cfg.metrics,args,callbacks=[EarlyStoppingCallback(early_stopping_patience=cfg.trainer.early_stopping_patience)]) #

        loader = DataLoader(train_dataset, batch_size=4)
        batch = next(iter(loader))
        print(batch)

        print("ahaha")
                        
        trainer.train()
           
        print("Testing")
            
        result = trainer.predict(test_dataset)
        print("Metrics on test set: ", result.metrics)



        import pickle


        
    

        json.dump(id2label, open(os.path.join(log_dir,'checkpoints',fold,"id2label.json"), 'w'))
        json.dump(label2id, open(os.path.join(log_dir,'checkpoints',fold,"label2id.json"), 'w'))

        
        dataframe = pd.DataFrame( columns = ["preds_family", "labels_family"]) 
    
        dataframe["preds_family"] = result.predictions[0].argmax(axis=1).squeeze()
        
        
        dataframe["labels_family"] = result.label_ids



        
        pickle.dump({'preds':result.predictions,'labels':result.label_ids}, open(os.path.join(log_dir,'checkpoints',fold,"predictions.pkl"), 'wb'))
        dataframe.to_csv(os.path.join(log_dir,'checkpoints',fold,"predictions.csv"), index=False)

        print("Time taken: ", time.time() - start_time)


if __name__ == "__main__":
    
    main()

    