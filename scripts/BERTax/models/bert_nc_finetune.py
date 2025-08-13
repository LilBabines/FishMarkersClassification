import tensorflow as tf
from tensorflow import keras
import json
from preprocessing.process_inputs import get_class_vectors, ALPHABET
from models.model import PARAMS
import numpy as np
from tensorflow.keras.utils import Sequence
from models.bert_utils import get_token_dict, seq2tokens, predict
from models.bert_utils import generate_bert_with_pretrained, generate_bert_with_pretrained_multi_tax, \
    get_classes_and_weights_multi_tax
from random import shuffle, sample
from sklearn.model_selection import train_test_split
import os
import argparse
from dataclasses import dataclass, field
from typing import List, Optional
from logging import warning
import pickle
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard, EarlyStopping, CSVLogger
from os.path import splitext
import pandas as pd
from sklearn.metrics import balanced_accuracy_score

print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
mirrored_strategy = tf.distribute.MirroredStrategy()


# from tensorflow.keras.mixed_precision import set_global_policy
# set_global_policy('mixed_float16')


learning_rate = 1e-5
tax_ranks = ["order", "family"]
# classes = pickle.load(open("data/data_set_multi/classes_dict.pkl", 'rb'))

def load_dataset(filepath):
    df = pd.read_csv(filepath)
    x = df["sequence"].tolist()
    y_family = df["family"].tolist()
    y_order = df["order"].tolist()
    return x, y_family, y_order


@dataclass
class FragmentGenerator_multi_tax(Sequence):

    def __init__(self, x, y, seq_len, max_seq_len=22, k=3, stride=3,
                 batch_size=32, seq_len_like=None, window=False, **kwargs):
        super().__init__(**kwargs)
        self.x = x
        self.y = y
        self.seq_len = seq_len
        self.max_seq_len = max_seq_len
        self.k = k
        self.stride = stride
        self.batch_size = batch_size
        self.seq_len_like = seq_len_like
        self.window = window


        self.token_dict = get_token_dict(ALPHABET, k=3)
        if (self.max_seq_len is None):
            self.max_seq_len = self.seq_len


    # def __post_init__(self):
    #     # from utils.tax_entry import TaxDB
    #     # self.taxDB = TaxDB(data_dir="/mnt/fass2/projects/fm_read_classification_comparison/taxonomy")

    def __len__(self):
        return np.ceil(len(self.x)
                       / float(self.batch_size)).astype(int)

    def __getitem__(self, idx):

        batch_fragments = self.x[idx * self.batch_size:(idx + 1) * self.batch_size]
    
        batch_x = [seq2tokens(seq, self.token_dict, seq_length=self.seq_len,
                            max_length=self.max_seq_len, k=self.k,
                            stride=self.stride, window=self.window,
                            seq_len_like=self.seq_len_like)
                for seq in batch_fragments]

        # Stack into arrays/tensors
        x0 = tf.convert_to_tensor([_[0] for _ in batch_x])
        x1 = tf.convert_to_tensor([_[1] for _ in batch_x])
        X = (x0, x1)  # Tuple — not list

        batch_y = self.y[idx * self.batch_size:(idx + 1) * self.batch_size]
        
        y = tuple([tf.convert_to_tensor([_[0] for _ in batch_y]),tf.convert_to_tensor([_[1] for _ in batch_y])])    
                
        
        return X, y
        
def get_fine_model_multi_tax(pretrained_model_file, num_classes, tax_ranks):
    model_fine = generate_bert_with_pretrained_multi_tax(pretrained_model_file, num_classes, tax_ranks)
    model_fine.compile(keras.optimizers.Adam(learning_rate),
                       loss={
                            'order_out': 'categorical_crossentropy',
                            'family_out': 'categorical_crossentropy'
                        },
                        metrics={
                            'order_out': 'accuracy',
                            'family_out': 'accuracy'
                        },
                        jit_compile=False,
                        ) # 
    max_length = model_fine.input_shape[0][1]

    return model_fine, max_length



