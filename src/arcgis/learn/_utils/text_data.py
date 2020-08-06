import re
import os
import sys
import copy
import types
import random
import warnings
import traceback
import pandas as pd
from functools import partial

HAS_FASTAI = True
try:
    import torch
    import arcgis
    from fastai.text import TextList, TextClasDataBunch, pad_collate
    from fastai.data_block import CategoryList, MultiCategoryList
except Exception as e:
    import_exception = "\n".join(traceback.format_exception(type(e), e, e.__traceback__))
    HAS_FASTAI = False

HAS_BEAUTIFULSOUP = True
try:
    from bs4 import BeautifulSoup
except:
    HAS_BEAUTIFULSOUP = False
else:
    warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

HAS_NUMPY = True
try:
    import numpy as np
except:
    HAS_NUMPY = False


max_len=100


# Overriding show_text_xys function of TextList to display the dataframe in desired fashion
def show_text_xys(self, xs, ys, max_len:int=max_len):
    "Show the `xs` (inputs) and `ys` (targets). `max_len` is the maximum number of tokens displayed."
    if not HAS_NUMPY:
        raise Exception("This module requires numpy.")

    from IPython.display import display, HTML
    names = ['idx','text'] if self._is_lm else ['text','target']
    items = []
    for i, (x,y) in enumerate(zip(xs,ys)):
        txt_x = ' '.join(x.text.split(' ')[:max_len]) if max_len is not None else x.text
        items.append([i, txt_x] if self._is_lm else [txt_x, y])
    items = np.array(items)
    df = pd.DataFrame({n:items[:,i] for i,n in enumerate(names)}, columns=names)
    dataframe_style = df.style\
        .set_table_styles([dict(selector='th', props=[('text-align', 'left')])])\
        .set_properties(**{'text-align': "left"}).hide_index()
    display(dataframe_style)


# Overriding show_text_xyzs function of TextList to display the dataframe in desired fashion
def show_text_xyzs(self, xs, ys, zs, max_len:int=max_len):
    "Show `xs` (inputs), `ys` (targets) and `zs` (predictions). `max_len` is the maximum number of tokens displayed."
    if not HAS_NUMPY:
        raise Exception("This module requires numpy.")

    from IPython.display import display, HTML
    items,names = [],['text','target','prediction']
    for i, (x,y,z) in enumerate(zip(xs,ys,zs)):
        txt_x = ' '.join(x.text.split(' ')[:max_len]) if max_len is not None else x.text
        items.append([txt_x, y, z])
    items = np.array(items)
    df = pd.DataFrame({n:items[:,i] for i,n in enumerate(names)}, columns=names)
    dataframe_style = df.style \
        .set_table_styles([dict(selector='th', props=[('text-align', 'left')])]) \
        .set_properties(**{'text-align': "left"}).hide_index()
    display(dataframe_style)

def read_file(path):
    filename, file_extension = os.path.splitext(path)
    if file_extension == ".csv":
        return pd.read_csv(path, dtype='str')
    else:
        return pd.read_csv(path, sep="\t", dtype='str')


def save_data_in_model_metrics_html(text, path, model_characteristics_folder):
    file_path = os.path.join(path, "model_metrics.html")
    if os.path.exists(file_path):
        with open(file_path, mode="a+", encoding="utf-8") as fp:
            fp.write(text)

    folder_path = os.path.join(path, model_characteristics_folder)
    if os.path.exists(folder_path):
        with open(os.path.join(folder_path, "sample_results.html"), mode="w", encoding="utf-8") as fp:
            fp.write(text)


