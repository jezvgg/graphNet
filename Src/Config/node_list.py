from keras import layers
import keras

from Src.Enums.attr_type import AttrType
from Src.Nodes import *
from Src.Models import File
from Src.Config.parameter import Parameter
from Src.Config.node_annotation import NodeAnnotation


# TODO Перевести в нормальные модели, фабрику и JSON
node_list = {
    "Data & Preprocessing":
    {
        "Import data": [
            NodeAnnotation(
                label = "Tables data",
                node_type = TableDataNode,
                logic = TableDataNode.open_data,
                annotations = {
                        "files": Parameter(AttrType.INPUT, File),
                        "skip_header": Parameter(AttrType.INPUT, bool),
                        "skip_footer": Parameter(AttrType.INPUT, bool),
                        "shape": Parameter(AttrType.OUTPUT, (int, int, int))  
                    }
            ),
            NodeAnnotation(
                label="Images data",
                node_type= ImageDataNode,
                logic = ImageDataNode.open_data,
                annotations = {
                        "files": Parameter(AttrType.INPUT, File),
                        "color_mode": Parameter(AttrType.INPUT, str),
                        "shape": Parameter(AttrType.OUTPUT, (int, int, int, int)) 
                        }
            )
        ],
        "Preprocessing Utils": [
            NodeAnnotation(
                label="to categorical",
                node_type= PipelineNode,
                logic = keras.utils.to_categorical,
                annotations = {
                        "x": Parameter(AttrType.INPUT, DataNode),
                        "num_classes": Parameter(AttrType.INPUT, int)
                    }
            )
        ]
    },
    "Neural Network Layers":
    {
        "Full":
        [
            NodeAnnotation(
                label= "Dense",
                node_type= LayerNode,
                logic = layers.Dense,
                annotations = {
                        "units": Parameter(AttrType.INPUT, int),
                        "activation": Parameter(AttrType.INPUT, str),
                        "use_bias": Parameter(AttrType.INPUT, bool)
                    }
            )
        ],
        "Convolutional":
        [
            NodeAnnotation(
                label= "Conv2D",
                node_type= LayerNode,
                logic = layers.Conv2D,
                annotations = {
                        "filters": Parameter(AttrType.INPUT, int),
                        "kernel_size": Parameter(AttrType.INPUT, int),
                        "strides": Parameter(AttrType.INPUT, int),
                        "padding": Parameter(AttrType.INPUT, str),
                        "activation": Parameter(AttrType.INPUT, str),
                        "use_bias": Parameter(AttrType.INPUT, bool),
                    } 
            ),
            NodeAnnotation(
                label= "MaxPooling2D",
                node_type= LayerNode,
                logic = layers.MaxPooling2D,
                annotations = {
                        "pool_size": Parameter(AttrType.INPUT, (int, int)),
                        "strides": Parameter(AttrType.INPUT, int),
                        "padding": Parameter(AttrType.INPUT, str),
                    }
            )
        ],
        "Etc":[
            NodeAnnotation(
                label="Concatenate",
                node_type= LayerNode,
                logic = layers.Concatenate,
            ),
            NodeAnnotation(
                label="Flatten",
                node_type= LayerNode,
                logic = layers.Flatten,
            ),
            NodeAnnotation(
                label="Add",
                node_type= LayerNode,
                logic = layers.Add,
            )
        ]
    },
    "Training": {
        "General": [
            NodeAnnotation(
                label="Compile model",
                node_type= CompileNode,
                logic = keras.models.Model.compile,
                annotations = {
                        "optimizer": Parameter(AttrType.INPUT, OptimizerNode),
                        "loss": Parameter(AttrType.INPUT, LossNode),
                        # "metrics": MetricNode
                    }
            ),
            NodeAnnotation(
                label="Fit model",
                node_type= FitNode,
                logic = keras.models.Model.fit,
                annotations = {
                        "self": Parameter(AttrType.INPUT, CompileNode),
                        "x": Parameter(AttrType.INPUT, DataNode),
                        "y": Parameter(AttrType.INPUT, DataNode),
                        "epochs": Parameter(AttrType.INPUT, int)
                    }
            )
        ],
        "Optimizers": [
            NodeAnnotation(
                label="Adam",
                node_type= OptimizerNode,
                logic = keras.optimizers.Adam,
                annotations = {
                        "learning_rate": Parameter(AttrType.INPUT, float),
                        # "beta_1": float,
                        # "beta_2": float,
                        # "epsilon": float
                    },
                input = False
            ),
            NodeAnnotation(
                label="Stochastic Gradient Descent",
                node_type= OptimizerNode,
                logic = keras.optimizers.SGD,
                annotations = {
                        "learning_rate": Parameter(AttrType.INPUT, float),
                        "momentum": Parameter(AttrType.INPUT, float),
                        "nesterov": Parameter(AttrType.INPUT, bool)
                    },
                input = False
            ),
            NodeAnnotation(
                label="RMSprop",
                node_type= OptimizerNode,
                logic = keras.optimizers.RMSprop,
                annotations =  {
                        "learning_rate": Parameter(AttrType.INPUT, float),
                        "momentum": Parameter(AttrType.INPUT, float)
                    },
                input =  False
            )
        ],
        "Losses": [
            NodeAnnotation(
                label="Binary cross-entropy",
                node_type= LossNode,
                logic = keras.losses.BinaryCrossentropy,
                input =  False
            ),
            NodeAnnotation(
                label="Mean Squared Error",
                node_type= LossNode,
                logic = keras.losses.MeanSquaredError,
                input = False
            ),
            NodeAnnotation(
                label="Cross-entropy",
                node_type= LossNode,
                logic = keras.losses.CategoricalCrossentropy,
                input = False
            ),
        ],
        "Metrics": [
            NodeAnnotation(
                label="Accuracy",
                node_type= ParameterNode,
                logic = keras.metrics.Accuracy,
                input = False
            ),
            NodeAnnotation(
                label="F1 score",
                node_type= ParameterNode,
                logic = keras.metrics.F1Score,
                input = False
            ),
            NodeAnnotation(
                label="Mean Squared Error",
                node_type= ParameterNode,
                logic = keras.metrics.MeanSquaredError,
                input = False
            )
        ],
        "Utils": [
            NodeAnnotation(
                label="Save model",
                node_type= UtilsNode,
                logic = keras.saving.save_model,
                annotations = {
                        "model": Parameter(AttrType.INPUT, CompileNode),
                        "filepath": Parameter(AttrType.INPUT, str)
                    },
                input = False,
                output = False
            ),
            NodeAnnotation(
                label="Plot model",
                node_type= UtilsNode,
                logic = keras.utils.plot_model,
                annotations = {
                        "model": Parameter(AttrType.INPUT, CompileNode),
                        "to_file": Parameter(AttrType.INPUT, str),
                        "show_shapes": Parameter(AttrType.INPUT, bool),
                        "show_layer_names": Parameter(AttrType.INPUT, bool),
                        "show_layer_activations": Parameter(AttrType.INPUT, bool)
                    },
                input = False,
                output = False
            )
        ]
    }
}
