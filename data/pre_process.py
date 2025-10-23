# After CRABS extraction on mitofish and NCBI, error treshold is set to 3

import pandas as pd
import numpy as np
import sklearn
from sklearn.model_selection import train_test_split, KFold
import math
import json
import os
import random
from tqdm import tqdm
from ete3 import NCBITaxa

seed = 111
np.random.seed(seed)
random.seed(seed)
sklearn.utils.check_random_state(seed)

dic_family_to_order = {"Scatophagidae": 'Perciformes',
                        'Sillaginidae' : 'Perciformes',
                        'Plesiopidae'  : 'Perciformes',
                        'Pomacanthidae' : 'Perciformes',
                        "Sciaenidae": "Acanthuriformes",
                        "Ambassidae"  : "Perciformes",
                        "Pseudochromidae"  : "Perciformes",
                        "Polycentridae" : "Perciformes",
                        "Opistognathidae"  : "Perciformes",
                        "Toxotidae" : "Perciformes",
                        'Pristiophoridae' : 'Pristiophoriformes',
                        'Platyrhinidae' : 'Torpediniformes',
                        'Emmelichthyidae' : 'Acanthuriformes',
                        'Pomacentridae':  "Perciformes",
                        'Embiotocidae' :'Perciformes',
                        'Siganidae': 'Perciformes',
                        'Squatinidae' : 'Squatiniformes',
                        "Centropomidae" : "Perciformes" ,
                        "Malacanthidae" : "Perciformes" ,
                        'Polynemidae' :  'Perciformes' , 
                        'Moronidae' :  'Perciformes' ,
                        'Menidae' :  'Perciformes' ,
                        "Lactariidae" : "Perciformes",
                        "Sphyraenidae" : "Perciformes",
                        'Callanthiidae' : 'Perciformes',
                        "Monodactylidae" : "Perciformes",
                      }

dic_order_to_class = {'Coelacanthiformes': "Sarcopterygii",
                    'Ceratodontiformes' : 'Sarcopterygii'}

dic_genus_to_family = {'Percalates': 'Percichthyidae',
                    'Paedocypris': 'Cyprinidae',
                    'Bembrops' : 'Percophidae',
                    'Conorhynchos' : 'Pimelodidae',
                    'Lepidogalaxias' :'Lepidogalaxiidae',
                    }

def fill_correction(df):
        df = df.copy()
        for key,item in dic_family_to_order.items():
            idx = df[df['family']==key]
            df.loc[idx.index, 'order'] = item
        for key,item in dic_order_to_class.items():
            idx = df[df['order']==key]
            df.loc[idx.index, 'class'] = item
        for key,item in dic_genus_to_family.items():
            idx = df[df['genus']==key]
            df.loc[idx.index, 'family'] = item

        df =df.dropna()
        
        return df

def rename_columns(df):
    df.rename(columns={0:'ID', 1:'taxid_ncbi', 2:'kingdom', 3:'phylum', 4:'class', 5:'order', 6:'family', 7:'genus', 8:'species', 9:'sequence'}, inplace=True)
    return df

def remove_not_desired(df_nan):
    
    df_nan = df_nan.dropna(subset=['class', 'kingdom'])
    
    df_nan = df_nan[~df_nan['order'].isin(['Testudines', 'Crocodylia', 'Diplura'])]

    df_nan = df_nan[df_nan['ID_ncbi'] != "KM078797.1.1318.2292"]

    df_nan.loc[df_nan['ID_ncbi'].isin(['AB626856.1.70.1026','AB626856']), ['kingdom', 'phylum', 'class', 'order', 'family', 'genus','species']] = ['Eukaryota', 'Chordata', 'Actinopteri', 'Cypriniformes', 'Leuciscidae', 'Pseudaspius','Pseudaspius_sachalinensis']

    df_nan.loc[df_nan['ID_ncbi'].isin(['AP011270.1.70.1026','AP011270']), ['kingdom', 'phylum', 'class', 'order', 'family', 'genus','species']] = ['Eukaryota', 'Chordata', 'Actinopteri', 'Cypriniformes', 'Leuciscidae', 'Pseudaspius','Pseudaspius_sachalinensis']

    return df_nan