class TextDataObject:

    databunch_kwargs = {'num_workers': 0} if sys.platform == 'win32' else {}
    databunch_kwargs["pin_memory"] = True
    if getattr(arcgis.env, "_processorType", "") == "GPU" and torch.cuda.is_available():
        databunch_kwargs["device"] = torch.device("cuda")
    elif getattr(arcgis.env, "_processorType", "") == "CPU":
        databunch_kwargs["device"] = torch.device("cpu")
    else:
        databunch_kwargs["device"] = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    def __init__(self):
        self._bs = None
        self._is_empty = True
        self._train_df = None
        self._valid_df = None
        self._text_cols = None
        self._label_cols = list()
        self._databunch = None
        self._training_indexes = list()
        self.classes = None

    @classmethod
    def prepare_data_for_classification(
            cls,
            data,
            text_cols,
            label_cols,
            train_file="train.csv",
            valid_file=None,
            val_split_pct=0.1,
            seed=42,
            batch_size=8,
            process_labels=False,
            remove_html_tags=False,
            remove_urls=False
        ):
        if not HAS_FASTAI:
            return

        text_data = cls()
        if not os.path.exists(data):
            raise Exception(f"Provided data directory - {data}, does not exists")

        training_file_path = os.path.join(data, train_file)

        if not os.path.exists(training_file_path):
            raise Exception(f"Provided data directory does not contain {train_file} file")

        train_df = read_file(training_file_path)
        train_df = cls._preprocess_df(train_df, text_cols, label_cols, process_labels, remove_html_tags, remove_urls)

        random.seed(seed)

        if valid_file is not None and os.path.exists(os.path.join(data, valid_file)):
            validation_file_exists = True
        else:
            validation_file_exists = False

        if validation_file_exists:
            valid_df = read_file(os.path.join(data, valid_file))
            valid_df = cls._preprocess_df(valid_df, text_cols, label_cols, process_labels, remove_html_tags, remove_urls)
        else:
            validation_indexes = random.sample(range(train_df.shape[0]), round(val_split_pct * train_df.shape[0]))
            training_indexes = list(set([i for i in range(train_df.shape[0])]) - set(validation_indexes))

            temp_df = copy.deepcopy(train_df)
            train_df = temp_df.loc[training_indexes]
            valid_df = temp_df.loc[validation_indexes]
            # Removing rows with empty strings in the text_cols from the training and validation data
            train_df[text_cols].replace('', np.nan, inplace=True)
            train_df.dropna(inplace=True)
            valid_df[text_cols].replace('', np.nan, inplace=True)
            valid_df.dropna(inplace=True)
            # Resetting dataframe indexes for training anf validation dataframe
            train_df.reset_index(drop=True, inplace=True)
            valid_df.reset_index(drop=True, inplace=True)
            del temp_df
        if len(label_cols)>1:
            text_data.classes = label_cols
        else:
            text_data.classes = valid_df[label_cols[0]].unique().tolist()
        text_data._bs = batch_size
        text_data._text_cols = text_cols
        text_data._label_cols = label_cols
        text_data._train_df = train_df[[text_cols] + label_cols]
        text_data._valid_df = valid_df[[text_cols] + label_cols]
        text_data._training_indexes = range(0, train_df.shape[0])

        return text_data

    def get_databunch(self):
        if self._is_empty:
            return None
        else:
            return self._databunch

    def _prepare_databunch(self, tokenizer, vocab, pad_first, pad_idx):
        """
        Wrapper to create fastai TextDataBunch Object
        """
        if not HAS_FASTAI:
            return

        self._databunch = TextClasDataBunch.\
            from_df(".",
                    train_df=self._train_df,
                    valid_df=self._valid_df,
                    tokenizer = tokenizer,
                    vocab=vocab,
                    include_bos=False,
                    include_eos=False,
                    text_cols=self._text_cols,
                    label_cols=self._label_cols,
                    bs=self._bs,
                    collate_fn=partial(pad_collate, pad_first=pad_first, pad_idx=pad_idx),
                    **self.databunch_kwargs
                    )

        TextList.show_xys = types.MethodType(show_text_xys, TextList)
        TextList.show_xyzs = types.MethodType(show_text_xyzs, TextList)
        self._is_empty = False

    @staticmethod
    def _preprocess_df(dataframe, text_cols, label_cols, process_labels, remove_html_tags=False, remove_urls=False):
        """
        Do some pre-processing on the dataframe columns
        """
        dataframe[text_cols] = dataframe.apply(
            lambda row: TextDataObject.process_text(row[text_cols], remove_html_tags, remove_urls), axis=1)
        if process_labels:
            for label in label_cols:
                dataframe[label] = dataframe.apply(
                    lambda row: TextDataObject.process_text(row[label], remove_html_tags, remove_urls), axis=1)

        return dataframe

    @staticmethod
    def process_text(text, remove_html_tags=False, remove_urls=False):
        """
        Perform some basic cleanup like removing HTML tags, removing urls,
        converting multiple white spaces to single white space
        """
        if remove_urls: text = re.sub(r'\b(?:(?:https?|ftp)://)?\w[\w-]*(?:\.[\w-]+)+\S*', ' ', text)

        # text = re.sub(r'<.*?>', '', text)
        if remove_html_tags:
            if not HAS_BEAUTIFULSOUP:
                raise Exception("This module requires BeautifulSoup.")
            text = BeautifulSoup(text, 'html.parser').get_text(separator=" ", strip=True)

        if remove_html_tags or remove_urls: text = re.sub(' +', ' ', text)
        return text.strip()

    def show_batch(self, rows=5, max_len=max_len):
        """
        Shows a batch of dataframe prepared without applying transforms.
        """
        processed_data = []
        rows = min(len(self._training_indexes), rows)
        random_batch = random.sample(self._training_indexes, rows)
        dataframe = self._train_df.loc[random_batch]
        if len(self._label_cols) > 1:
            for idx, item in dataframe.iterrows():
                target = ";".join([column for column in self._label_cols if int(getattr(item, column))])
                source = getattr(item, self._text_cols)
                if max_len is not None: source = " ".join(source.split(" "))[:max_len]
                processed_data.append([source, target])

            dataframe = pd.DataFrame(processed_data, columns=["source", "target"])

        return dataframe.style\
            .set_table_styles([dict(selector='th', props=[('text-align', 'left')])])\
            .set_properties(**{'text-align': "left"}).hide_index()

    def create_empty(self, text_cols, label_cols, classes, is_multilabel=False):
        self._text_cols = text_cols
        self._label_cols = label_cols

        text_list = TextList([], ignore_empty=True).split_by_idx([])
        if is_multilabel:
            self._databunch = text_list.label_const(0, label_cls=MultiCategoryList, classes=classes).databunch()
        else:
            self._databunch = text_list.label_const(0, label_cls=CategoryList, classes=classes).databunch()
        self._is_empty = False

        # self._train_df = self._create_empty_df(batch_size, [text_cols] + label_cols)
        # self._valid_df = self._create_empty_df(batch_size, [text_cols] + label_cols)

    # @staticmethod
    # def _create_empty_df(batch_size, columns):
    #     l1 = ["" for x in columns]
    #     l2 = [l1 for x in range(batch_size)]
    #     return pd.DataFrame(l2, columns=columns)

