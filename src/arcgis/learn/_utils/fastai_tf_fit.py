

try:
    import tensorflow as tf
    HAS_TENSORFLOW = True
except:
    HAS_TENSORFLOW = False

try:
    from fastai.basics import *
    HAS_FASTAI = True
except:
    HAS_FASTAI = False


__all__ = ['_tf_to_pytorch', '_pytorch_to_tf', 'TfLearner', 'tf_fit', 'tf_loss_batch', 'tf_train_epoch', 'tf_validate', 'tf_get_preds', 'TfOptimWrapper', 'TfRegularizer', 'tf', 'tf_lr_find', 'TfLRFinder']

if HAS_FASTAI and HAS_TENSORFLOW:
        
    defaults.device = torch.device('cpu')

    try:
        #tf.enable_eager_execution()
        tf.compat.v1.enable_eager_execution()
        # check by tf.executing_eagerly()
    except:
        pass

    tf_flatten_model=lambda m: sum(map(tf_flatten_model,m.layers),[]) if hasattr(m, "layers") else [m]

    tf_bn_types = (tf.keras.layers.BatchNormalization,)

    tf.Tensor.detach = lambda x: x
    tf.Tensor.cpu = lambda x: x.numpy()
    tf.Tensor.item = lambda x: x.numpy()
    tf.Tensor.size = lambda x, axis: tf.shape(x)[axis].numpy()

# Activation function for losses
def noop(x): return x

def _loss_func2activ(loss_func):
    return noop

def _pytorch_to_tf(var):
    if not is_listy(var): 
        return tf.constant(var.cpu().numpy())
    else: 
        return [tf.constant(v.cpu().numpy()) for v in var]

def _pytorch_to_tf_batch(var):
    if tf.keras.backend.image_data_format() == 'channels_last':
        _var = var.permute((0, 2, 3, 1))
    else:
        _var = var
    return _pytorch_to_tf(_var)

def _tf_to_pytorch(var):
    if not is_listy(var): 
        return torch.tensor(var.numpy())
    else: 
        return [torch.tensor(v.numpy()) for v in var]

def tf_loss_batch(model, xb, yb, loss_func=None, opt=None, cb_handler=None):
    "Calculate loss for a batch, call out to callbacks as necessary."
    cb_handler = ifnone(cb_handler, CallbackHandler())
    if not is_listy(xb): 
        xb = [xb]
    if not is_listy(yb): 
        yb = [yb]

    def forward():
        out = model(*xb, training=True)
        out = cb_handler.on_loss_begin(out)
        return out

    def forward_calc_loss():
        out = forward()
        loss = loss_func(*yb, out) #reversed params compared to pytorch
        loss, skip_bwd = cb_handler.on_backward_begin(loss)
        return loss
    
    if not loss_func: 
        return forward(), yb[0]
        
    loss = None
    if opt is not None:
        with tf.GradientTape() as tape:
            loss = forward_calc_loss()
            grads = tape.gradient(loss, model.trainable_variables)
        cb_handler.on_backward_end()
        opt.apply_gradients(zip(grads, model.trainable_variables))
        cb_handler.on_step_end()
    else:
        loss = forward_calc_loss()
        
    return loss.numpy()

def calc_loss(predictions, ground_truth, loss_func):
    loss = loss_func(ground_truth, predictions, reduction=False)
    return _tf_to_pytorch(loss)

def tf_get_preds(model, dl, pbar=None, cb_handler=None, activ=None, loss_func=None, n_batch=None):
    "Tuple of predictions and targets, and optional losses (if `loss_func`) using `dl`, max batches `n_batch`."
    res = [np.concatenate(o) for o in
           zip(*tf_validate(model, dl, cb_handler=cb_handler, pbar=pbar, average=False, n_batch=n_batch))]
    if loss_func is not None: 
        res.append(calc_loss(res[0], res[1], loss_func))
    if activ is not None: 
        res[0] = activ(res[0])
    res[0] = torch.tensor(res[0])
    res[1] = torch.tensor(res[1])
    return res
    
    
