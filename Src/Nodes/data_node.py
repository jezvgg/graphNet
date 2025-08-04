from pathlib import Path

import numpy as np

from Src.Utils import Backfield
from Src.Nodes import ParameterNode



class DataNode(ParameterNode):
    '''
    Нода, которая содержит в себе данные. (файлы или табличные)
    '''
    shape: tuple[int] = Backfield()
    data: np.ndarray
    

    @staticmethod
    def open_data(files: list[Path], *args, **kwargs):
        pass


    def compile(self, kwargs = {}):
        # TODO kwargs - костыль убрать
        super().compile(kwargs)
        self.shape = self.data.shape
        return self.data
    