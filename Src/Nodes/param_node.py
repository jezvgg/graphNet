import keras

from Src.Nodes import AbstractNode



class ParameterNode(AbstractNode):
    data: any
    

    def compile(self):
        self.data = super().compile()
        return self.data