def clean_taxo_consistency(df, verif= False):

    df = df.copy()
    df['kingdom'] = 'Metazoa'

    # df['taxid_ncbi'] = df['ID'].combine_first(df['ncbi_taxid'])

    df.loc[(df['species'] == 'Stephanolepis_hispidus'), 'species'] = 'Stephanolepis_hispida'
    df.loc[(df['species'] == 'Stephanolepis_hispida'), 'taxid_ncbi'] = 2996723.0

    df.loc[(df['genus'] == 'Cobitis'), 'family'] = 'Cobitidae'
    df.loc[(df['genus'] == 'Neolissochilus'), 'family'] = 'Cyprinidae'
    df.loc[(df['genus'] == 'Triplophysa'), 'family'] = 'Nemacheilidae'
    df.loc[(df['genus'] == 'Taeniura'), 'family'] = 'Potamotrygonidae'
    df.loc[(df['genus'] == 'Rhinogobius'), 'family'] = 'Gobiidae'
    df.loc[(df['genus'] == 'Glyphis'), 'family'] = 'Carcharhinidae'
    df.loc[(df['genus'] == 'Psalidodon'), 'family'] = 'Characidae'
    df.loc[(df['genus'] == 'Kyphosus'), 'family'] = 'Kyphosidae'
    df.loc[(df['genus'] == 'Rhinogobius'), 'family'] = 'Gobiidae'
    df.loc[(df['genus'] == 'Carcharhinus'), 'family'] = 'Carcharhinidae'
    df.loc[(df['genus'] == 'Carcharodon'), 'family'] = 'Alopiidae'
    df.loc[(df['genus'] == 'Creteuchiloglanis'), 'family'] = 'Sisoridae'
    df.loc[(df['genus'] == 'Rhodeus'), 'family'] = 'Acheilognathidae'
    df.loc[(df['genus'] == 'Culter'), 'family'] = 'Xenocyprididae'
    df.loc[(df['genus'] == 'Coris'), 'family'] = 'Labridae'
    df.loc[(df['genus'] == 'Lepidomeda'), 'family'] = 'Leuciscidae'
    df.loc[(df['genus'] == 'Joturus'), 'family'] = 'Mugilidae'
    df.loc[(df['genus'] == 'Achoerodus'), 'family'] = 'Labridae'
    df.loc[(df['genus'] == 'Cyathochromis'), 'family'] = 'Cichlidae'
    df.loc[(df['genus'] == 'Gastropsetta'), 'family'] = 'Paralichthyidae'
    df.loc[(df['genus'] == 'Ascelichthys'), 'family'] = 'Cottidae'
    df.loc[(df['genus'] == 'Erotelis'), 'family'] = 'Eleotridae'
    df.loc[(df['genus'] == 'Muraenolepis'), 'family'] = 'Muraenolepididae'

    df.loc[(df['genus'] == 'Tachysurus'), 'order'] = 'Cypriniformes'
    df.loc[(df['genus'] == 'Algansea'), 'order'] = 'Cypriniformes'
    df.loc[(df['genus'] == 'Rhinogobius'), 'order'] = 'Gobiiformes'
    df.loc[(df['genus'] == 'Phoxinus'), 'order'] = 'Cypriniformes'
    df.loc[(df['genus'] == 'Sarcocheilichthys'), 'order'] = 'Cypriniformes'
    df.loc[(df['genus'] == 'Capoeta'), 'order'] = 'Cypriniformes'
    df.loc[(df['genus'] == 'Eleotris'), 'order'] = 'Gobiiformes'
    df.loc[(df['genus'] == 'Pseudorasbora'), 'order'] = 'Cypriniformes'
    df.loc[(df['genus'] == 'Carassius'), 'order'] = 'Cypriniformes'
    df.loc[(df['genus'] == 'Scaphirhynchus'), 'order'] = 'Acipenseriformes'
    df.loc[(df['genus'] == 'Rhynchocypris'), 'order'] = 'Cypriniformes'
    df.loc[(df['genus'] == 'Rudarius'), 'order'] = 'Tetraodontiformes'
    df.loc[(df['genus'] == 'Neobythites'), 'order'] = 'Ophidiiformes'
    df.loc[(df['genus'] == 'Cynoglossus'), 'order'] = 'Pleuronectiformes'
    df.loc[(df['genus'] == 'Sirembo'), 'order'] = 'Ophidiiformes'


    df.loc[(df['family'] == 'Cyprinidae'), 'class'] = 'Actinopteri'
    df.loc[(df['family'] == 'Percichthyidae'), 'class'] = 'Actinopteri'
    df.loc[(df['family'] == 'Lepidogalaxiidae'), 'class'] = 'Actinopteri'


    df.loc[(df['genus'] == 'Glyphis'), 'class'] = 'Chondrichthyes'
    df.loc[(df['genus'] == 'Carcharhinus'), 'class'] = 'Chondrichthyes'
    df.loc[(df['genus'] == 'Carcharodon'), 'class'] = 'Chondrichthyes'


    df.loc[(df['genus'] == 'Bembrops'), 'family'] = 'Bembropidae'

    df.loc[(df['genus'] == 'Aphaniops'), 'genus'] = 'Aphanius'

    df.loc[(df['species'] == 'Aphaniops_dispar'), 'species'] = 'Aphanius_dispar'

    df.loc[(df['family'] == 'Percophidae'), 'order'] = 'Pempheriformes'
    df.loc[(df['family'] == 'Bagridae'), 'order'] = 'Siluriformes'
    df.loc[(df['family'] == 'Iguanodectidae'), 'order'] = 'Characiformes'
    df.loc[(df['family'] == 'Hemiscylliidae'), 'order'] = 'Orectolobiformes'
    df.loc[(df['family'] == 'Urotrygonidae'), 'order'] = 'Myliobatiformes'
    df.loc[(df['family'] == 'Proscylliidae'), 'order'] = 'Carcharhiniformes'
    df.loc[(df['family'] == 'Gurgesiellidae'), 'order'] = 'Rajiformes'
    df.loc[(df['family'] == 'Cynodontidae'), 'order'] = 'Characiformes'

    ranks = ['kingdom', 'phylum', 'class', 'order', 'family','genus', 'species'][::-1]


    for i,rank in enumerate(ranks[:-1]):
        up_rank = ranks[i+1]

        for rank_name in tqdm(df[rank].unique()):

            if df[df[rank] == rank_name][up_rank].nunique() >1:
                
                sub_data = df[df[rank] == rank_name]
                values_count = sub_data[up_rank].value_counts()
                # print(values_count)
                max_val_count = values_count.index[0]

                if values_count.iloc[0] > 1.5 * values_count.iloc[1]:
                    df.loc[df[rank] == rank_name, up_rank] = max_val_count
                else:
                    print(f'Inconstency in {rank} : {rank_name} : {values_count}')

    if verif:
        verif_taxo_consistency(df)

    return df