def tf_validate(model, dl, loss_func=None, cb_handler=None, pbar=None, average=True, n_batch=None):
    "Calculate `loss_func` of `model` on `dl` in evaluation mode."
    val_losses,nums = [],[]
    for xb,yb in progress_bar(dl, parent=pbar, leave=(pbar is not None)):
        xb, yb = _pytorch_to_tf_batch(xb), _pytorch_to_tf(yb)
        if cb_handler: xb, yb = cb_handler.on_batch_begin(xb, yb, train=False)
        val_losses.append(tf_loss_batch(model, xb, yb, loss_func, cb_handler=cb_handler))
        if not is_listy(yb): 
            yb = [yb]
        nums.append(yb[0].size(0))
        if cb_handler and cb_handler.on_batch_end(val_losses[-1]): 
            break
        if n_batch and (len(nums)>=n_batch): 
            break
    nums = np.array(nums, dtype=np.float32)
    if average: 
        return (np.stack(val_losses) * nums).sum() / nums.sum()
    else:       
        return val_losses


def tf_train_epoch(model, dl, opt, loss_func):
    "Simple training of `model` for 1 epoch of `dl` using optim `opt` and loss function `loss_func`."
    for xb,yb in dl:
        xb, yb = _pytorch_to_tf(xb), _pytorch_to_tf(yb)
        if not is_listy(xb): 
            xb = [xb]
        if not is_listy(yb): 
            yb = [yb]
        with tf.GradientTape() as tape:
            out = model(*xb)
            loss = loss_func(*yb, out) #reversed params compared to pytorch

        grads = tape.gradient(loss, model.trainable_weights)
        opt.apply_gradients(zip(grads, model.trainable_weights))

def tf_fit(epochs, model, loss_func, opt, data, callbacks, metrics):
    cb_handler = CallbackHandler(callbacks, metrics)
    pbar = master_bar(range(epochs))
    cb_handler.on_train_begin(epochs, pbar=pbar, metrics=metrics)

    exception=False
    try:
        for epoch in pbar:
            cb_handler.on_epoch_begin()

            for xb,yb in progress_bar(data.train_dl, parent=pbar):
                xb, yb = _pytorch_to_tf_batch(xb), _pytorch_to_tf(yb)
                xb, yb = cb_handler.on_batch_begin(xb, yb)
                loss = tf_loss_batch(model, xb, yb, loss_func, opt, cb_handler)
                if cb_handler.on_batch_end(loss):
                    break
            
            if not data.empty_val:
                val_loss = tf_validate(model, data.valid_dl, loss_func=loss_func, cb_handler=cb_handler, pbar=pbar)
            else: 
                val_loss=None
            if cb_handler.on_epoch_end(val_loss): 
                break
    except Exception as e:
        exception = e
        raise e
    finally: cb_handler.on_train_end(exception)

    
