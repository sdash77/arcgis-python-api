from ._codetemplate import image_translation_prf
import json
import traceback
from .._data import _raise_fastai_import_error
from ._arcgis_model import ArcGISModel
try:
    from ._pix2pix_utils import pix2pixLoss, pix2pixTrainer, optim, compute_fid_metric
    from ._pix2pix_utils import  pix2pix as pix2pix_model
    from .._utils.pix2pix import ImageTuple, ImageTupleList2
    from torchvision import transforms
    from pathlib import Path
    from fastai.vision import *
    from fastai.vision import DatasetType, Learner, partial, open_image
    import torch

    HAS_FASTAI = True
except Exception as e:
    import_exception = "\n".join(traceback.format_exception(type(e), e, e.__traceback__))
    HAS_FASTAI = False

class Pix2Pix(ArcGISModel):

    """
    Creates a model object which generates fake images of type B from type A.

    =====================   ===========================================
    **Argument**            **Description**
    ---------------------   -------------------------------------------
    data                    Required fastai Databunch. Returned data object from
                            `prepare_data` function.
    ---------------------   -------------------------------------------
    pretrained_path         Optional string. Path where pre-trained model is
                            saved.
    =====================   ===========================================
                                             
    :returns: `Pix2Pix` Object
    """
    
    def __init__(self, data, pretrained_path=None, *args, **kwargs):
        super().__init__(data)

        pix2pix_gan = pix2pix_model(3,3)

        self.learn = Learner(data, 
                             pix2pix_gan, 
                             loss_func=pix2pixLoss(pix2pix_gan), 
                             opt_func=partial(optim.Adam,betas=(0.5,0.99)),
                             callback_fns=[pix2pixTrainer])

        self.learn.model = self.learn.model.to(self._device)
        self._slice_lr = False
        
        if pretrained_path is not None:
            self.load(pretrained_path)
        self._code = image_translation_prf
        def __str__(self):
            return self.__repr__()
        def __repr__(self):
            return '<%s>' % (type(self).__name__)
        
    @classmethod
    def from_model(cls, emd_path, data=None):
        """
        Creates a Pix2Pix object from an Esri Model Definition (EMD) file.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        emd_path                Required string. Path to Esri Model Definition
                                file.
        ---------------------   -------------------------------------------
        data                    Required fastai Databunch or None. Returned data
                                object from `prepare_data` function or None for
                                inferencing.
        =====================   ===========================================
        
        :returns: `Pix2Pix` Object
        """
        
        if not HAS_FASTAI:
            _raise_fastai_import_error(import_exception=import_exception)
            
        emd_path = Path(emd_path)
        with open(emd_path) as f:
            emd = json.load(f)

        model_file = Path(emd['ModelFile'])

        if not model_file.is_absolute():
            model_file = emd_path.parent / model_file

        model_params = emd['ModelParameters']
        resize_to = emd.get('resize_to')
        chip_size = emd['ImageHeight']
        if data is None:
            data = ImageTupleList2.from_folders(emd_path.parent, emd_path.parent, emd_path.parent)\
                .split_none()\
                .label_empty()\
                .transform(size=(chip_size, chip_size))\
                .databunch(bs=2, no_check = True)
            data.n_channel = emd['n_channel']
            data._is_empty = True
            data.emd_path = emd_path
            data.emd = emd
        data.resize_to = chip_size
        
        return cls(data, **model_params, pretrained_path=str(model_file))
        
    @property
    def _model_metrics(self):
        fid = self.compute_metrics()
        return {'FID': f'{fid}'}

    def _get_emd_params(self, save_inference_file):
        _emd_template = {}
        _emd_template["Framework"] = "arcgis.learn.models._inferencing"
        _emd_template["ModelConfiguration"] = "_pix2pix"
        _emd_template["InferenceFunction"] = "ArcGISImageTranslation.py"
        _emd_template["ModelType"] = "Pix2Pix"
        _emd_template["n_channel"] = self._data.n_channel
        return _emd_template

    def show_results(self,rows=5):
        """
        Displays the results of a trained model on a part of the validation set.

        """

        self.learn.model.arcgis_results = True
        self.learn.show_results()
        self.learn.model.arcgis_results = False

    def predict(self, img_path):
        """
        Predicts and display the image.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        img_path                Required path of an image.
        =====================   ===========================================

        """
        self.learn.model.arcgis_results = True
        img_path = Path(img_path)
        raw_img = open_image(img_path)
        raw_img_tuple = ImageTuple(raw_img, raw_img)
        pred_tuple = self.learn.predict(raw_img_tuple)
        pred_img = pred_tuple[1][0]/2+0.5
        
        pred_img = transforms.ToPILImage()(pred_img).convert("RGB")
        self.learn.model.arcgis_results = False
        return pred_img

    def compute_metrics(self):
        """
        Computes Frechet Inception Distance (FID) on validation set.
        """
        fid = compute_fid_metric(self, self._data)
        return fid
