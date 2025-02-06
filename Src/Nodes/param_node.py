from Src.Nodes import AbstractNode



class ParameterNode(AbstractNode):
    # TODO Сделать геттер с варнингом если data = None
    data: any
    

    def compile(self, kwargs = {}):
        # TODO kwargs - костыль убрать
        self.data = super().compile(kwargs)
        return self.data