@dataclass
class TfLearner():
    "Train `model` using `data` to minimize `loss_func` with optimizer `opt_func`."
    data:DataBunch
    model:tf.keras.Model
    opt_func:Callable
    loss_func:Callable
    metrics:Collection[Callable]=None
    true_wd:bool=True
    bn_wd:bool=True
    wd:float=defaults.wd
    train_bn:bool=True
    path:str=None
    model_dir:str='models'
    callback_fns:Collection[Callable]=None
    callbacks:Collection[Callback]=field(default_factory=list)
    layer_groups:Collection[tf.keras.layers.Layer]=None
    def __post_init__(self)->None:
        "Setup path,metrics, callbacks and ensure model directory exists."
        self.path = Path(ifnone(self.path, self.data.path))
        (self.path/self.model_dir).mkdir(parents=True, exist_ok=True)
        self.metrics=listify(self.metrics)
        if not self.layer_groups: 
            self.layer_groups = tf_flatten_model(self.model)
        self.callbacks = listify(self.callbacks)
        self.callback_fns = [Recorder] + [TfRegularizer] + listify(self.callback_fns)
        
        #build the model by running 1 batch
        xb, yb = next(iter(self.data.train_dl))
        xb, yb = _pytorch_to_tf_batch(xb), _pytorch_to_tf(yb)
        tf_loss_batch(self.model, xb, yb)

    def init(self, init): 
        raise NotImplementedError

    def lr_range(self, lr:Union[float,slice])->np.ndarray:
        "Build differential learning rates."
        if not isinstance(lr,slice): 
            return lr
        if lr.start: 
            res = even_mults(lr.start, lr.stop, len(self.layer_groups))
        else: 
            res = [lr.stop/10]*(len(self.layer_groups)-1) + [lr.stop]
        return np.array(res)

    def fit(self, epochs:int, lr:Union[Floats,slice]=defaults.lr,
            wd:Floats=None, callbacks:Collection[Callback]=None)->None:
        "Fit the model on this learner with `lr` learning rate, `wd` weight decay for `epochs` with `callbacks`."
        lr = self.lr_range(lr)
        if wd is None: wd = self.wd

        self.create_opt(lr, wd)
        callbacks = [cb(self) for cb in self.callback_fns] + listify(callbacks)      
        tf_fit(epochs, self.model, self.loss_func, opt=self.opt, data=self.data, metrics=self.metrics,
            callbacks=self.callbacks+callbacks)

    def create_opt(self, lr:Floats, wd:Floats=0.)->None:
        "Create optimizer with `lr` learning rate and `wd` weight decay."
        self.opt = TfOptimWrapper.create(self.opt_func, lr, wd, self.layer_groups)

    def freeze_to(self, n:int)->None:
        "Freeze layers up to layer `n`."
        for l in self.layer_groups[:n]: 
            if not self.train_bn or not ( isinstance(l, bn_types) or 'BatchNormalization' in l.__class__.__name__ ): 
                l.trainable = False
        for l in self.layer_groups[n:]: 
            l.trainable = True

    def freeze(self)->None:
        "Freeze up to last layer."
        assert(len(self.layer_groups)>1)
        self.freeze_to(-1)

    def unfreeze(self):
        "Unfreeze entire model."
        self.freeze_to(0)

    def __del__(self): del(self.model, self.data)

    def save(self, name:PathOrStr, return_path=True):
        "Save model with `name` to `self.model_dir`."
        root = tf.train.Checkpoint(model=self.model)
        model_save_path = self.path/self.model_dir/f'{name}'
        root.save(file_prefix=model_save_path)
        if return_path:
            return model_save_path

    def _save_keras_model(self, name:PathOrStr, return_path=True, model_to_save=None):
        "Save model with `name` to `self.model_dir`."
        model_save_path = self.path/self.model_dir/f'{name}'
        # if not os.path.exists(model_save_path):
        #     os.mkdir(model_save_path)
        if model_to_save is None:
            model_to_save = self.model
        model_to_save.save(str(os.path.abspath(model_save_path)))
        if return_path:
            return model_save_path

    def _save_tflite(self, name:PathOrStr, return_path=True, model_to_save=None, quantized=False, data=None):
        "Save model with `name` to `self.model_dir`."
        
        if model_to_save is None:
            model_to_save = self.model

        if quantized:
            #
            # Have to first save to keras model and then quantize model using 
            # compatible API V1 because model quantization does not work in TF 2.0.0
            # https://github.com/tensorflow/tensorflow/issues/36610 and other issues
            #
            keras_model_path = self._save_keras_model(name, return_path=True, model_to_save=model_to_save)
            
            # Get Representative dataset
            num_calibration_steps = min((round(len(data.x) / data.batch_size) - 1), 256)
            iterator = iter(data.train_dl)
            x_batch = []
            for i in range(round(num_calibration_steps / data.batch_size)):
                xb, yb = next(iterator)
                x_batch.append(xb)
            x_batch = torch.cat(x_batch).permute(0, 2, 3, 1).cpu().numpy()
            def representative_dataset_gen():
                for i in range(num_calibration_steps):
                    # Get sample input data as a numpy array in a method of your choosing.
                    im = x_batch[i][None]
                    yield [im]

            converter = tf.compat.v1.lite.TFLiteConverter.from_keras_model_file(str(os.path.abspath(keras_model_path)))
            converter.representative_dataset = representative_dataset_gen
            converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
            converter.inference_input_type = tf.uint8
            converter.inference_output_type = tf.uint8
        else:
            converter = tf.lite.TFLiteConverter.from_keras_model(model_to_save)
        #
        #converter.optimizations = [tf.lite.Optimize.DEFAULT]
        tflite_model = converter.convert()
        model_save_path = self.path/self.model_dir/f'{name}.tflite'
        with open(model_save_path, "wb") as m:
            m.write(tflite_model)
        return model_save_path

    def dl(self, ds_type:DatasetType=DatasetType.Valid):
        "Return DataLoader for DatasetType `ds_type`."
        return self.data.dl(ds_type)
        
    def load(self, name:PathOrStr, purge=False):
        "Load model `name` from `self.model_dir`."
        root = tf.train.Checkpoint(model=self.model)
        root.restore(str(self.path/self.model_dir/f'{name}-1'))
    
    def get_preds(self, ds_type:DatasetType=DatasetType.Valid, with_loss:bool=False, n_batch:Optional[int]=None, pbar:Optional[PBar]=None) -> List[Tensor]:
        "Return predictions and targets on `ds_type` dataset."
        lf = self.loss_func if with_loss else None
        return tf_get_preds(self.model, self.dl(ds_type), cb_handler=CallbackHandler(self.callbacks),
                         activ=_loss_func2activ(self.loss_func), loss_func=lf, n_batch=n_batch, pbar=pbar)

    def pred_batch(self, ds_type:DatasetType=DatasetType.Valid, batch:Tuple=None, reconstruct:bool=False, with_dropout:bool=False) -> List[Tensor]:
        if batch is not None:
            xb, yb = batch
        else:
            _xb, _yb = self.data.one_batch(ds_type, detach=False, denorm=False)
        cb_handler = CallbackHandler(self.callbacks)
        xb,yb = cb_handler.on_batch_begin(xb, yb, train=False)
        #activ = ifnone(activ, _loss_func2activ(self.loss_func))
        with torch.no_grad():
            if not with_dropout: 
                preds = tf_loss_batch(self.model, _pytorch_to_tf_batch(xb), yb, cb_handler=cb_handler)
            else: 
                preds = tf_loss_batch(self.model.eval().apply(self.apply_dropout), xb, yb, cb_handler=cb_handler)
            #res = activ(preds[0])
            res = _tf_to_pytorch(preds[0])
        if not reconstruct: 
            return res
        res = res.detach().cpu()
        ds = self.dl(ds_type).dataset
        norm = getattr(self.data, 'norm', False)
        if norm and norm.keywords.get('do_y',False):
            res = self.data.denorm(res, do_x=True)
        return [ds.reconstruct(o) for o in res]

    def backward(self, item):
        raise NotImplementedError
    def predict(self, item:ItemBase, **kwargs):
        raise NotImplementedError
    def validate(self, dl=None, callbacks=None, metrics=None):
        raise NotImplementedError
    def show_results(self, ds_type=DatasetType.Valid, rows:int=5, **kwargs):
        raise NotImplementedError      

        
