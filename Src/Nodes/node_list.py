
from typing import NamedTuple

from keras import layers
import keras

from Src.Nodes import *
from Src.Models import File


listNode = NamedTuple('listNode', [("label", str), ("node_type", AbstractNode), ("kwargs", dict)])

# TODO Перевести в нормальные модели, фабрику и JSON

node_list = {
    "Data & Preprocessing":
    {
        "Import data": [
            listNode(
                label="Tables data",
                node_type= TableDataNode,
                kwargs= {
                    "logic": TableDataNode.open_data,
                    "annotations": {
                        "files": File,
                        "skip_header": bool,
                        "skip_footer": bool
                    }
                }
            ),
            listNode(
                label="Images data",
                node_type= ImageDataNode,
                kwargs= {
                    "logic": ImageDataNode.open_data,
                    "annotations": {
                        "files": File,
                        "color_mode": str
                    }
                }
            )
        ],
        "Preprocessing Utils": [
            listNode(
                label="to categorical",
                node_type= PipelineNode,
                kwargs= {
                    "logic": keras.utils.to_categorical,
                    "annotations": {
                        "x": DataNode,
                        "num_classes": int
                    }
                }
            )
        ]
    },
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
        "General": [
            listNode(
                label="Compile model",
                node_type= CompileNode,
                kwargs= {
                    "logic": keras.models.Model.compile,
                    "annotations": {
                        "optimizer": OptimizerNode,
                        "loss": LossNode,
                        # "metrics": MetricNode
                    }
                }
            ),
            listNode(
                label="Fit model",
                node_type= FitNode,
                kwargs= {
                    "logic": keras.models.Model.fit,
                    "annotations": {
                        "self": CompileNode,
                        "x": DataNode,
                        "y": DataNode,
                        "epochs": int
                    }
                }
            )
        ],
        "Optimizers": [
            listNode(
                label="Adam",
                node_type= OptimizerNode,
                kwargs={
                    "logic": keras.optimizers.Adam,
                    "annotations": {
                        "learning_rate": float,
                        # "beta_1": float,
                        # "beta_2": float,
                        # "epsilon": float
                    },
                    "input": False
                }
            ),
            listNode(
                label="Stochastic Gradient Descent",
                node_type= OptimizerNode,
                kwargs= {
                    "logic": keras.optimizers.SGD,
                    "annotations": {
                        "learning_rate": float,
                        "momentum": float,
                        "nesterov": bool
                    },
                    "input": False
                }
            ),
            listNode(
                label="RMSprop",
                node_type= OptimizerNode,
                kwargs= {
                    "logic": keras.optimizers.RMSprop,
                    "annotations": {
                        "learning_rate": float,
                        "momentum": float
                    },
                    "input": False
                }
            )
        ],
        "Losses": [
            listNode(
                label="Binary cross-entropy",
                node_type= LossNode,
                kwargs= {
                    "logic": keras.losses.BinaryCrossentropy,
                    "annotations": {},
                    "input": False
                },
                
            ),
            listNode(
                label="Mean Squared Error",
                node_type= LossNode,
                kwargs= {
                    "logic": keras.losses.MeanSquaredError,
                    "annotations": {},
                    "input": False
                }
            ),
            listNode(
                label="Cross-entropy",
                node_type= LossNode,
                kwargs= {
                    "logic": keras.losses.CategoricalCrossentropy,
                    "annotations": {},
                    "input": False
                }
            ),
        ],
        "Metrics": [
            listNode(
                label="Accuracy",
                node_type= ParameterNode,
                kwargs= {
                    "logic": keras.metrics.Accuracy,
                    "annotations": {},
                    "input": False
                }
            ),
            listNode(
                label="F1 score",
                node_type= ParameterNode,
                kwargs= {
                    "logic": keras.metrics.F1Score,
                    "annotations": {},
                    "input": False
                }
            ),
            listNode(
                label="Mean Squared Error",
                node_type= ParameterNode,
                kwargs= {
                    "logic": keras.metrics.MeanSquaredError,
                    "annotations": {},
                    "input": False
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
                        "model": CompileNode,
                        "filepath": str
                    },
                    "input": False,
                    "output": False
                }
            ),
            listNode(
                label="Plot model",
                node_type= UtilsNode,
                kwargs= {
                    "logic": keras.utils.plot_model,
                    "annotations": {
                        "model": CompileNode,
                        "to_file": str,
                        "show_shapes": bool,
                        "show_layer_names": bool,
                        "show_layer_activations": bool
                    },
                    "input": False,
                    "output": False
                }
            )
        ]
    }
}
