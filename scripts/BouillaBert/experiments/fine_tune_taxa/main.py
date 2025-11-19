import hydra
from omegaconf import DictConfig
import os
import sys 
import pandas as pd

sys.path.append(os.path.join(os.getcwd(), 'src'))
from models.tokenizer import load_tokenizer
from data.dataset import load_data, encode_multiTaxa_dataset, encode_singleTaxa_dataset
from models.model import MultiTaxaClassification, load_bert_model, get_best
from utils.trainer import define_trainer
from utils.visualize import plot_save_loss
from models.dnabert2  import bert_layers
import json

from transformers import TrainingArguments, AutoModel, EarlyStoppingCallback, BertConfig
import torch

import time


#set seeds

def set_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    os.environ['PYTHONHASHSEED'] = str(seed)
set_seed(42)


@hydra.main(version_base="1.3",config_path="config", config_name="config")
def main(cfg: DictConfig):
    
    

    log_dir = hydra.core.hydra_config.HydraConfig.get().runtime.output_dir
    print("log_dir: ", log_dir)
    tokenizer = load_tokenizer(cfg.model.tokenizer_name)

    for fold in os.listdir(cfg.data.dataset_path):
        start_time = time.time()
        print('-----------------')
        print(f"Fold: {fold}")
        if os.path.exists(os.path.join(log_dir,'checkpoints',fold)):
            print("Fold already trained")
            continue
        print('-----------------')
        print("Model Initialization")
        if cfg.task.task == "multiTaxa":
            
            train_dataset, val_dataset, test_dataset, id2label_order, label2id_order, id2label_family, label2id_family = encode_multiTaxa_dataset(tokenizer, os.path.join(cfg.data.dataset_path,fold), train_name = cfg.data.train_name )
            num_classes = (len(id2label_order) , len(id2label_family))

            model = MultiTaxaClassification( len(id2label_order), len(id2label_family),vocab_size = tokenizer.vocab_size,model_name=cfg.model.model_name, use_pretrained = cfg.model.use_pretrained ,**cfg.model.bert_kwargs)  

        elif cfg.task.task == "singleTaxa":

            train_dataset, val_dataset, test_dataset, id2label, label2id = encode_singleTaxa_dataset(tokenizer,os.path.join(cfg.data.dataset_path,fold))
            num_classes = len(id2label)
            model = load_bert_model(cfg.model.model_name, tokenizer.vocab_size, local=cfg.model.local, id2label=id2label, label2id=label2id)
        else:
            raise ValueError("cfg.task.task has to be either 'multiTaxa' or 'singleTaxa'")
        
        if cfg.model.local :

            if cfg.task.train :
                #from MLM Task
                print("Loading MLM model")
                best_model = get_best(os.path.join(cfg.model.local_path))
                print("best_model: ", best_model)
                

                masked_lm_model = bert_layers.BertForMaskedLM.from_pretrained(best_model)
                
                
                model.bert.load_state_dict(masked_lm_model.bert.state_dict(),strict=False)
            else :
                print("Loading Fine-tuned model")

                config = BertConfig.from_pretrained(get_best(cfg.task.checkpoint_path+"/"+fold))
                model.load_state_dict(torch.load(get_best(cfg.task.checkpoint_path+"/"+fold)+"/pytorch_model.bin"))
                # model = MultiTaxaClassification.from_pretrained(get_best(cfg.task.checkpoint_path+"/"+fold))

        

        args = TrainingArguments(os.path.join(log_dir,'checkpoints',fold),
                                 **cfg.trainer.kwargs,
                                 save_safetensors=False, 
                                 logging_dir = os.path.join(log_dir,'logs',fold))
        
        trainer, metrics_order, metrics_family = define_trainer(model, tokenizer, train_dataset, val_dataset, num_classes,cfg.metrics,args,callbacks=[EarlyStoppingCallback(early_stopping_patience=cfg.trainer.early_stopping_patience)]) #

        
        if cfg.task.train :
            print("Training")
            try:

                trainer.train()
            except KeyboardInterrupt:
                print("Training interrupted, current status will be saved")
                trainer.save_model()
        
        print("Testing")
            
        result = trainer.predict(test_dataset)
        print("Metrics on test set: ", result.metrics)

        if cfg.task.save_preds :

            import pickle

            if cfg.task.task == "multiTaxa":

                json.dump(id2label_family, open(os.path.join(log_dir,'checkpoints',fold,"id2label_family.json"), 'w'))
                json.dump(label2id_family, open(os.path.join(log_dir,'checkpoints',fold,"label2id_family.json"), 'w'))

                dataframe = pd.DataFrame( columns = ["preds_order","preds_family", "labels_order", "labels_family"]) 
                dataframe["preds_order"] = result.predictions[0].argmax(axis=1).squeeze()
                dataframe["preds_family"] = result.predictions[1].argmax(axis=1).squeeze()
                
                dataframe["labels_order"] = result.label_ids[:,0]
                dataframe["labels_family"] = result.label_ids[:,1]

                dataframe["labels_order_name"] = dataframe["labels_order"].map(id2label_order)
                dataframe["labels_family_name"] = dataframe["labels_family"].map(id2label_family)
                dataframe["preds_order_name"] = dataframe["preds_order"].map(id2label_order)
                dataframe["preds_family_name"] = dataframe["preds_family"].map(id2label_family)

                
                pickle.dump({'preds':result.predictions,'labels':result.label_ids}, open(os.path.join(log_dir,'checkpoints',fold,"predictions.pkl"), 'wb'))
                dataframe.to_csv(os.path.join(log_dir,'checkpoints',fold,"predictions.csv"), index=False)

            else : 

                json.dump(id2label, open(os.path.join(log_dir,'checkpoints',fold,"id2label.json"), 'w'))
                json.dump(label2id, open(os.path.join(log_dir,'checkpoints',fold,"label2id.json"), 'w'))

                
                dataframe = pd.DataFrame( columns = ["preds_family", "labels_family"]) 
            
                dataframe["preds_family"] = result.predictions[0].argmax(axis=1).squeeze()
                
                
                dataframe["labels_family"] = result.label_ids


                import pickle

                
                pickle.dump({'preds':result.predictions,'labels':result.label_ids}, open(os.path.join(log_dir,'checkpoints',fold,"predictions.pkl"), 'wb'))
                dataframe.to_csv(os.path.join(log_dir,'checkpoints',fold,"predictions.csv"), index=False)

        print("Time taken: ", time.time() - start_time)


if __name__ == "__main__":
    
    main()

    