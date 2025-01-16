from keras import layers
from Src.Nodes import Node


layers_list = {
    "Full": [
        Node(layers.Dense, annotations={
            "units": int,
            "activation": str,
            "use_bias": bool
        })
    ]
    }