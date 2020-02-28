import os

HAS_TENSORFLOW = False
HAS_BACKEND_SET = False
ARCGIS_ENABLE_TF_BACKEND = os.environ.get('ARCGIS_ENABLE_TF_BACKEND') is '1'

try:
    import tensorflow as tf
    HAS_TENSORFLOW = True
except:
    pass

def enable_backend():
    global HAS_BACKEND_SET
    global HAS_TENSORFLOW
    global ARCGIS_ENABLE_TF_BACKEND

    if ARCGIS_ENABLE_TF_BACKEND:
        #if tf.__version__ == '2.0.0':
        if HAS_TENSORFLOW  and not HAS_BACKEND_SET:
            try:
                tf.compat.v1.enable_eager_execution()
            except:
                pass
            tf_set_gpu_memory_growth()
            tf_sample_op()
            HAS_BACKEND_SET = True

def tf_set_gpu_memory_growth():
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            # Currently, memory growth needs to be the same across GPUs
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
            #print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
        except RuntimeError as e:
            # Memory growth must be set before GPUs have been initialized
            print(e)

def raise_tensorflow_import_error():
    message = """
    Could not find tensorflow, Please install tensorflow using the following command 
    \nconda install -c esri tensorflow-gpu=2.0.0
    """
    ex = Exception(message)
    raise(ex)

def tf_sample_op():
    a = tf.keras.layers.Conv2D(1, (3, 3))
    a = a(tf.zeros((1, 3, 224, 224)))
