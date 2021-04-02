import traceback
from .._data import _raise_fastai_import_error
HAS_TRANSFORMER = True

try:
    from pathlib import Path
    import json
    import os
    import torch
    from transformers import pipeline, logging
    from .._utils.common import _get_device_id, _get_emd_path
    from fastprogress.fastprogress import progress_bar
    from transformers.modeling_auto import MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING
    EXPECTED_MODEL_TYPES = [x.__name__.replace('Config', '') for x in MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING.keys()]
except Exception as e:
    transformer_exception = "\n".join(traceback.format_exception(type(e), e, e.__traceback__))
    HAS_TRANSFORMER = False
    EXPECTED_MODEL_TYPES = []

class InferenceOnlyModel:

    def __init__(self):
        if 'working_dir' in self.kwargs.keys():
            self.working_dir = self.kwargs.get('working_dir')
        else:
            self.working_dir =  Path.cwd()
        self._device = _get_device_id()

    def _create_emd(self, name_or_path):
        emd_template = {}
        emd_template.update({'ModelName':self.__class__.__name__})
        emd_template.update({'architectures':self.model.model.config.architectures})
        path = Path(name_or_path)
        name = path.parts[-1]
        with open(os.path.join(path,f'{name}.emd'), 'w') as f:
            f.write(json.dumps(emd_template))

    def save(self, name_or_path):
        """
        Saves the translator model files on a specified path on the local disk.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        name_or_path            Required string. Path to save  
                                model files on the local disk.
        =====================   ===========================================
        
        :returns: Absolute path for the saved model
        """

        if '\\' in name_or_path or '/' in name_or_path:
            path = name_or_path
        else:
            path = os.path.join(self.working_dir, 'models', name_or_path)
        self.model.save_pretrained(path)
        self._create_emd(path)
        return Path(path).absolute()
    
    @classmethod
    def from_model(cls, emd_path, **kwargs):
        """
        Creates an SequenceToSequence model object from an 
        Esri Model Definition (EMD) file.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        emd_path                Required string. Path to 
                                Esri Model Definition(EMD) file or the folder 
                                with saved model files.
        =====================   ===========================================

        :returns: SequenceToSequence Object
        """
        emd_path = _get_emd_path(emd_path)
        with open(emd_path) as f:
            emd_json = json.loads(f.read())
        model_path = Path(emd_path).parent
        cls_object = cls(pretrained_path=model_path)
        return cls_object
        