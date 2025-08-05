import numpy as np

from Src.Nodes import DataNode



class TableDataNode(DataNode):

    @staticmethod
    def open_data(files: dict, delimiter: str, *args, **kwargs):
        return np.genfromtxt(files[0], delimiter=delimiter, *args, **kwargs)