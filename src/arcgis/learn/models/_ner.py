try:
    import spacy
    import pandas as pd
    from fastprogress import master_bar, progress_bar
    from ._codetemplate import entity_recognizer_placeholder
    HAS_SPACY=True
except:
    HAS_SPACY=False

from ._arcgis_model import ArcGISModel
import os,json,logging
from pathlib import Path
import random,os
from ._ner_utils import *
from time import sleep
from collections.abc import Iterable

def _raise_spacy_import_error():
    return logging.warning('This module requires spacy version 2.1.8 or above and fastprogress. Install it using "pip install spacy==2.1.8 fastprogress pandas"')




class EntityRecognizer(ArcGISModel):
    """
    Creates an entity recognition model to extract text entities from unstructured text documents.
    Based on Spacy's `EntityRecognizer <https://spacy.io/api/entityrecognizer>`_

    =====================   ===========================================
    **Argument**            **Description**
    ---------------------   -------------------------------------------
    data                    Requires data object returned from
                            ``prepare_data`` function.
    ---------------------   -------------------------------------------
    lang                    Optional string. Language-specific code, 
                            named according to the language’s `ISO code <https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes>`_
                            The default value is 'en' for English.                       
    =====================   ===========================================

    :returns: ``EntityRecognizer`` Object
    """
    
    def __init__(self, data=None,lang='en'):
        if not HAS_SPACY:
            _raise_spacy_import_error()
        super().__init__(data)
        self._code = entity_recognizer_placeholder
        self._emd_template = {}
        self.model_dir=None
        self.model = spacy.blank(lang)
        self.ner = self.model.create_pipe('ner')
        self.model.add_pipe(self.ner, last=True)
        self._address_tag = 'Address'  #Defines the default addres field
        self.entities = None #Stores all the entity names from the training data into a list
        self._has_address = False #Flag to identify if the training data has any address  
        self._trained = False #Flag to check if model has been trained     
        self.lang = lang
        if data:
            self._address_tag=data._address_tag
            self._has_address=data._has_address
            self.path = data.path
            self.data = data
            self.train_ds = data.train_ds
            self.val_ds = data.val_ds
        else:
            self.train_ds = None
            self.val_ds = None
            self.path = '.'

    def lr_find(self, allow_plot=True):
        """
        Not implemented for this model.
        """
        logging.error('lr_find() is not implemented for EntityRecognizer model.')
    
    def unfreeze(self):
        """
        Not implemented for this model.
        """
        logging.error('unfreeze() is not implemented for EntityRecognizer model.')

    def fit(self, epochs=20, lr=None, one_cycle=True, early_stopping=False, checkpoint=True, **kwargs):

        """
        Trains an EntityRecognition model for 'n' number of epochs..

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        epoch                   Optional integer. Number of times the model will train 
                                on the complete dataset.
        ---------------------   -------------------------------------------
        lr                      Optional float. Learning rate
                                to be used for training the model.
        ---------------------   -------------------------------------------
        one_cycle               Not implemented for this model.
        ---------------------   -------------------------------------------
        early_stopping          Not implemented for this model.    
        ---------------------   -------------------------------------------
        early_stopping          Not implemented for this model.
        =====================   ===========================================
        """

        if self.train_ds==None:
            return logging.warning('Cannot fit the model on empty data.')
        TRAIN_DATA = self.train_ds.data
        VAL_DATA = self.val_ds.data
        nlp = self.model 
        
        
        if 'ner' not in nlp.pipe_names: # create the built-in pipeline components and add them to the pipeline
            # spacy.require_gpu()
            self.ner = nlp.create_pipe('ner') # nlp.create_pipe works for built-ins that are registered with spaCy
            nlp.add_pipe(self.ner, last=True)
        i=0
        for _, annotations in TRAIN_DATA: # adding labels
            for ent in annotations.get('entities'):
                if (ent[2] not in self.ner.labels):
                    self.ner.add_label(ent[2])
            i+=1

        
        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner'] # get names of other pipes to disable them during training
        with nlp.disable_pipes(*other_pipes):  # only train NER
            nlp.vocab.vectors.name = 'spacy_pretrained_vectors'
            optimizer = nlp.begin_training()
            if lr is not None:
                if not isinstance(lr,(int,float)):
                    raise Exception('lr needs to be an int or a floating point number.')
                else:
                    optimizer.alpha=lr
            mb = master_bar(range(epochs))
            mb.write(['Epoch','Train_loss','Val_loss'],table=True)
            for itn in mb:
                random.shuffle(TRAIN_DATA)
                losses = {}
                val_losses = {}
                for text, annotations in progress_bar(TRAIN_DATA, parent=mb):
                    nlp.update(
                        [text],  # batch of texts
                        [annotations],  # batch of annotations
                        drop = 0.2,  # dropout - make it harder to memorise data
                        sgd = optimizer,  # callable to update weights
                        losses = losses)  
                if VAL_DATA:
                    for val_text, val_annotations in (VAL_DATA):
                        nlp.update([val_text],[val_annotations], sgd = None, losses = val_losses)

                train_loss = losses['ner']/len(TRAIN_DATA)
                val_loss = val_losses['ner']/len(VAL_DATA)
                mb.write([itn,round(train_loss,2),round(val_loss,2)],table=True)

        self._trained = True
        self.model = nlp
        self.entities = list({item[2:] for item in self.model.entity.move_names if item !='O'})

    def _create_emd(self, path):
        path=Path(path)
        self._emd_template["ModelConfiguration"] = "_ner"
        self._emd_template["InferenceFunction"] = "EntityRecognizer.py"
        self._emd_template['ModelFile'] = str(Path(path).name)
        self._emd_template['ModelName'] = type(self).__name__
        self._emd_template['Labels'] = self.model.entity.labels
        self._emd_template['Lang'] = self.lang
        if self._has_address:
            self._emd_template['address_tag'] = self._address_tag
        json.dump(self._emd_template, open(path/Path(path.stem).with_suffix('.emd'), 'w'), indent=4)
        pathstr = path/Path(path.stem).with_suffix('.emd')
        print(f'Model has been saved to {str(path.resolve())}')
  
    def save(self, name_or_path, **kwargs):
        """
        Saves the model weights, creates an Esri Model Definition.
        Train the model for the specified number of epochs and using the
        specified learning rates.
        
        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        name_or_path            Required string. Name of the model to save. It
                                stores it at the pre-defined location. If path
                                is passed then it stores at the specified path
                                with model name as directory name. and creates
                                all the intermediate directories.
        =====================   ===========================================
        """        
        return self._save(name_or_path, **kwargs)

    def _save(self, name_or_path, zip_files=True):
        temp=self.path
        if not self._trained:
            return logging.error("Model needs to be fitted, before saving.")

        if '\\' in name_or_path or '/' in name_or_path:
            path=Path(name_or_path)
            parent_path = path.parent
            name = path.parts[-1]
            self.model_dir = parent_path/name
            if not os.path.exists(self.model_dir):
                os.makedirs(self.model_dir)
        else:
            self.model_dir =  Path(self.path) /'models'/ name_or_path
            name = name_or_path
            if not os.path.exists(self.model_dir):
                os.makedirs(self.model_dir)
        
        self.model.to_disk(self.model_dir)
        self._create_emd(self.model_dir)
        with open(self.model_dir / self._emd_template['InferenceFunction'], 'w') as f:
            f.write(self._code)
        if zip_files:
            _create_zip(name, str(self.model_dir))


    def load(self, name_or_path):
        """
        Loads a saved EntityRecognition model from disk.
        
        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        name_or_path            Required string. Path of the emd file.
        =====================   ===========================================
        """
        if '\\' in name_or_path or '/' in name_or_path:
            name_or_path=name_or_path
            model_path = Path(name_or_path).parent
        else:
            model_path =  Path(self.path) /'models'/ name_or_path
            name_or_path=Path(self.path) /'models'/ name_or_path / f'{name_or_path}.emd'
        with open(name_or_path, 'r', encoding='utf-8') as f:
            emd = f.read()
        emd = json.loads(emd)
        address_tag= emd.get('address_tag')
        if address_tag:
            self._has_address=True
            self._address_tag=address_tag
        self.model = spacy.load(model_path)
        self.ner = self.model.get_pipe('ner')
        self._trained = True
        self.entities = list(self.model.entity.labels)
        self.model_dir=Path(name_or_path).parent.resolve()
        print(self.model)

    @classmethod
    def from_model(cls, emd_path, data=None):
        """
        Creates an EntityRecognizer from an Esri Model Definition (EMD) file.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        emd_path                Required string. Path to Esri Model Definition
                                file.
        ---------------------   -------------------------------------------
        data                    Required DatabunchNER object or None. Returned data
                                object from `prepare_data` function or None for
                                inferencing.
        
        =====================   ===========================================

        :returns: `EntityRecognizer` Object
        """  
        emd_path = Path(emd_path)
        ner = cls(data=data)
        ner.load(emd_path)
        ner.trained = True
        ner.entities = list(ner.model.entity.labels)
        return ner


    def _post_process_non_address_df(self, unprocessed_df):
        """
        This function post processes the output dataframe from extract_entities function and returns a processed dataframe.
        """
        processed_df = pd.DataFrame(columns = unprocessed_df.columns)
        for col in unprocessed_df.columns: ## converting all list columns to string
            if pd.Series(filter(lambda x: x != '',unprocessed_df[col])).apply(isinstance,args = ([str])).sum() == 0: ## split if this condition
                processed_df[col] = unprocessed_df[col].apply(",".join)  #join the list to strind and copy to the processed df
            else:
                 processed_df[col] = unprocessed_df[col] #copy to the processed df
        return processed_df

    def _post_process_address_df(self, unprocessed_df,drop):
        """
        This function post processes the output dataframe from extract_entities function and returns a processed dataframe with cleaned up missed detections.
        """
        address_tag = self._address_tag
        processed_df = pd.DataFrame(columns = unprocessed_df.columns) #creating an empty processed dataframe
        for i,adds in unprocessed_df[address_tag].iteritems(): #duplicating rows with multiple addresses to be one row per address
            if len(adds)>0:#adding data for address documents
                for j,add in enumerate(adds):
                    curr_index = len(processed_df)
                    processed_df.loc[curr_index] = unprocessed_df.loc[i]
                    processed_df.loc[curr_index][address_tag] = add
            else: #adding data for non-address documents
                curr_index = len(processed_df)
                processed_df.loc[curr_index] = unprocessed_df.loc[i]
                processed_df.loc[curr_index][address_tag] = ''
        drop_ids = []

        for i,add in processed_df[address_tag].iteritems():
            if len(add.split(' '))<2:
                drop_ids.append(i)
        del unprocessed_df

        if drop: #flag for dropping/not-dropping documents without address.
            processed_df.drop(drop_ids, inplace=True)        
        cols = processed_df.columns
        processed_df.reset_index(drop=True, inplace=True)

        for col in processed_df.columns: ## converting all list columns to string
            if col != address_tag and pd.Series(filter(lambda x: x != '',processed_df[col])).apply(isinstance,args = ([str])).sum() == 0: ## split if this condition
                processed_df[col] = processed_df[col].apply(",".join)  #join the list to strind and copy to the processed df
            else:
                 processed_df[col] = processed_df[col] #copy to the processed df
        return processed_df
    
    def _extract_entities_text(self,text):
        """
        This function extracts entities from a string"
        
        Arguments:
        text:str

        Returns:
        spacy's doc object

        Example of how to visualize the results:
        [(ent.label_,ent.text) for ent in doc_object.ents]
        """
        return self.model(text)
    
    def extract_entities(self, text_list,drop=True):
        """
        Extracts the entities from [documents in the mentioned path or text_list].
        
        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        text_list               Required string(path) or list(documents). 
                                List of documents for entity extraction OR
                                path to the documents.
        drop                    Optional bool. 
                                If documents without address needs to be 
                                dropped from the results.                                
        =====================   ===========================================

        :returns: Pandas DataFrame
        """

        if self._trained:
            df = pd.DataFrame(columns = ['TEXT','Filename']+self.entities)

            if isinstance(text_list, list):
                item_list= pd.Series(text_list)

            elif isinstance(text_list, str):
                item_names = os.listdir(text_list)
                item_list = pd.Series()
                text = []
                skipped_docs=[]
                for item_name in item_names:
                    try:
                        with open(f'{text_list}/{item_name}', 'r', encoding='utf-16', errors='ignore') as f:
                            item_list[item_name] = f.read()
                    except:
                        try:
                            with open(f'{text_list}/{item_name}', 'r', encoding='utf-8', errors='ignore') as f:
                                item_list[item_name]=f.read()
                        except:
                            skipped_docs.append(item_name)
                if len(skipped_docs):
                    print('Unable to read the following documents ', ', '.join(skipped_docs))



    
            # if self._address_tag not in self.entities and self._has_address==True:
            #     return logging.warning('Model\'s address tag does not match with any field in your data, one of the below steps could resolve your issue:\n\
            #         1. Set address tag to the address field in your data [your_model._address_tag=\'your_address_field\']\n\
            #         2. If your data does not have any address field set _has_address=False [your_model._has_address=False]')
            
            for i,item in item_list.iteritems():
                df.loc[i] = None
                doc = self._extract_entities_text(item) ## predicting entities using entity_extractor model
                text = doc.text
                tmp_ents = {}
                for ent in doc.ents:  ##Preparing a dataframe from results
                    if tmp_ents.get(ent.label_) == None:
                        tmp_ents[ent.label_] = []+[ent.text]
                    else:
                        tmp_ents[ent.label_].extend([ent.text])

                df.loc[i]['TEXT'] = text
                if isinstance(i,Iterable): #For test documents
                    df.loc[i]['Filename'] = i
                else: #for show_results()
                    df.loc[i]['Filename'] = 'Example_'+str(i)
                
                for label in tmp_ents.keys():
                    df.loc[i][label] = tmp_ents[label]
            
            df.fillna('', inplace=True)
            if self._has_address:
                df = self._post_process_address_df(df,drop) #Post processing the dataframe
            else: 
                df = self._post_process_non_address_df(df)  #Post processing the dataframe
            # df.to_csv(f'{output_path}/output.csv')
            return df.reset_index(drop='True')
        else:
             return logging.error("Model needs to be fitted, before extraction.")

    def show_results(self, ds_type='valid'):
        """
        Runs entity extraction on a random batch from the mentioned ds_type.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        ds_type                 Optional string, defaults to valid. 
        =====================   ===========================================
        
        :returns: Pandas DataFrame
        """

        if not self._trained:
            return logging.warning('This model has not been trained')
        '''
        Make predictions on a batch of documents from specified ds_type.
        ds_type:['valid'|'train] 
        '''
        # if self._address_tag not in self.entities and self._has_address == True:
        #     return logging.warning('Model\'s address tag does not match with any field in your data, one of the below steps could resolve your issue:\n\
        #         1. Set address tag to the address field in your data [your_model._address_tag=\'your_address_field\']\n\
        #         2. If your data does not have any address field set _has_address=False [your_model._has_address=False]')

        if ds_type.lower() == 'valid':
            xs = self.val_ds._random_batch(self.val_ds.x)
            return self.extract_entities(xs)
        elif ds_type.lower() == 'train':
            xs = self.train_ds._random_batch(self.train_ds.x)
            return self.extract_entities(xs)
        else:
            print('Please provide a valid ds_type:[\'valid\'|\'train\']')