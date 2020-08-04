import os
import json
import torch
import traceback

HAS_TRANSFORMER = True

try:
    from transformers import AutoModelForSequenceClassification
    from ._arcgis_transformer import ArcGISTransformer
except Exception as e:
    transformer_exception = "\n".join(traceback.format_exception(type(e), e, e.__traceback__))
    HAS_TRANSFORMER = False

    class ArcGISTransformer:
        pass

backbone_models_map = {
    'bert': ('bert-base-cased', 'bert-base-uncased', 'bert-large-cased', 'bert-large-uncased'),
    'albert': ('albert-base-v1', 'albert-base-v2', 'albert-large-v1', 'albert-large-v2',
               'albert-xlarge-v1', 'albert-xlarge-v2', 'albert-xxlarge-v1', 'albert-xxlarge-v2'),
    'roberta': ('roberta-base', 'roberta-large', 'distilroberta-base'),
    'distilbert': ('distilbert-base-cased', 'distilbert-base-uncased'),
    'xlnet': ('xlnet-base-cased', 'xlnet-large-cased'),
    'xlm': ('xlm-mlm-ende-1024', 'xlm-mlm-enfr-1024', 'xlm-mlm-xnli15-1024', 'xlm-mlm-en-2048'),
    'flaubert': ('flaubert/flaubert_small_cased', 'flaubert/flaubert_base_cased', 'flaubert/flaubert_base_uncased',
                 'flaubert/flaubert_large_cased'),
    'xlm-roberta': ('xlm-roberta-base', 'xlm-roberta-large'),
    'longformer': ('allenai/longformer-base-4096',),
    'electra': ('google/electra-base-discriminator', 'google/electra-base-generator'),
    'bart': ('facebook/bart-base', 'facebook/bart-large'),
    'camembert': ('camembert-base',)
}

transformer_architectures = ['BERT', 'RoBERTa', 'DistilBERT', 'ALBERT', 'FlauBERT', 'CamemBERT',
                             'XLNet', 'XLM', 'XLM-RoBERTa', 'Bart', 'ELECTRA', 'Longformer']

backbone_models_reverse_map = {x:key for key, val in backbone_models_map.items() for x in val}

transformer_seq_length = 512


class TransformerForTextClassification(ArcGISTransformer):

    _supported_backbones = transformer_architectures

    def __init__(self, architecture, pretrained_model_name, config=None, pretrained_model_path=None,
                 seq_len=transformer_seq_length):
        super().__init__(architecture, pretrained_model_name, config, pretrained_model_path)
        self._seq_len = seq_len
        self._max_seq_len = None

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '<%s>' % type(self).__name__

    def _process_config(self):
        """
        Process the model config to convert the class values to integers in the
        id2label attribute (which is a dictionary) of the model config
        """
        self._config.id2label = {int(x): y for x, y in self._config.id2label.items()}

    def _set_max_seq_length(self):
        """
        Set the max-seq-len parameter to avoid out of memory issues for transformers
        like Bart, Longformer, XLNet
        """
        self._max_seq_len = min(self._tokenizer.model_max_length, self._seq_len)

    @classmethod
    def _available_backbone_models(cls, architecture):
        """
        Provides a list of available models for a given transformer architecture

        =====================   =================================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------------
        architecture            Required string. The transformer architecture for
                                which we wish to get the available models
        ---------------------   -------------------------------------------------
        return: tuple containing available models for the given architecture
        """
        if architecture.lower() in backbone_models_map:
            return backbone_models_map[architecture.lower()]
        else:
            return f"Error, wrong architecture name - {architecture} supplied. " \
                   f"PLease choose from {cls._supported_backbones}"

    def save(self, model_path):
        """
        Method to save the fine-tuned model to the disk

        =====================   =================================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------------
        model_path              Required string. The disk location where the
                                fine-tuned model has to be saved
        ---------------------   -------------------------------------------------
        """
        if not os.path.exists(model_path):
            os.mkdir(model_path)
        model_params = {"architecture": self._transformer_architecture,
                        "pretrained_model": self._transformer_pretrained_model_name}
        file_path = os.path.join(model_path, self._outfile)
        out_file = open(file_path, "w")
        json.dump(model_params, out_file)
        self._transformer.save_pretrained(model_path)
        # self._tokenizer.save_pretrained(model_path)

    @classmethod
    def load_pretrained_model(cls, path):
        """
        Method to load the fine-tuned model which was saved on the disk

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        path                    Required string. The disk location from
                                where the fine-tuned model has to be loaded
        ---------------------   -------------------------------------------
        """
        architecture_file_path = os.path.join(path, cls._outfile)
        if os.path.exists(architecture_file_path):
            with open(architecture_file_path) as f:
                data = json.load(f)
            architecture = data.get("architecture")
            pretrained_model_name = data.get("pretrained_model")
            obj = TransformerForTextClassification(architecture, pretrained_model_name, pretrained_model_path=path)
            obj.init_model()
            return obj
        else:
            raise Exception(f"{cls._outfile} not present at {path}")

    def forward(self, input_ids, **kwargs):
        """
        Return only the logits from the transfomer model

        =====================   ==============================================
        **Argument**            **Description**
        ---------------------   ----------------------------------------------
        input_ids               tensor object. tensor containing the token-ids
                                got by calling tokenizer.encode method to the
                                input text. works same for mini-batches
        ---------------------   ----------------------------------------------

        :return: the logits from the transformer model
        """
        logits = self._transformer(input_ids)[0]
        return logits

    def _load_transformer(self):
        """
        Method to load the transformer model. For this class we want to load the
        transformer model for performing Sequence Classification tasks
        """
        if self._pretrained_model_path and os.path.exists(self._pretrained_model_path):
            self._transformer = AutoModelForSequenceClassification.from_pretrained(self._pretrained_model_path)
        else:
            self._transformer = AutoModelForSequenceClassification.\
                from_pretrained(self._transformer_pretrained_model_name, config=self._config)

    def predict_class(self, text, is_multilabel_problem=False, thresh=None):
        """
        Method to predict the class labels for an input text

        =====================   ==============================================
        **Argument**            **Description**
        ---------------------   ----------------------------------------------
        text                    Required string. The text for which we wish to
                                predict the class
        ---------------------   ----------------------------------------------

        :return: the predicted label and the corresponding confidence score.
        """
        device_type = next(self._transformer.parameters()).device.type
        device = torch.device("cuda:0" if device_type == "cuda" else "cpu")
        sequence = torch.tensor([self._tokenizer.encode(text, max_length=self._max_seq_len)]).to(device)
        logits = self._transformer(sequence)[0]
        if is_multilabel_problem:
            results = torch.sigmoid(logits)[0]
            category, raw_pred = [], []
            for idx, x in enumerate(results):
                pred = 0
                if x.item() > thresh:
                    pred = 1
                    category.append(self._config.id2label[idx])
                raw_pred.append(pred)
            return ";".join(category), raw_pred, [round(x, 4) for x in results.tolist()]
        else:
            results = torch.softmax(logits, dim=1)[0]
            clas = self._config.id2label[torch.argmax(logits, dim=1)[0].item()]
            score = results[torch.argmax(logits, dim=1)[0]]
            return clas, score.item()