def verif_taxo_consistency(df):

    ranks = ['kingdom', 'phylum', 'class', 'order', 'family','genus', 'species']

    for i,rank in enumerate(ranks[1:]):

        for rank_name in tqdm(df[rank].unique()):

            sub_data = df[df[rank] == rank_name]
            super_rank = ranks[i]
            assert sub_data[super_rank].nunique() == 1, f"rank {super_rank} is not unique for {rank,rank_name}, {sub_data[super_rank].value_counts()} "


def clean_taxid_incompability(df):

        
    df.loc[(df['taxid_ncbi'] == 196032.0), ['genus','species']] = ['Aphanius','Aphanius_dispar']


    df.loc[(df['taxid_ncbi'] == 2968234.0), 'family'] = 'Rajidae'

    df.loc[(df['taxid_ncbi'] == 41697.0), 'species'] = 'Sardinops_melanostictus'
    df.loc[(df['taxid_ncbi'] == 118256.0), 'genus'] = 'Rhizoprionodon'


    df.loc[(df['taxid_ncbi'] == 586868.0), 'genus'] = 'Tetrosomus'

    df.loc[(df['taxid_ncbi'] == 2949627.0), 'genus'] = 'Aphaniops'
    df.loc[(df['taxid_ncbi'] == 2783872.0), 'genus'] = 'Aphaniops'

    df.loc[(df['taxid_ncbi'] == 643384.0), 'family'] = 'Gobionidae'
    df.loc[(df['taxid_ncbi'] == 643384.0), 'genus'] = 'Squalidus'

    df.loc[(df['taxid_ncbi'] == 643384.0), 'species'] = 'Squalidus_gracilis'


    df.loc[(df['taxid_ncbi'] == 80988.0), 'species'] = 'Stegastes_lacrymatus'

    df.loc[(df['taxid_ncbi'] == 1338610.0), 'species'] = 'Catostomus_discobolus'

    df.loc[(df['taxid_ncbi'] == 270609.0), 'family'] = 'Bembropidae'

    df.loc[(df['taxid_ncbi'].isin([270607.0,1633524.0,1672025.0,2507724.0])), 'order'] = 'Pempheriformes'

    df.loc[(df['taxid_ncbi'] == 1470305.0), 'family'] = 'Gobionidae'
    df.loc[(df['taxid_ncbi'] == 1470305.0), 'genus'] = 'Squalidus'
    df.loc[(df['taxid_ncbi'] == 1470305.0), 'species'] = 'Squalidus_gracilis'

    df.loc[(df['taxid_ncbi'] == 75369.0), 'genus'] = 'Spinibarbus'
    df.loc[(df['taxid_ncbi'] == 75369.0), 'species'] = 'Spinibarbus_denticulatus'

    df.loc[(df['taxid_ncbi'] == 206124.0), 'genus'] = 'Macroramphosus'
    df.loc[(df['taxid_ncbi'] == 206124.0), 'species'] = 'Macroramphosus_scolopax'

    df.loc[(df['taxid_ncbi'] == 997969.0), 'genus'] = 'Chromis'
    df.loc[(df['taxid_ncbi'] == 997969.0), 'species'] = 'Chromis_vanderbilti'


    df.loc[(df['taxid_ncbi'] == 1338610.0), 'species'] = 'Catostomus_discobolus'

    df.loc[(df['taxid_ncbi'] == 1003821.0), 'species'] = 'Osteomugil_robustus'


    df.loc[(df['taxid_ncbi'] == 2484686.0), 'genus'] = 'Hypanus'
    df.loc[(df['taxid_ncbi'] == 2484686.0), 'species'] = 'Hypanus_americanus'
    
    df = df[~df['species'].isin(['Helcogrammoides_chilensis', 'Helcogrammoides_cunninghami','Hypsoblennius_sordidus'])]


    return df

