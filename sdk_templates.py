INIT_PY_TEMPLATE: str = ""

EXTENSION_CONFIG_TEMPLATE: str = """from Src.Nodes import AbstractNode

class {class_name}(AbstractNode):
    @classmethod
    def get_category(cls) -> str:
        return "{ext_name}"

    @classmethod
    def get_name(cls) -> str:
        return "{class_name}"

    def setup(self):
        pass

    def compute(self):
        pass

ExtensionList = [{class_name}]
"""
