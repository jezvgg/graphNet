from Src.Nodes import AbstractNode



class ParameterNode(AbstractNode):
    # TODO Сделать геттер с варнингом если data = None
    data: any
    

    def compile(self, kwargs = {}):
        # TODO kwargs - костыль убрать
        status = super().compile(kwargs)
        self.data = self.OUTPUT
        return status