if __name__ == '__main__':
# def multi_tax() : 

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='fine-tune BERT on pre-generated fragments')
    parser.add_argument('pretrained_bert')
    parser.add_argument('--seq_len', help=' ', type=int, default=22)
    parser.add_argument('--seq_len_like', default=None,
                        help='path of pickled class dict of seq lens for '
                             'generating sampled sequence sizes')
    parser.add_argument('--k', help=' ', default=3, type=int)
    parser.add_argument('--stride', help=' ', default=3, type=int)
    parser.add_argument('--batch_size', help=' ', type=int, default=8)
    parser.add_argument('--epochs', help=' ', type=int, default=20)
    parser.add_argument('--nr_seqs', help=' ', type=int, default=0)
    parser.add_argument('--learning_rate', help=' ', type=float, default=1e-5)
    parser.add_argument('--store_predictions', help=' ', action='store_true')
    parser.add_argument('--store_train_data', help=' ', action='store_true')
    parser.add_argument('--roc_auc', help=' ', action='store_true')
    parser.add_argument('--multi_tax', help='predict multiple taxonomic ranks with a single model, see also --tax_ranks', action='store_true')
    parser.add_argument('--tax_ranks', help='taxonomic ranks to train for',
                        nargs='+', default=["order", "family"])
    parser.add_argument('--only_test_model', help='don\'t train a model but evaluate the performance', action='store_true')
    parser.add_argument('--use_defined_train_test_set', help='useful for benchmarking, uses output from preprocessing.make_dataset for training and performance evaluation', action='store_true')
    args = parser.parse_args()

    tax_ranks = args.tax_ranks
    multi_tax = True
    test = False

    learning_rate = args.learning_rate


    if (args.seq_len_like is not None):
        seq_len_dict = pickle.load(open(args.seq_len_like, 'rb'))
        min_nr_seqs = min(map(len, seq_len_dict.values()))
        seq_len_like = []
        for k in seq_len_dict:
            seq_len_like.extend(np.random.choice(seq_len_dict[k], min_nr_seqs)
                                // args.k)
    else:
        seq_len_like = None

    data_set = ["berry","ac16",'mifish','teleo']

    for data_name in data_set:

        print("------------------------------------")
        print("DATA : ", data_name)
        print("------------------------------------")

        os.makedirs(data_name, exist_ok=True)
        datatrain = pd.read_csv(f"data/{data_name}/folds/fold_1/train.csv")
        dataval = pd.read_csv(f"data/{data_name}/folds/fold_1/val.csv")
        datatest = pd.read_csv(f"data/{data_name}/folds/fold_1/test.csv")
        data = pd.concat([datatrain, dataval, datatest])
        max_seq = max(data['sequence'], key=len)
        max_kmer_len = (len(max_seq) // args.k ) +1

        seq_len = max_kmer_len

        unique_family = data["family"].unique()
        unique_order = data["order"].unique()
        

        #label to index mapping
        family_to_index = {family: i for i, family in enumerate(unique_family)}
        order_to_index = {order: i for i, order in enumerate(unique_order)}

        # json.dump(family_to_index, open(os.path.join("data",data_name, "family_to_index.json"), 'w'))
        # json.dump(order_to_index, open(os.path.join("data",data_name, "order_to_index.json"), 'w'))

        
        
        for fold in range(1,7):
            if os.path.exists(os.path.join(data_name, f"fold_{fold}", "model.best.acc.h5")) and not test:
                print(f"fold {fold} already trained, skipping")
                continue
            
            test_x, test_y_family, test_y_order = load_dataset(os.path.join("data",data_name,f"folds/fold_{fold}", "test.csv"))
            train_x, train_y_family, train_y_order = load_dataset(os.path.join("data",data_name,f"folds/fold_{fold}", "train_low_augment.csv"))
            val_x, val_y_family, val_y_order = load_dataset(os.path.join("data",data_name,f"folds/fold_{fold}", "val.csv"))

            save_path = os.path.join(data_name, f"fold_{fold}")
            os.makedirs(save_path, exist_ok=True)

            # idx to one hot encoding
            train_y = list(zip(tf.one_hot([order_to_index[order] for order in train_y_order], len(unique_order)),
                        tf.one_hot([family_to_index[family] for family in train_y_family], len(unique_family))))
            
            val_y = list(zip(tf.one_hot([order_to_index[order] for order in val_y_order], len(unique_order)),
                        tf.one_hot([family_to_index[family] for family in val_y_family], len(unique_family))))
            
            test_y = list(zip(tf.one_hot([order_to_index[order] for order in test_y_order], len(unique_order)),
                        tf.one_hot([family_to_index[family] for family in test_y_family], len(unique_family))))
            
            if test:
                pass
                # from models.bert_utils import load_bert
                # best = "berry/fold_3/model.best.acc.h5"
                # model = load_bert(best, compile_=True)
                # max_length = model.input_shape[0][1]
            else:
                # building model
                if args.multi_tax:
                    num_classes = [len(unique_order), len(unique_family)]
                    
                    model, max_length = get_fine_model_multi_tax(args.pretrained_bert, num_classes=num_classes,
                                                                tax_ranks=tax_ranks)
                else:
                    raise ValueError("multi_tax must be True for this script")
                
                if (args.seq_len > max_length):
                    warning(f'desired seq len ({args.seq_len}) is higher than possible ({max_length})'
                            f'setting seq len to {max_length}')
                    args.seq_len = max_length

            generator_args = {
                'max_seq_len': max_length, 'k': args.k, 'stride': args.stride,
                'batch_size': args.batch_size, 'window': True,
                'seq_len_like': seq_len_like}
            model.summary()

            if not test:
        

                filepath1 = os.path.join(save_path, "model.best.acc.h5")
                filepath2 = os.path.join(save_path, "model.best.loss.h5")
                checkpoint1 = ModelCheckpoint(filepath1, monitor='val_family_out_accuracy', verbose=0, save_best_only=True,
                                            save_weights_only=False, mode='max')
                checkpoint2 = ModelCheckpoint(filepath2, monitor='val_loss', verbose=0, save_best_only=True,
                                            save_weights_only=False, mode='min')
                checkpoint3 = EarlyStopping('val_loss', min_delta=0, patience=8, restore_best_weights=True)
                tensorboard_callback = TensorBoard(log_dir=os.path.join(save_path,"logs"), histogram_freq=1,
                                                write_graph=True,
                                                write_images=True, update_freq=100, embeddings_freq=1)
                csv_logger = CSVLogger(os.path.join(save_path,"traning.log"))
                # callbacks_list = [checkpoint1, checkpoint2, checkpoint3]
                callbacks_list = [csv_logger,checkpoint1, checkpoint2, checkpoint3, tensorboard_callback]

                
       
            
            test_g = FragmentGenerator_multi_tax(test_x, test_y, seq_len=args.seq_len,
                                                    **generator_args)
          

            if not test:

                try:

                    train_gen = FragmentGenerator_multi_tax(train_x, train_y,
                                                            seq_len=args.seq_len,
                                                                **generator_args)
                    val_gen = FragmentGenerator_multi_tax(val_x, val_y,
                                                            seq_len=args.seq_len, 
                                                                **generator_args)

                    model.fit(
                        train_gen,
                        validation_data = val_gen,
                        callbacks=callbacks_list, epochs=args.epochs
                        )
                except (KeyboardInterrupt):

                    print("training interrupted, current status will be saved and tested, press ctrl+c to cancel this")
                    file_suffix = '_aborted.hdf5'
                    model.save(splitext(args.pretrained_bert)[0] + '_aborted.h5')
                    print('testing...')
                    result = model.evaluate(test_g)
                    print("test results:", *zip(model.metrics_names, result))
                    # exit()

                
                model.save(os.path.join(save_path, "model_last.h5"))
                print('testing...')

            if (args.store_predictions or args.roc_auc):
                predicted = predict(
                    model, test_g,
                    args.roc_auc, classes=None, return_data=args.store_predictions, calc_metrics=False)
                y_true, y_pred = predicted["data"]
                for i in range(len(y_pred)):
                    acc = balanced_accuracy_score(np.argmax(y_true[i], axis=1), np.argmax(y_pred[i], axis=1))
                    print(f"{tax_ranks[i]} acc:", acc)
                    print(pd.crosstab(np.argmax(np.array(y_true[i]), axis=1), np.argmax(np.array(y_pred[i]), axis=1),
                                    rownames=['True'], colnames=['Predicted'], margins=True))
                result = predicted['metrics']
                metrics_names = predicted['metrics_names']
                if (args.store_predictions):
                    import pickle

                    pickle.dump(predicted, open(os.path.join(save_path,"test_multi_predictions.pkl"), 'wb'))

            else:
                result = model.evaluate(test_g)
                metrics_names = model.metrics_names

