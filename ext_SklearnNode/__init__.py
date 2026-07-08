from Src.Config.node_annotation import NodeAnnotation
from .extension_config import ExtSklearnnodeNode
from Src.Config.parameter import Parameter, AttrType
from Src.Nodes.dataset_node import Dataset

EXTENSION_NAME = "ext_SklearnNode"

EXTENSION_CONFIG = {
    "ext_SklearnNode": [
        NodeAnnotation(
            label="ExtSklearnnodeNode",
            node_type=ExtSklearnnodeNode,
            logic=ExtSklearnnodeNode.compute,
            annotations={"INPUT": Parameter(AttrType.INPUT, Dataset)},
            input=True,
            output=True
        )
    ]
}
