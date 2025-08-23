import numpy as np

from keras import layers
import keras

from Src.Enums import *
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
                        "delimiter": Parameter(AttrType.INPUT, AEnum[Delimiters]),
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
                        "color_mode": Parameter(AttrType.INPUT, AEnum[ColorMode]),
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
                        "activation": Parameter(AttrType.INPUT, AEnum[Activations]),
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
                        "padding": Parameter(AttrType.INPUT, AEnum[Padding]),
                        "activation": Parameter(AttrType.INPUT, AEnum[Activations]),
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
                        "padding": Parameter(AttrType.INPUT, AEnum[Padding]),
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
                        "optimizer": Parameter(AttrType.INPUT, AEnum[Optimizers]),
                        "loss": Parameter(AttrType.INPUT, AEnum[Losses]),
                        # "metrics": MetricNode
                    }
            ),
            NodeAnnotation(
                label="Fit model",
                node_type= FitNode,
                logic = FitNode.fit,
                annotations = {
                        "self": Parameter(AttrType.INPUT, ANode),
                        "x": Parameter(AttrType.INPUT, ANode),
                        "y": Parameter(AttrType.INPUT, ANode),
                        "epochs": Parameter(AttrType.INPUT, AInteger)
                    }
            ),
            NodeAnnotation(
                label="Predict",
                node_type= PredictNode,
                logic = keras.models.Model.predict,
                annotations = {
                        "self": Parameter(AttrType.INPUT, ANode),
                        "x": Parameter(AttrType.INPUT, ANode),
                    },
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
            ),
            NodeAnnotation(
                label="Calculate Metric",
                node_type=MetricNode,
                logic=MetricNode.calculate,
                annotations={
                    "metric": Parameter(AttrType.INPUT, AEnum[Metrics]),
                    "y_true": Parameter(AttrType.INPUT, ANode),
                    "y_pred": Parameter(AttrType.INPUT, ANode),
                    "data": Parameter(
                        AttrType.OUTPUT,
                        AFloat,
                        backfield=MetricNode.data
                    )
                },
                input=False,
                output=False
            ),
            NodeAnnotation(
                label="Save data",
                node_type = UtilsNode,
                logic = lambda X, fname: np.savetxt(fname, [X] if not hasattr(X, '__len__') else X),
                annotations = {
                    "X": Parameter(AttrType.INPUT, ANode),
                    "fname": Parameter(AttrType.INPUT, AString, default='result.txt')
                },
                input = False,
                output = False
            )
        ]
    }
}