class TfLRFinder(LearnerCallback):
    "Causes `learn` to go on a mock training from `start_lr` to `end_lr` for `num_it` iterations."
    def __init__(self, learn:Learner, start_lr:float=1e-7, end_lr:float=10, num_it:int=100, stop_div:bool=True):
        super().__init__(learn)
        self.data,self.stop_div = learn.data,stop_div
        self.sched = Scheduler((start_lr, end_lr), num_it, annealing_exp)
        #To avoid validating if the train_dl has less than num_it batches, we put aside the valid_dl and remove it
        #during the call to fit.
        import copy
        self.valid_dl = copy.deepcopy(learn.data.valid_dl)
        self.data.valid_dl = None

    def on_train_begin(self, pbar, **kwargs:Any)->None:
        "Initialize optimizer and learner hyperparameters."
        setattr(pbar, 'clean_on_interrupt', True)
        self.learn.save('tmp')
        self.opt = self.learn.opt
        self.opt.lr = self.sched.start
        self.stop,self.best_loss = False,0.
        return {'skip_validate': True}

    def on_batch_end(self, iteration:int, smooth_loss:TensorOrNumber, **kwargs:Any)->None:
        "Determine if loss has runaway and we should stop."
        if iteration==0 or smooth_loss < self.best_loss: 
            self.best_loss = smooth_loss
        self.opt.lr = self.sched.step()
        if self.sched.is_done or (self.stop_div and (smooth_loss > 4*self.best_loss or tf.math.is_nan(smooth_loss))):
            #We use the smoothed loss to decide on the stopping since it's less shaky.
            return {'stop_epoch': True, 'stop_training': True}

    def on_train_end(self, **kwargs:Any)->None:
        "Cleanup learn model weights disturbed during LRFind exploration."
        # restore the valid_dl we turned off on `__init__`
        self.data.valid_dl = self.valid_dl
        self.learn.load('tmp')
        if hasattr(self.learn.model, 'reset'): self.learn.model.reset()
        for cb in self.callbacks:
            if hasattr(cb, 'reset'): cb.reset()
        print('LR Finder is complete, type {learner_name}.recorder.plot() to see the graph.')
        
