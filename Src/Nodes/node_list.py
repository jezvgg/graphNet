
from typing import NamedTuple
from keras import layers
import keras
from Src.Nodes import *


listNode = NamedTuple('listNode', [("label", str), ("node_type", AbstractNode), ("kwargs", dict)])

# TODO Перевести в нормальные модели, фабрику и JSON

node_list = {
    "Neural Network Layers":
    {
        "Full":
        [
            listNode(
                label= "Dense",
                node_type= LayerNode,
                kwargs = {
                    "logic": layers.Dense,
                    "annotations": {
                        "units": int,
                        "activation": str,
                        "use_bias": bool
                    }
                }
            )
        ],
        "Convolutional":
        [
            listNode(
                label= "Conv2D",
                node_type= LayerNode,
                kwargs = {
                    "logic": layers.Conv2D,
                    "annotations": {
                        "filters": int,
                        "kernel_size": int,
                        "strides": int,
                        "padding": str,
                        "activation": str,
                        "use_bias": bool 
                    }
                }   
            ),
            listNode(
                label= "MaxPooling2D",
                node_type= LayerNode,
                kwargs = {
                    "logic": layers.MaxPooling2D,
                    "annotations": {
                        "pool_size": (int, int),
                        "strides": int,
                        "padding": str
                    }
                }
            )
        ],
        "Etc":[
            listNode(
                label="Concatenate",
                node_type= LayerNode,
                kwargs = {
                    "logic": layers.Concatenate,
                    "annotations": {}
                }
            ),
            listNode(
                label="Flatten",
                node_type= LayerNode,
                kwargs = {
                    "logic": layers.Flatten,
                    "annotations": {}
                }
            ),
            listNode(
                label="Add",
                node_type= LayerNode,
                kwargs = {
                    "logic": layers.Add,
                    "annotations": {}
                }
            )
        ]
    },
    "Training": {
        "Train": [
            listNode(
                label="Compile model",
                node_type= CompileNode,
                kwargs= {
                    "logic": keras.models.Model.compile,
                    "annotations": {}
                }
            )
        ],
        "Utils": [
            listNode(
                label="Save model",
                node_type= UtilsNode,
                kwargs= {
                    "logic": keras.saving.save_model,
                    "annotations": {
                        "model": ParameterNode,
                    }
                }
            ),
            listNode(
                label="Plot model",
                node_type= UtilsNode,
                kwargs= {
                    "logic": keras.utils.plot_model,
                    "annotations": {
                        "model": ParameterNode,
                    }
                }
            )
        ]
    }
}