def validate_taxonomy(row):
    ncbi = NCBITaxa()
    taxid = row['taxid_ncbi']
    
    try:
        # Fetch the lineage for the taxid
        lineage = ncbi.get_lineage(taxid)
        
        # Get taxonomic names and ranks
        names = ncbi.get_taxid_translator(lineage)
        ranks = ncbi.get_rank(lineage)
        
        # Create a dictionary of expected ranks from the lineage
        correct_ranks = {ranks[taxid]: names[taxid] for taxid in lineage}
        
        # Compare the dataframe values with the NCBI values
        mismatches = {'taxid': taxid}
        
        # Check each level (kingdom, phylum, etc.)
        for rank in ['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species']:
            if rank in correct_ranks:
                correct_name = correct_ranks[rank]

                # filter special characters and species names
                if ' ' in correct_ranks[rank] :
                    correct_name = correct_ranks[rank].split(' ')[0]+'_'+correct_ranks[rank].split(' ')[1] 
                name = row[rank]
                if '.' in  row[rank]:
                    name = row[rank].split('.')[0]+'.'
                if '_x_' in row[rank]:

                    name = row[rank].split('_x_')[0]
                if '_complex_' in row[rank]:
                    name = row[rank].split('_complex_')[0]


                if name != correct_name:
                    mismatches[rank] = f"Expected: {correct_name}, Found: {name}"
            # else:
            #     mismatches[rank] = f"No {rank} found in NCBI taxonomy"

        return mismatches if mismatches else "All matches"
    
    except Exception as e:
        return f"Error for taxid {taxid}: {str(e)}"
    
def verif_taxid_incompability(df):
    df = df.copy()
    # Apply the function to each row in the dataframe
    df['validation'] = df.apply(validate_taxonomy, axis=1)
    values = df[ 'validation'].value_counts()

    c = 0
    for key, _ in values.items():
        if isinstance(key, dict):
            if len(key.keys()) >1 and key['taxid'] :


                c+=len(key.keys())-1
                print(key)
    print(c, ' inconsistencies found')

