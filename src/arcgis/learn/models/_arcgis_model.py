HAS_FASTAI = True
try:
    from fastai.callbacks import TrackerCallback, EarlyStoppingCallback, LearnerCallback
    from torch import nn
    import torch
    from torchvision import models
    import math
except ImportError:
    HAS_FASTAI = False
    class TrackerCallback():
        pass
    class LearnerCallback():
        pass
    
import arcgis
from pathlib import Path
import os
import tempfile
import logging
from .._data import _raise_fastai_import_error
logger = logging.getLogger()

#For lr computation, skip beginning and trailing values.
losses_skipped = 5
trailing_losses_skipped = 5

class _MultiGPUCallback(LearnerCallback):
    """
    Parallize over multiple GPUs only if multiple GPUs are present.
    """
    def __init__(self, learn):
        super(_MultiGPUCallback, self).__init__(learn)
        
        self.multi_gpu = torch.cuda.device_count() > 1

    def on_train_begin(self, **kwargs):
        if self.multi_gpu:
            logger.info('Training on multiple GPUs')
            self.learn.model = nn.DataParallel(self.learn.model)
    
    def on_train_end(self, **kwargs):
        if self.multi_gpu:
            self.learn.model = self.learn.model.module

def _set_multigpu_callback(model):
    model.learn.callback_fns.append(_MultiGPUCallback)


def _create_zip(zipname, path):
    import shutil
    if os.path.exists(os.path.join(path, zipname) + '.dlpk'):
        os.remove(os.path.join(path, zipname) + '.dlpk')
        
    temp_dir = tempfile.TemporaryDirectory().name    
    zip_file = shutil.make_archive(os.path.join(temp_dir, zipname), 'zip', path)
    dlpk_base = os.path.splitext(zip_file)[0]
    os.rename(zip_file, dlpk_base + '.dlpk')
    dlpk_file = dlpk_base+'.dlpk'
    shutil.move(dlpk_file, path)


class SaveModelCallback(TrackerCallback):

    def __init__(self, model, every='improvement', load_best_at_end=True, **kwargs):
        super().__init__(learn=model.learn, **kwargs)
        self.model = model
        self.every = every
        self.name = tempfile.NamedTemporaryFile().name
        self.load_best_at_end = load_best_at_end
        if self.every not in ['improvement', 'epoch']:
            warn('SaveModel every {} is invalid, falling back to "improvement".'.format(self.every))
            self.every = 'improvement'

    def on_epoch_end(self, epoch, **kwargs):
        "Compare the value monitored to its best score and maybe save the model."
        if self.every == "epoch": self.model.save('{}_{}'.format(self.name, epoch))
        else: #every="improvement"
            current = self.get_monitor_value()
            if current is not None and self.operator(current, self.best):
                if arcgis.env.verbose:
                    print('saving checkpoint.')
                self.best = current
                self.model._save('{}'.format(self.name), zip_files=False)

    def on_train_end(self, **kwargs):
        "Load the best model."      
        if self.every == "improvement" and self.load_best_at_end:
            self.model.load('{}'.format(self.name))
            self.model.save('{}'.format(self.name))


