import numpy as np

from Src.Nodes import DataNode



class TableDataNode(DataNode):

    @staticmethod
    def open_data(files: dict, *args, **kwargs):
        key = list(files['selections'].keys())[0]
        return np.genfromtxt(files['selections'][key], delimiter=',', *args, **kwargs)