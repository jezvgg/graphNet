from keras import layers
from Src.Nodes import Layer


layers_list = {
    "Full": [
        Layer(layers.Dense, annotations={
            "units": int,
            "activation": str,
            "use_bias": bool
        })
    ],
    "Convolutional": [
        Layer(layers.Conv2D, annotations={
            "filters": int,
            "kernel_size": int,
            "strides": int,
            "padding": str,
            "activation": str,
            "use_bias": bool 
        }),
        Layer(layers.MaxPooling2D, annotations={
            "pool_size": (int, int),
            "strides": int,
            "padding": str
        })
    ],
    "Etc": [
        Layer(layers.Concatenate, annotations={}),
        Layer(layers.Flatten, annotations={}),
        Layer(layers.Add, annotations={})
    ]
    }