class ArcGISModel(object):
    
    def __init__(self, data, backbone=None, **kwargs):
        if not HAS_FASTAI:
            _raise_fastai_import_error()

        self._device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        if backbone is None:
            self._backbone = models.resnet34
        elif type(backbone) is str:
            self._backbone = getattr(models, backbone)
        else:
            self._backbone = backbone

        self._data = data

        # Declare the family of backbones to be unpacked and used by different models as supported types
        self._vgg_family = [models.vgg11.__name__, models.vgg11_bn.__name__, models.vgg13.__name__, models.vgg13_bn.__name__, 
                            models.vgg16.__name__, models.vgg16_bn.__name__, models.vgg19.__name__, models.vgg19_bn.__name__]
        self._resnet_family = [models.resnet18.__name__, models.resnet34.__name__, models.resnet50.__name__, 
                               models.resnet101.__name__, models.resnet152.__name__]
        self._densenet_family = [models.densenet121.__name__, models.densenet169.__name__, models.densenet161.__name__, 
                                 models.densenet201.__name__]

    def _check_backbone_support(self, backbone):
        "Fetches the backbone name and returns True if it is in the list of supported backbones"
        backbone_name = backbone if type(backbone) is str else backbone.__name__
        return False if backbone_name not in self.supported_backbones else True

    def lr_find(self, allow_plot=True):
        """
        Runs the Learning Rate Finder, and displays the graph of it's output.
        Helps in choosing the optimum learning rate for training the model.
        """
        self.learn.lr_find()
        from IPython.display import clear_output
        clear_output()
        lr, index = self._find_lr()
        if allow_plot:
            self._show_lr_plot(index)

        return lr

    def _show_lr_plot(self, index):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 1)
        ax.plot(
            self.learn.recorder.lrs[losses_skipped:-trailing_losses_skipped],
            self.learn.recorder.losses[losses_skipped:-trailing_losses_skipped]
        )
        ax.set_ylabel("Loss")
        ax.set_xlabel("Learning Rate")
        ax.set_xscale('log')
        ax.xaxis.set_major_formatter(plt.FormatStrFormatter('%.0e'))
        ax.plot(
            self.learn.recorder.lrs[index],
            self.learn.recorder.losses[index],
            markersize=10,
            marker='o',
            color='red'
        )

        plt.show()

    def _find_lr(self):
        losses = self.learn.recorder.losses[losses_skipped:-trailing_losses_skipped]
        lrs = self.learn.recorder.lrs[losses_skipped:-trailing_losses_skipped]

        n = len(losses)

        max_start = 0
        max_end = 0

        lds = [1] * n

        for i in range(1, n):
            for j in range(0, i):
                if losses[i] < losses[j] and lds[i] < lds[j] + 1:
                    lds[i] = lds[j] + 1
                if lds[max_end] < lds[i]:
                    max_end = i
                    max_start = max_end - lds[max_end]

        sections = (max_end - max_start) / 3
        final_index = max_start + int(sections) + int(sections/2)

        return lrs[final_index], losses_skipped + final_index

    def _get_model_metrics(self, **kwargs):
        raise NotImplementedError

    def _html_metrics(self):
        raise NotImplementedError

    def fit(self, epochs=10, lr=None, one_cycle=True, early_stopping=False, checkpoint=True, **kwargs):
        """
        Train the model for the specified number of epocs and using the
        specified learning rates
        
        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        epochs                  Required integer. Number of cycles of training
                                on the data. Increase it if underfitting.
        ---------------------   -------------------------------------------
        lr                      Required float or slice of floats. Learning rate
                                to be used for training the model. Select from
                                the `lr_find` plot.
        ---------------------   -------------------------------------------
        one_cycle               Optional boolean. Parameter to select 1cycle
                                learning rate schedule. If set to `False` no 
                                learning rate schedule is used.       
        ---------------------   -------------------------------------------
        early_stopping          Optional boolean. Parameter to add early stopping.
                                If set to `True` training will stop if validation
                                loss stops improving for 5 epochs.        
        ---------------------   -------------------------------------------
        checkpoint              Optional boolean. Parameter to save the best model
                                during training. If set to `True` the best model 
                                based on validation loss will be saved during 
                                training.
        =====================   ===========================================
        """
        if lr is None:
            if arcgis.env.verbose:
                logger.info('Finding optimum learning rate.')

            lr = self.lr_find(allow_plot=False)
            lr = slice(lr/10, lr)

        self._learning_rate = lr

        if arcgis.env.verbose:
            logger.info('Fitting the model.')        
        callbacks = kwargs['callbacks'] if 'callbacks' in kwargs.keys() else []
        kwargs.pop('callbacks', None)
        if early_stopping:
            callbacks.append(EarlyStoppingCallback(learn=self.learn, monitor='valid_loss', min_delta=0.01, patience=5))
        if checkpoint:
            callbacks.append(SaveModelCallback(self, monitor='valid_loss', every='improvement'))

        if one_cycle:
            self.learn.fit_one_cycle(epochs, lr, callbacks=callbacks, **kwargs)
        else:
            self.learn.fit(epochs, lr, callbacks=callbacks, **kwargs)
        
    def unfreeze(self):
        """
        Unfreezes the earlier layers of the model for fine-tuning.
        """
        self.learn.unfreeze()

    def _create_emd(self, path):
        self._emd_template = {
            'ModelFile': path.name,
            'ImageHeight': self._data.chip_size,
            'ImageWidth': self._data.chip_size,
            'ModelParameters': {'backbone': self._backbone.__name__}
        }

        resize_to = None
        if hasattr(self._data, 'resize_to') and self._data.resize_to:
            resize_to = self._data.resize_to

        self._emd_template['resize_to'] = resize_to

    def _create_html(self, path_model):
        import matplotlib.pyplot as plt
        import base64
        plot_losses_png = self.learn.recorder.plot_losses()
        plot_losses_dir = tempfile.NamedTemporaryFile().name + '.png'
        plt.savefig(plot_losses_dir)
        plt.close()
        show_results_png = self.show_results()
        show_results_dir = tempfile.NamedTemporaryFile().name + '.png'
        plt.savefig(show_results_dir)
        plt.close()
        encoded_losses_img = base64.b64encode(open(plot_losses_dir, 'rb').read()).decode('utf-8')
        encoded_losses_img = "data:image/png;base64,{0}".format(encoded_losses_img)
        encoded_sresults_img = base64.b64encode(open(show_results_dir, 'rb').read()).decode('utf-8')
        encoded_sresults_img = "data:image/png;base64,{0}".format(encoded_sresults_img)
        html_file_path = os.path.join(path_model.parent,'model_metrics.html')
        model_type, model_analysis = self._html_metrics() 
        fil = open(html_file_path,'w')
        HTML_TEMPLATE = f"""        
                <p><b> {model_type} </b></p>
                <p><b>Backbone:</b> {self._backbone.__name__}</p>
                <p><b>Learning Rate:</b> {self._learning_rate}</p>
                <p><b>Training and Validation loss</b></p>
                <img src="{encoded_losses_img}" alt="training and validation losses">
                <p><b>Analysis of the model</b></p>
                {model_analysis}
                <p><b>Sample Results</b></p>
                <img src="{encoded_sresults_img}" alt="Sample Results">
        """
        fil.write(HTML_TEMPLATE)
        fil.close()
        return HTML_TEMPLATE

    def _save(self, name_or_path, framework='PyTorch', zip_files=True, **kwargs):
        temp = self.learn.path

        if '\\' in name_or_path or '/' in name_or_path:
            path = Path(name_or_path)
            name = path.parts[-1]
            # to make fastai save to both path and with name    
            self.learn.path = path
            self.learn.model_dir = ''
            if not os.path.exists(self.learn.path):
                os.makedirs(self.learn.path)
        else:
            # fixing fastai bug
            self.learn.path = self.learn.path.parent
            self.learn.model_dir =  Path(self.learn.model_dir) /  name_or_path
            if not os.path.exists(self.learn.path / self.learn.model_dir):
                os.makedirs(self.learn.path / self.learn.model_dir)
            name = name_or_path

        try:
            saved_path = self.learn.save(name,  return_path=True)
            # undoing changes to self.learn.path
        except Exception as e:  
            raise e
        finally:
            self.learn.path = temp
            self.learn.model_dir = 'models'

        if framework.lower() == "tf-onnx":
            if kwargs['batch_size'] is None:
                batch_size = 16
            else:
                batch_size = kwargs['batch_size']

            self._save_as_tfonnx(saved_path, batch_size)
            zip_name = self._create_tfonnx_emd(saved_path.with_suffix('.onnx'), batch_size)
            os.remove(saved_path.with_suffix('.pth'))
        else:
            zip_name = self._create_emd(saved_path)
            html_string = self._create_html(saved_path)     

        with open(saved_path.parent / self._emd_template['InferenceFunction'], 'w') as f:
            f.write(self._code)
        if zip_files:
            _create_zip(str(zip_name), str(saved_path.parent))
        if arcgis.env.verbose:
            print('Created model files at {spp}'.format(spp=saved_path.parent))

        return saved_path.parent

    def _save_as_tfonnx(self, saved_path, batch_size):
        try:
            import onnx
            from onnx_tf.backend import prepare
        except:
            raise Exception('Tensorflow(version 1.13.1 or above), Onnx(version 1.5.0) and Onnx_tf(version 1.3.0) libraries are not installed. Install Tensorflow using "conda install tensorflow-gpu=1.13.1". Install onnx and onnx_tf using "pip install onnx onnx_tf".')

        batch_size = int(math.sqrt(int(batch_size)))**2
        dummy_input = torch.randn(batch_size, 3, self._data.chip_size, self._data.chip_size, device=self._device, requires_grad=True)
        torch.onnx.export(self.learn.model, dummy_input, saved_path.with_suffix('.onnx'))

    def save(self, name_or_path, framework='PyTorch', **kwargs):
        """
        Saves the model weights, creates an Esri Model Definition and Deep
        Learning Package zip for deployment to Image Server or ArcGIS Pro
        Train the model for the specified number of epocs and using the
        specified learning rates.
        
        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        name_or_path            Required string. Name of the model to save. It
                                stores it at the pre-defined location. If path
                                is passed then it stores at the specified path
                                with model name as directory name. and creates
                                all the intermediate directories.
        ---------------------   -------------------------------------------
        framework               Optional string. Defines the framework of the
                                model. Framework can be PyTorch or TF-ONNX.
                                If framework used is TF-ONNX, batch_size has
                                to be passed as keyword arguments. Default
                                batch_size is 16.
        =====================   ===========================================
        """        
        return self._save(name_or_path, framework=framework, **kwargs)
        
    def load(self, name_or_path):
        """
        Loads a saved model for inferencing or fine tuning from the specified
        path or model name.
        
        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        name_or_path            Required string. Name of the model to load from
                                the pre-defined location. If path is passed then
                                it loads from the specified path with model name
                                as directory name. Path to ".pth" file can also
                                be passed
        =====================   ===========================================
        """
        temp = self.learn.path
        if '\\' in name_or_path or '/' in name_or_path:
            path = Path(name_or_path)
            # to make fastai from both path and with name
            if path.is_file():
                name = path.stem
                self.learn.path = path.parent
            else:
                name = path.parts[-1]
                self.learn.path = path
            self.learn.model_dir = ''
        else:
            # fixing fastai bug
            self.learn.path = self.learn.path.parent
            self.learn.model_dir =  Path(self.learn.model_dir) /  name_or_path
            name = name_or_path

        try:
            self.learn.load(name, purge=False)
        except Exception as e:
            raise e
        finally:
            # undoing changes to self.learn.path
            self.learn.path = temp
            self.learn.model_dir = 'models'
