import numpy as np

from keras import layers
import keras

from Src.Enums import *
from Src.Nodes import *
from Src.Config.parameter import Parameter
from Src.Config.node_annotation import NodeAnnotation
from Src.Config.Annotations import *


# TODO Сделать сериализацию в JSON?
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
                                           backfield=ShapeNode.shape)  
                    },
                input=False,
                output=DataNode
            ),
            NodeAnnotation(
                label="Images data",
                node_type= ImageDataNode,
                logic = ImageDataNode.open_data,
                annotations = {
                        "files": Parameter(AttrType.INPUT, AFile),
                        "color_mode": Parameter(AttrType.INPUT, AEnum[ColorMode]),
                        "shape": Parameter(AttrType.OUTPUT, ASequence[AInteger, AInteger, AInteger])
                        },
                input=False,
                output=DataNode
            )
        ],
        "Preprocessing Utils": [
            NodeAnnotation(
                label="to categorical",
                node_type= DataNode,
                logic = keras.utils.to_categorical,
                annotations = {
                        "num_classes": Parameter(AttrType.INPUT, AInteger)
                    },
                input=Single[DataNode]
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
                logic = LayerNode.layer(layers.Dense),
                annotations = {
                        "units": Parameter(AttrType.INPUT, AInteger),
                        "activation": Parameter(AttrType.INPUT, AEnum[Activations]),
                        "use_bias": Parameter(AttrType.INPUT, ABoolean)
                    },
                input=LayerNode
            )
        ],
        "Convolutional":
        [
            NodeAnnotation(
                label= "Conv2D",
                node_type= LayerNode,
                logic = LayerNode.layer(layers.Conv2D),
                annotations = {
                        "filters": Parameter(AttrType.INPUT, AInteger),
                        "kernel_size": Parameter(AttrType.INPUT, AInteger),
                        "strides": Parameter(AttrType.INPUT, AInteger),
                        "padding": Parameter(AttrType.INPUT, AEnum[Padding]),
                        "activation": Parameter(AttrType.INPUT, AEnum[Activations]),
                        "use_bias": Parameter(AttrType.INPUT, ABoolean),
                    },
                input=LayerNode
            ),
            NodeAnnotation(
                label= "MaxPooling2D",
                node_type= LayerNode,
                logic = LayerNode.layer(layers.MaxPooling2D),
                annotations = {
                        "pool_size": Parameter(AttrType.INPUT, ASequence[AInteger, AInteger]),
                        "strides": Parameter(AttrType.INPUT, AInteger),
                        "padding": Parameter(AttrType.INPUT, AEnum[Padding]),
                    },
                input=LayerNode
            )
        ],
        "Etc":[
            NodeAnnotation(
                label="Concatenate",
                node_type= LayerNode,
                logic = LayerNode.layer(layers.Concatenate),
                input=LayerNode
            ),
            NodeAnnotation(
                label="Flatten",
                node_type= LayerNode,
                logic = LayerNode.layer(layers.Flatten),
                input=LayerNode
            ),
            NodeAnnotation(
                label="Add",
                node_type= LayerNode,
                logic = LayerNode.layer(layers.Add),
                input=LayerNode
            )
        ]
    },
    "Training": {
        "General": [
            NodeAnnotation(
                label="Compile model",
                node_type= CompileNode,
                logic = CompileNode.compile_model,
                annotations = {
                        "optimizer": Parameter(AttrType.INPUT, AEnum[Optimizers]),
                        "loss": Parameter(AttrType.INPUT, AEnum[Losses]),
                        # "metrics": MetricNode
                    },
                input=LayerNode
            ),
            NodeAnnotation(
                label="Fit model",
                node_type= FitNode,
                logic = FitNode.fit,
                annotations = {
                        "x": Parameter(AttrType.INPUT, ANode[Single[DataNode]]),
                        "y": Parameter(AttrType.INPUT, ANode[Single[DataNode]]),
                        "epochs": Parameter(AttrType.INPUT, AInteger)
                    },
                input = Single[CompileNode]
            ),
            NodeAnnotation(
                label="Predict",
                node_type= PredictNode,
                logic = PredictNode.predict,
                annotations = {
                        "x": Parameter(AttrType.INPUT, ANode[Single[DataNode]]),
                    },
                input = Single[FitNode],
                output = DataNode
            )
        ],
        "Utils": [
            NodeAnnotation(
                label="Save model",
                node_type= UtilsNode,
                logic = keras.saving.save_model,
                annotations = {
                        "model": Parameter(AttrType.INPUT, ANode[Single[FitNode]]),
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
                        "model": Parameter(AttrType.INPUT, ANode[Single[CompileNode]]),
                        "to_file": Parameter(AttrType.INPUT, AString),
                        "show_shapes": Parameter(AttrType.INPUT, ABoolean),
                        "show_layer_names": Parameter(AttrType.INPUT, ABoolean),
                        "show_layer_activations": Parameter(AttrType.INPUT, ABoolean)
                    },
                input = False,
                output = False
            ),
            NodeAnnotation(
                label="Save data",
                node_type = UtilsNode,
                logic = np.savetxt,
                annotations = {
                    "X": Parameter(AttrType.INPUT, ANode[Single[DataNode]]),
                    "fname": Parameter(AttrType.INPUT, AString, default='result.txt')
                },
                input = False,
                output = False
            )
        ]
    }
}
