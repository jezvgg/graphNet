import keras

from Src.Nodes import AbstractNode



class ParameterNode(AbstractNode):
    data: any
    

    def compile(self, kwargs = {}):
        self.data = super().compile(kwargs)
        return self.data