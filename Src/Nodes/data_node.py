from pathlib import Path

import numpy as np

from Src.Nodes import ParameterNode



class DataNode(ParameterNode):
    '''
    Нода, которая содержит в себе данные. (файлы или табличные)
    '''
    _shape: tuple[int]
    data: np.ndarray
    

    @staticmethod
    def open_data(files: list[Path], *args, **kwargs):
        pass


    def compile(self, kwargs = {}):
        # TODO kwargs - костыль убрать
        super().compile(kwargs)
        self._shape = self.data.shape
        return self.data
    

    @property
    def shape(self):
        return self._shape
    