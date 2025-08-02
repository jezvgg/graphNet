import numpy as np

from Src.Nodes import DataNode



class TableDataNode(DataNode):

    @staticmethod
    def open_data(files: dict, *args, **kwargs):
        return np.genfromtxt(files[0], delimiter=',', *args, **kwargs)