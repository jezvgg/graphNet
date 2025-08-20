import numpy as np

from Src.Nodes import DataNode



class TableDataNode(DataNode):

    @staticmethod
    def open_data(files: dict, *args, **kwargs):
        if not files: 
            raise AttributeError("Вы не выбрали данные, которые нужно открыть!")
        
        return np.genfromtxt(files[0], *args, **kwargs, ndmin=2)