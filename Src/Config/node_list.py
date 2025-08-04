from keras import layers
import keras

from Src.Enums.attr_type import AttrType
from Src.Nodes import *
from Src.Config.parameter import Parameter
from Src.Config.node_annotation import NodeAnnotation
from Src.Config.Annotations import *


# TODO Сделать сериализацию в JSON
node_list = {
    "Data & Preprocessing":
    {
        "Import data": [
            NodeAnnotation(
                label = "Tables data",
                node_type = TableDataNode,
                logic = TableDataNode.open_data,
                annotations = {
                        "files": Parameter(AttrType.INPUT, AFile),
                        "skip_header": Parameter(AttrType.INPUT, ABoolean),
                        "skip_footer": Parameter(AttrType.INPUT, ABoolean),
                        "shape": Parameter(AttrType.OUTPUT, 
                                           ASequence[AInteger, AInteger, AInteger],
                                           backfield=DataNode.shape)  
                    },
                input=False
            ),
            NodeAnnotation(
                label="Images data",
                node_type= ImageDataNode,
                logic = ImageDataNode.open_data,
                annotations = {
                        "files": Parameter(AttrType.INPUT, AFile),
                        "color_mode": Parameter(AttrType.INPUT, AString),
                        "shape": Parameter(AttrType.OUTPUT, ASequence[AInteger, AInteger, AInteger]) 
                        }
            )
        ],
        "Preprocessing Utils": [
            NodeAnnotation(
                label="to categorical",
                node_type= PipelineNode,
                logic = keras.utils.to_categorical,
                annotations = {
                        "x": Parameter(AttrType.INPUT, ANode),
                        "num_classes": Parameter(AttrType.INPUT, AInteger)
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
                        "units": Parameter(AttrType.INPUT, AInteger),
                        "activation": Parameter(AttrType.INPUT, AString),
                        "use_bias": Parameter(AttrType.INPUT, ABoolean)
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
                        "filters": Parameter(AttrType.INPUT, AInteger),
                        "kernel_size": Parameter(AttrType.INPUT, AInteger),
                        "strides": Parameter(AttrType.INPUT, AInteger),
                        "padding": Parameter(AttrType.INPUT, AString),
                        "activation": Parameter(AttrType.INPUT, AString),
                        "use_bias": Parameter(AttrType.INPUT, ABoolean),
                    } 
            ),
            NodeAnnotation(
                label= "MaxPooling2D",
                node_type= LayerNode,
                logic = layers.MaxPooling2D,
                annotations = {
                        "pool_size": Parameter(AttrType.INPUT, ASequence[AInteger, AInteger]),
                        "strides": Parameter(AttrType.INPUT, AInteger),
                        "padding": Parameter(AttrType.INPUT, AString),
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
                        "optimizer": Parameter(AttrType.INPUT, ANode),
                        "loss": Parameter(AttrType.INPUT, ANode),
                        # "metrics": MetricNode
                    }
            ),
            NodeAnnotation(
                label="Fit model",
                node_type= FitNode,
                logic = keras.models.Model.fit,
                annotations = {
                        "self": Parameter(AttrType.INPUT, ANode),
                        "x": Parameter(AttrType.INPUT, ANode),
                        "y": Parameter(AttrType.INPUT, ANode),
                        "epochs": Parameter(AttrType.INPUT, AInteger)
                    }
            )
        ],
        "Optimizers": [
            NodeAnnotation(
                label="Adam",
                node_type= OptimizerNode,
                logic = keras.optimizers.Adam,
                annotations = {
                        "learning_rate": Parameter(AttrType.INPUT, AFloat),
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
                        "learning_rate": Parameter(AttrType.INPUT, AFloat),
                        "momentum": Parameter(AttrType.INPUT, AFloat),
                        "nesterov": Parameter(AttrType.INPUT, ABoolean)
                    },
                input = False
            ),
            NodeAnnotation(
                label="RMSprop",
                node_type= OptimizerNode,
                logic = keras.optimizers.RMSprop,
                annotations =  {
                        "learning_rate": Parameter(AttrType.INPUT, AFloat),
                        "momentum": Parameter(AttrType.INPUT, AFloat)
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
                        "model": Parameter(AttrType.INPUT, ANode),
                        "filepath": Parameter(AttrType.INPUT, AString)
                    },
                input = False,
                output = False
            ),
            NodeAnnotation(
                label="Plot model",
                node_type= UtilsNode,
                logic = keras.utils.plot_model,
                annotations = {
                        "model": Parameter(AttrType.INPUT, ANode),
                        "to_file": Parameter(AttrType.INPUT, AString),
                        "show_shapes": Parameter(AttrType.INPUT, ABoolean),
                        "show_layer_names": Parameter(AttrType.INPUT, ABoolean),
                        "show_layer_activations": Parameter(AttrType.INPUT, ABoolean)
                    },
                input = False,
                output = False
            )
        ]
    }
}
