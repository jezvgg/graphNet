INIT_PY_TEMPLATE: str = '''from Src.Config.node_annotation import NodeAnnotation
from .extension_config import {class_name}

EXTENSION_NAME = "{ext_name}"

EXTENSION_CONFIG = {{
    "{ext_name}": [
        NodeAnnotation(
            label="{class_name}",
            node_type={class_name},
            logic={class_name}.compute,
            annotations={{}},
            input=False,
            output=False
        )
    ]
}}
'''

EXTENSION_CONFIG_TEMPLATE: str = '''from Src.Nodes import AbstractNode

class {class_name}(AbstractNode):
    def setup(self):
        pass

    def compute(self):
        pass
'''
