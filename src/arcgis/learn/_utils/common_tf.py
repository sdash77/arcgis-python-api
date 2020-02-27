import tensorflow as tf
from tensorflow.keras.layers import Layer
    

## Tensorflow specific utils end ##
mean =  tf.convert_to_tensor([0.485, 0.456, 0.406], dtype=tf.float32)
std = tf.convert_to_tensor([0.229, 0.224, 0.225], dtype=tf.float32)

class NormalizationLayerRGB(Layer):
    def __call__(self, input):
        x = (input + 1. ) / 2.
        x = (x - mean) / std
        return x


