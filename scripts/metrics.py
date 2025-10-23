import ast
import os
import pandas as pd
from sklearn.metrics import f1_score as f1 
from sklearn.metrics import precision_recall_fscore_support as prf
import numpy as np
import pickle as pkl
import json
from scipy.special import softmax

def get_family(x,database):

    sub = database[database['genus']== x]
    
    family = sub['family'].unique()
    
    if len(family) > 1:
        return 'NC'
    return family[0]

def valid_rank(x):
    if x in ['family','subfamily', 'genus','subgenus','subspecies', 'species']:
        return True
    return False

totaux = {}
for marker in ["ac16", "berry","mifish","teleo"] : #,
    print("==================")
    print(marker)
    for fold in range(1,7):
        print('----------------------')
        print(f"Fold {fold}")
        predictions = pd.DataFrame(columns=["order","family","obi4","MMseqs2","BERTax","DNAGPT","DNABert2_random_weights","DNABert2","DNABert2_mlm","Ensemble_obi4","Ensemble_mmseqs2","top15_DNABert2","sequence"])

        # DNABert2 : 
        dnabert2_preds = pd.read_csv(f"DNABert2/experiments/fine_tune_taxa/outputs/{marker}_from_pt_dnabert2/checkpoints/fold_{fold}/predictions.csv")
        test_df = pd.read_csv(f"DNABert2/experiments/fine_tune_taxa/data/{marker}/folds/fold_{fold}/test.csv")

        predictions["sequence"] = test_df["sequence"]
        predictions["family"] = test_df["family"]
        predictions["order"] = test_df["order"]

        assert dnabert2_preds['labels_family_name'].equals(test_df['family'])

        predictions["DNABert2"] = dnabert2_preds["preds_family_name"]

        # DNABert2 : 
        dnabert2_preds = pd.read_csv(f"DNABert2/experiments/fine_tune_taxa/outputs/{marker}_from_mlm/checkpoints/fold_{fold}/predictions.csv")
        assert dnabert2_preds['labels_family_name'].equals(test_df['family'])
        predictions["DNABert2_mlm"] = dnabert2_preds["preds_family_name"]

        dnabert2_preds = pd.read_csv(f"DNABert2/experiments/fine_tune_taxa/outputs/{marker}_from_random_weights/checkpoints/fold_{fold}/predictions.csv")
        assert dnabert2_preds['labels_family_name'].equals(test_df['family'])
        predictions["DNABert2_random_weights"] = dnabert2_preds["preds_family_name"]

        #obi4 
        preds = pd.read_csv(f'Obitools/results/obi4/{marker}/fold_{fold}/output.csv', sep=",")
        # assert preds["sequence"].str.upper().equals(predictions["sequence"].str.upper())

        db = pd.read_csv(f'Obitools/data/{marker}/folds/fold_{fold}/train.csv')


        preds['best_match']= preds['obitag_bestmatch'].apply(lambda x: '.'.join(x.split('.')[0:-1])) # remove the prefix
        preds['preds_family'] = preds['best_match'].apply(lambda x: get_family(x, db))

        preds['obi_tag']= preds['taxid'].apply(lambda x: x.split('[')[1].split(']')[0]) # remove the prefix
        preds['valid_rank_preds'] = preds['obitag_rank'].apply(lambda x: valid_rank(x)) # remove the prefix

        predictions['obi4'] = preds.apply(lambda row: row['preds_family'] if row['valid_rank_preds'] else 'NC', axis=1)

        # MMseqs2
        preds_df = pd.read_csv(f'MMseqs2/result/{marker}/folds/fold_{fold}/tax_out/tax_out_lca.tsv', sep="\t", header=None,names=["id_seq","taxid","rank","pred"])
        preds_df["num"]= preds_df["id_seq"].str.extract(r'^(\d+)').astype(int)
        preds_df = preds_df.sort_values(by='num')
        preds_df = preds_df.reset_index(drop=True)


        predictions['MMseqs2'] = preds_df['pred'].apply(lambda x: "NC" if x =="unclassified" else x) # take the family from the taxid
    
        # BERTax
        preds_pkl = f'BERTax/outputs/{marker}/fold_{fold}/test_multi_predictions.pkl'
        preds_pkl = pd.read_pickle(preds_pkl)


        X_ground_truth, X_preds = preds_pkl['data'][0][1], preds_pkl['data'][1][1]
        labels= np.argmax(X_ground_truth, axis=1)
        preds = np.argmax(X_preds, axis=1)

        family_to_idx =  json.load(open(f'BERTax/data/{marker}/family_to_index.json'))

        idx_to_family = {v: k for k, v in family_to_idx.items()}

        assert predictions['family'].equals(pd.Series([idx_to_family[x] for x in labels]))

        predictions["BERTax"] = pd.Series([idx_to_family[x] for x in preds])

        # DNABert2 + obi 

        preds_bert = pd.read_csv(f'DNABert2/experiments/fine_tune_taxa/outputs/{marker}_from_mlm/checkpoints/fold_{fold}/predictions.csv')
        logits = pkl.load(open(f'DNABert2/experiments/fine_tune_taxa/outputs/{marker}_from_mlm/checkpoints/fold_{fold}/predictions.pkl', 'rb'))  
        idx_to_label = (
                preds_bert[["labels_family", "labels_family_name"]]
                .drop_duplicates()
                .sort_values("labels_family")
                .set_index("labels_family")["labels_family_name"]
                .to_dict()
            )
        
        logits_preds_family = logits['preds'][1] # size : (n_samples, n_classes)
        probas = softmax(logits_preds_family, axis=1)

        top15 = np.argsort(probas, axis=1)[:,-15:]
        top15_families = np.array([np.array([idx_to_label[int(i)] for i in row]) for row in top15])

        assert predictions['DNABert2_mlm'].equals(pd.Series(top15_families[:,-1])) # take the first family as prediction
       
        predictions['top15_DNABert2'] = top15_families.tolist()



        predictions["Ensemble_obi4"] = predictions.apply(lambda row: row['obi4'] if row['obi4'] in row['top15_DNABert2'] else row['DNABert2_mlm'], axis=1)
        predictions["Ensemble_mmseqs2"] = predictions.apply(lambda row: row['MMseqs2'] if row['MMseqs2'] in row['top15_DNABert2'] else row['DNABert2_mlm'], axis=1)


        totaux[(marker, fold)] = predictions.copy()
        os.makedirs(f"../results/{marker}/fold_{fold}", exist_ok=True)
        predictions.to_csv(f"../results/{marker}/fold_{fold}/predictions.csv", index=False)

dataframe_totaux = pd.concat(totaux, names=["marker", "fold"])


dataframe_totaux.to_csv("../results/all_predictions.csv")

for method in ["obi4","MMseqs2","BERTax","DNAGPT","DNABert2_random_weights","DNABert2","DNABert2_mlm","Ensemble_obi4","Ensemble_mmseqs2"]: 
    print("==================")
    print(f"Method: {method}")
    for marker in ["teleo","mifish", "berry","ac16"] :
        print("-----------------")
        print(f"Marker: {marker}")
        f1_scores = []
        precision_scores = []
        recall_scores = []
        for fold in range(1,7):
            predictions = dataframe_totaux.loc[(marker, fold)]
            y_true = predictions['family']
            y_pred = predictions[method]


            p,r,f,s = prf(y_true, y_pred, average='macro', labels=y_true.unique(),zero_division=0)

            f1_scores.append(f)
            precision_scores.append(p)
            recall_scores.append(r)


        print(f"Precision: {np.round(np.mean(precision_scores),3)}")
        print(f"Recall: {np.round(np.mean(recall_scores),3)}")
        print(f"F1 Score: {np.round(np.mean(f1_scores),3)}")