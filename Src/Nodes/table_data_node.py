import numpy as np

from Src.Nodes import ShapeNode



class TableDataNode(ShapeNode):
    color = (255, 144, 144, 255)


    @staticmethod
    def open_data(files: dict, *args, **kwargs):
        if not files: 
            raise AttributeError("Вы не выбрали данные, которые нужно открыть!")
        
        return np.genfromtxt(files, *args, **kwargs, ndmin=2)