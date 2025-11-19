from torch import nn
import torch

import os
from transformers.modeling_outputs import SequenceClassifierOutput
from transformers import AutoModel, AutoModel, BertConfig, BertForMaskedLM

from transformers import AutoModelForSequenceClassification
from datasets import load_dataset

class MultiTaxaClassification(nn.Module):
    def __init__(self, num_labels_order = 72, num_labels_family = 303, vocab_size = None, model_name = "zhihan1996/DNABERT-2-117M",use_pretrained=False,**bert_kwargs ):
        super(MultiTaxaClassification,self).__init__()
        
        self.num_labels = (num_labels_order, num_labels_family)
        self.problem_type = "multi_label_classification"
        config = BertConfig.from_pretrained(model_name,vocab_size= vocab_size,**bert_kwargs )
        if use_pretrained:

            self.bert = AutoModel.from_pretrained(model_name, trust_remote_code=True,config=config, ignore_mismatched_sizes=True)
        else :
            self.bert = AutoModel.from_config(config, trust_remote_code=True)

        self.bert.resize_token_embeddings(vocab_size)
        
        hidden_size = self.bert.config.hidden_size
        classifier_dropout = 0.1

        self.dropout = nn.Dropout(classifier_dropout)
        

        self.classifier_order = nn.Linear(hidden_size, self.num_labels[0])
        self.classifier_family = nn.Linear(hidden_size + self.num_labels[0] , self.num_labels[1]) # Concatenate the order logits to the family logits
        # self.classifier_family = nn.Linear(hidden_size, self.num_labels[1]) 

    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        token_type_ids=None,
        position_ids=None,
        head_mask=None,
        inputs_embeds=None,
        labels=None,
        output_attentions=True,
        output_hidden_states=True,
        return_dict=True,
    ):
        
        

        outputs = self.bert(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            )
        
        
        # Use the [CLS] token's output (first token of the sequence)
        pooled_output = outputs[0][:, 0, :]  # Shape: [batch_size, hidden_size]

        pooled_output = self.dropout(pooled_output)
        
        logits_order = self.classifier_order(pooled_output)
        logits_family = self.classifier_family(torch.cat((pooled_output, logits_order), dim=1))
        logits = (logits_order, logits_family)
        
        
        loss = None
        
        if labels is not None:
            labels_order, labels_family = labels[:,0], labels[:,1]

            loss_fct = nn.CrossEntropyLoss()
            loss_order = loss_fct(logits_order, labels_order)
            loss_family = loss_fct(logits_family, labels_family)
            loss = loss_order + loss_family
     
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        
        # return {"loss":loss, "logits":logits}
        return SequenceClassifierOutput(
            loss=loss,
            logits=logits,
            # hidden_states=outputs.hidden_states,
            # attentions=outputs.attentions,
        )




def load_bert_model(name, vocab_size, local=False, id2label=None, label2id=None):

    # model_path_save=r"C:\Users\Auguste Verdier\Desktop\ADNe\BouillaClip\Model\genera_300_medium_3_mer\checkpoint-85335"
    if local:
        assert os.path.exists(name), "The model path does not exist at the specified location, but local flag is set to True"
        assert os.path.exists(os.path.join(name,"config.json")), "The model path does not contain a config.json file"
        config_path = os.path.join(name,"config.json")
    else :
        config_path = name
        
    config = BertConfig.from_pretrained(config_path, 
                                        num_labels=len(id2label), 
                                        max_position_embeddings=514,
                                        id2label=id2label,
                                        label2id=label2id)

    


   
    model = AutoModelForSequenceClassification.from_pretrained(name, trust_remote_code=True, ignore_mismatched_sizes=True, config=config)

    model.id2label = id2label
    model.label2id = label2id
    model.resize_token_embeddings(vocab_size)
    return model

def get_best(checkpoints_dir):
    checkpoints = os.listdir(checkpoints_dir)
    checkpoints = [i for i in checkpoints if "checkpoint" in i]
    checkpoints = [int(i.split("-")[1]) for i in checkpoints]
    checkpoints.sort()
    return os.path.join(checkpoints_dir,f"checkpoint-{checkpoints[0]}")


if __name__=='__main__':


    pass
    
    

