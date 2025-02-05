from abc import ABC

from Src.Nodes import ParameterNode



class DataNode(ParameterNode):
    '''
    Нода, которая содержит в себе данные. (файлы или табличные)
    '''
    

    @staticmethod
    def open_data(files: dict, *args, **kwargs):
        pass
    