def tf_lr_find(learn:Learner, start_lr:Floats=1e-7, end_lr:Floats=10, num_it:int=100, stop_div:bool=True, **kwargs:Any):
    "Explore lr from `start_lr` to `end_lr` over `num_it` iterations in `learn`. If `stop_div`, stops when loss diverges."
    start_lr = learn.lr_range(start_lr)
    start_lr = np.array(start_lr) if is_listy(start_lr) else start_lr
    end_lr = learn.lr_range(end_lr)
    end_lr = np.array(end_lr) if is_listy(end_lr) else end_lr
    cb = TfLRFinder(learn, start_lr, end_lr, num_it, stop_div)
    a = int(np.ceil(num_it/len(learn.data.train_dl)))
    learn.fit(a, start_lr, callbacks=[cb], **kwargs)    

TfLearner.fit_one_cycle = fit_one_cycle
TfLearner.lr_find = tf_lr_find


class TfOptimWrapper():
    def __init__(self, opt_func, layer_groups):
        self.layer_groups = layer_groups
        self._lr = [tf.Variable(0.0) for o in layer_groups]
        self._mom = tf.Variable(0.0)
        self._wd = 0.0
    
        opt_params = inspect.signature(opt_func).parameters
        params = {}
        if opt_params.get("momentum"):
            self.mom = opt_params.get("momentum").default
            params["momentum"] = self._mom
        if opt_params.get("beta1"):
            self.mom = opt_params.get("beta1").default
            params["beta1"] = self._mom
        
        self.opt = [opt_func(learning_rate=o, **params) for o in self._lr]
        
    @classmethod
    def create(cls, opt_func, lr, wd, layer_groups, **kwargs):
        opt = cls(opt_func, layer_groups,  **kwargs)
        opt.lr = lr
        opt.wd = wd
        return opt
    
    #requires grads and vars of only trainable layers 
    def apply_gradients(self, grads_and_vars):
        for l, opt in zip(self.layer_groups, self.opt):
            for i in range(len(l.trainable_weights)):
                opt.apply_gradients([next(grads_and_vars)])
        
    @property
    def lr(self)->float:
        "Get learning rate."
        return self._lr[-1].numpy()

    @lr.setter
    def lr(self, val:float)->None:
        "Set learning rate."
        val = listify(val, self._lr)
        for o, v in zip(self._lr, val): o.assign(v) 

    @property
    def mom(self)->float:
        "Get momentum."
        return self._mom.numpy()

    @mom.setter
    def mom(self, val:float)->None:
        "Set momentum."
        if not isinstance(val, float): val = val[-1]
        self._mom.assign(val)
        
    @property
    def wd(self)->float:
        "Get wd."
        return self._wd

    @wd.setter
    def wd(self, val:float)->None:
        "Set wd."
        self._wd = val

class TfRegularizer(LearnerCallback):
    def __init__(self, learn:Learner):
        super().__init__(learn)

    def on_backward_begin(self, last_loss, **kwargs):
        if not self.learn.true_wd:
            regularizer = sum([tf.nn.l2_loss(w) for w in self.learn.model.weights])
            return last_loss + self.learn.wd * regularizer

    def on_backward_end(self, **kwargs):
        if self.learn.true_wd:
            opt = self.learn.opt
            for lr, l in zip(opt._lr, opt.layer_groups):
                if l.trainable:
                    if self.learn.bn_wd or not isinstance(l, tf_bn_types):
                        for w in l.weights: w=w*lr*opt.wd