def final_process(df):

    df= df[[ 'taxid_ncbi', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species', 'sequence']]
    df.loc[:,'taxid_ncbi'] = df['taxid_ncbi'].astype(int)
    df =df.drop_duplicates( keep='first')
    return df

def info_dataframe(df):

    max=0
    
    min=np.inf

    len_df=df.shape[0] 
    print( f"nombre d'échantillon : {len_df}")
    print(f'nombre unique sequence : {len(df["sequence"].value_counts())}')
    for seq in df['sequence']:
        l=len(seq)
        if l>max:
            max=l
        if l<min:
            min=l


    print(f"taille max de séquence : {max}")
    print(f"taille min de sequence : {min}")

    
    print(f'nombre de genus : {len(df["genus"].value_counts())}')


    print(f'nombre de famille : {len(df["family"].value_counts())}')


    print(f'nombre de order : {len(df["order"].value_counts())}')


    
    print(f'nombre de class : {len(df["class"].value_counts())}')


    print(f'nombre de phylum : {len(df["phylum"].value_counts())}')


    print(f'nombre d"espèce : {len(df["species"].value_counts())}')


def pre_process_mifish(path_mitofish, path_genbank):
    '''
    Pre-process the data extracted from MitoFish and NCBI
        :param mitophish: path to the data extracted from MitoFish with CRABS ( separated by `tab`, without header)
        :param ncbi: path to the data extracted from NCBI with CRABS ( separated by `tab`, without header)
    '''

    mifish_genbank= pd.read_csv(path_genbank, sep='\t',header=None)
    mifish_genbank = rename_columns(mifish_genbank)

    mifish_mitofish = pd.read_csv(path_mitofish, sep='\t',header=None)
    mifish_mitofish = rename_columns(mifish_mitofish)

    all_mifish = pd.concat([mifish_mitofish, mifish_genbank])
   
    mifish_nan = all_mifish[all_mifish['class'].isna()]
    cleaned_mifish = pd.concat([remove_not_desired(mifish_nan), all_mifish])

    # Filter sequence lenght
    cleaned_mifish_correct_len = cleaned_mifish[cleaned_mifish['sequence'].str.len() >= 25]


    # Filter sequience contains N
    cleaned_mifish_no_N = cleaned_mifish_correct_len[cleaned_mifish_correct_len['sequence'].str.contains('N') == False]

    # Fill NaN
    mifish = fill_correction(cleaned_mifish_no_N)

    # Keep only Actinopteri and Chondrichthyes
    mifish = mifish[(mifish['class'] == 'Actinopteri') | (mifish['class'] == 'Chondrichthyes')]

    mifish = clean_taxo_consistency(mifish, verif=True)

    verif_taxid_incompability(mifish)

    mifish = final_process(mifish)

    mifish.to_csv("data_clean/mifish_clean.tsv", sep='\t', index=False)

    return  mifish


def pre_process_berry(path_genbank):
   

    berry_genbank= pd.read_csv(path_genbank, sep='\t',header=None)
    berry_genbank = rename_columns(berry_genbank)

   
    berry_nan = berry_genbank[berry_genbank['class'].isna()]
    berry_no_nan = berry_genbank[~berry_genbank['class'].isna()]
    cleaned_berry = pd.concat([remove_not_desired(berry_nan), berry_no_nan])

    # Filter sequence lenght
    cleaned_berry_correct_len = cleaned_berry[cleaned_berry['sequence'].str.len() >= 25]


    # Filter sequience contains N
    cleaned_berry_no_N = cleaned_berry_correct_len[cleaned_berry_correct_len['sequence'].str.contains('N') == False]

    # Fill NaN
    berry = fill_correction(cleaned_berry_no_N)

    # Keep only Actinopteri and Chondrichthyes
    berry = berry[(berry['class'] == 'Actinopteri') | (berry['class'] == 'Chondrichthyes')]

    berry = clean_taxo_consistency(berry, verif=True)

    verif_taxid_incompability(berry)

    berry = final_process(berry)

    berry.to_csv("data_clean/berry_clean.tsv", sep='\t', index=False)

    return  berry


def pre_process_teleo(path_mitofish, path_genbank):
    '''
    Pre-process the data extracted from MitoFish and NCBI
        :param mitophish: path to the data extracted from MitoFish with CRABS ( separated by `tab`, without header)
        :param ncbi: path to the data extracted from NCBI with CRABS ( separated by `tab`, without header)
    '''
    print(" Read data")

    teleo_genbank= pd.read_csv(path_genbank, sep='\t',header=None)
    teleo_genbank = rename_columns(teleo_genbank)


    teleo_mitofish = pd.read_csv(path_mitofish, sep='\t',header=None)
    teleo_mitofish = rename_columns(teleo_mitofish)

    all_teleo = pd.concat([teleo_mitofish, teleo_genbank])

    print("Fill/Remove NaN")
    teleo_nan = all_teleo[all_teleo['class'].isna()]
    teleo_no_nan = all_teleo[~all_teleo['class'].isna()]
    cleaned_teleo = pd.concat([remove_not_desired(teleo_nan), teleo_no_nan])

    # Filter sequence lenght
    cleaned_teleo_correct_len = cleaned_teleo[cleaned_teleo['sequence'].str.len() >= 20]

    # Filter sequience contains N
    cleaned_teleo_no_N = cleaned_teleo_correct_len[cleaned_teleo_correct_len['sequence'].str.contains('N') == False]

    # Fill NaN
    teleo = fill_correction(cleaned_teleo_no_N)

    # Keep only Actinopteri and Chondrichthyes
    teleo = teleo[(teleo['class'] == 'Actinopteri') | (teleo['class'] == 'Chondrichthyes')]

    print("Clean taxo consistency")
    teleo = clean_taxo_consistency(teleo, verif=True)

    print("Clean taxid incompability")
    teleo = clean_taxid_incompability(teleo)

    print("Verif taxid incompability")
    verif_taxid_incompability(teleo)


    teleo = final_process(teleo)

    teleo.to_csv("data_clean/teleo_clean.tsv", sep='\t', index=False)

    return teleo


def fold_6_data(df,out_put):
    n_splits = 6
    for k in range(n_splits):
        # fill the fold column with -1
        df[f'fold_{k}'] = "none"


    families = df['family'].unique()

    for family in families:

        family_data = df[df['family'] == family]
        genus_labels = family_data['genus'].unique()
        genus_number = family_data['genus'].nunique()

        # exclude family with only one genus (cant be split)
        if genus_number ==1:
            continue
        
        # if the number of genus is smaller than the number of splits
        elif genus_number < n_splits :
            skf = KFold(n_splits=genus_number)

        else :
            skf = KFold(n_splits=n_splits)

        
        # shuffle the fold assignment
        random_fold_assigment = np.arange(min(genus_number, n_splits))
        np.random.shuffle(random_fold_assigment)

        # partition data at genus level
        for fold, (train_index, val_index) in enumerate(skf.split(genus_labels)):
            
            # get the genus labels for the current fold
            val_genus = genus_labels[val_index]
            train_genus = genus_labels[train_index]

            # select validation data
            val_data = df[df['genus'].isin(val_genus)]

            if len(val_data)>1:
                # if there are more than 1 sample in the validation set, 50/50 split it into validation and test
                val_index , test_index = train_test_split(val_data.index, test_size=0.5)
            else:
                # if there is only one sample in the validation set, use it as test
                val_index = []
                test_index = val_data.index

            # fill the fold column
            df.loc[val_index, f'fold_{random_fold_assigment[fold]}'] = 'val'
            df.loc[test_index, f'fold_{random_fold_assigment[fold]}'] = 'test'
            df.loc[df['genus'].isin(train_genus), f'fold_{random_fold_assigment[fold]}'] = 'train'

        # fill the other fold if genus_number < n_splits
        if fold < n_splits-1:
            
            a=np.arange(fold+1)
            np.random.shuffle(a)
            dulicate = np.tile(a, math.ceil((n_splits-fold-1)/(fold+1)))[:n_splits-fold-1]
            for i,f in enumerate(range(fold + 1, n_splits)):
                
                # duplicate the fold assignment based on `duplicate` index
                df.loc[family_data.index, f'fold_{f}'] = df.loc[family_data.index, f'fold_{dulicate[i]}'].copy()
    # save the data
    df.to_csv(out_put, index=False)

    return df

def get_repartition(df):

    repartition = {}

    for i in range(6):
        print("-------------------")
        print(f"Fold {i+1}")

        val =df[df[f'fold_{i}'] == 'val']
        train =df[df[f'fold_{i}'] == 'train']
        test =df[df[f'fold_{i}'] == 'test']
        val_test = pd.concat([val,test])

        print(f"Train genus ratio : {train['genus'].nunique() / (train['genus'].nunique() + val_test['genus'].nunique() )}")
        print(f'Train samples ratio : {train.shape[0] /(val.shape[0] + train.shape[0] + test.shape[0])}')
        print(f"Val samples ratio : {val.shape[0] /(val.shape[0] + train.shape[0] + test.shape[0])}")
        print(f"Test samples ratio : {test.shape[0] /(val.shape[0] + train.shape[0] + test.shape[0])}")

        assert set(val_test['genus']).isdisjoint(set(train['genus'])), set(val_test['genus']).intersection(set(train['genus']))
        repartition[i] = df[f'fold_{i}'].value_counts().to_dict()

    return repartition

def build_file(df_with_folds, name_marker):

    os.makedirs(f"dataset/{name_marker}/folds", exist_ok=True)
    for i in range(6):

        os.makedirs(f"dataset/{name_marker}/folds/fold_{i+1}", exist_ok=True)
        
        train = df_with_folds[df_with_folds[f'fold_{i}'] == 'train']
        val = df_with_folds[df_with_folds[f'fold_{i}'] == 'val']
        test = df_with_folds[df_with_folds[f'fold_{i}'] == 'test']

        #save genus for validation and test
        json_data = pd.concat([val,test])['genus'].unique().tolist()
        json.dump(json_data, open(rf"dataset/{name_marker}/folds/fold_{i+1}/test_genus.json", 'w'))

        columns = ['taxid_ncbi','kingdom','phylum','class','order','family','genus','species','sequence']
        val[columns].to_csv(f"dataset/{name_marker}/folds/fold_{i+1}/val.csv", sep=',', index=False, header=True)
        train[columns].to_csv(rf"dataset/{name_marker}/folds/fold_{i+1}/train.csv", sep=',', index=False, header=True)
        test[columns].to_csv(rf"dataset/{name_marker}/folds/fold_{i+1}/test.csv", sep=',', index=False, header=True)

def mutate_dna_sequence(sequence, mutation_probability):
    mutated_sequence = ""
    
    for base in sequence:
        if random.random() < mutation_probability:
            mutated_base = random.choice(['A', 'T', 'C', 'G'])
            while mutated_base == base:                             # :)
                mutated_base = random.choice(['A', 'T', 'C', 'G'])  # :)
            mutated_sequence += mutated_base
        else:
            mutated_sequence += base
    
    return mutated_sequence

def split_and_mutate_sequence(sequence):
    '''
    Augment DNA by random mutation, mutation proba are based on teleo marker intra-family variance'''
    # Calculate the lengths of each part
    length_1 = int(len(sequence) * 0.06)
    length_2 = int(len(sequence) * 0.62)
    length_3 = int(len(sequence) * 0.29)
    
    # Split the sequence into three parts
    part_1 = sequence[:length_1]
    part_2 = sequence[length_1:length_1+length_2]
    part_3 = sequence[length_1+length_2:]
    
    # Apply mutate_dna_sequence to each part with respective probabilities
    mutated_part_1 = mutate_dna_sequence(part_1, 0.012)
    mutated_part_2 = mutate_dna_sequence(part_2, 0.12)
    mutated_part_3 = mutate_dna_sequence(part_3, 0.004)
    
    # Concatenate the mutated parts into a new sequence
    mutated_sequence = mutated_part_1 + mutated_part_2 + mutated_part_3
    
    # Return the mutated sequence
    return mutated_sequence

def mutate(df, full_random = True):
    # Calculate the value count of the "family" column
    family_counts = df['family'].value_counts()

    # Get the families with a count below 200
    families_below_200 = family_counts[family_counts < 300].index

    # Duplicate rows for families with a count below 200
    for family in tqdm(families_below_200):
        count = family_counts[family]
        if count == 1:
            # Duplicate the only row 199 times
            duplicated_rows = pd.concat([df[df['family'] == family]] * 299, ignore_index=True)
        else:
            # Duplicate random members of the family to reach a count of 200
            duplicated_rows = df[df['family'] == family].sample(n=300-count, replace=True)
        
        # Apply mutations to each duplicated row's sequence
        if full_random:
            duplicated_rows['sequence'] = duplicated_rows['sequence'].apply(lambda seq: mutate_dna_sequence(seq, 0.05))
        else:
            duplicated_rows['sequence'] = duplicated_rows['sequence'].apply(lambda seq: split_and_mutate_sequence(seq))
        
        # Change the species to "Synthetic" for the duplicated rows
        duplicated_rows['species'] = 'Synthetic'
        
        df = pd.concat([df, duplicated_rows], ignore_index=True)

    return df

def mutate_data_fold(data_path):
    '''
    Mutate the data
        :param data_path: folds location (data/markername_fold/)
    '''
    
    for fold in range(1, 7):
        df = pd.read_csv(data_path +f"/fold_{fold}/train.csv")
        df = mutate(df)
        df.to_csv(data_path +f"/fold_{fold}/train_low_augment.csv", index=False)
