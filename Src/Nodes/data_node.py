from pathlib import Path
from abc import abstractmethod

import numpy as np

from Src.Utils import Backfield
from Src.Nodes import AbstractNode



class DataNode(AbstractNode):
    '''
    Нода, которая содержит в себе данные. (файлы или табличные)
    '''
    shape: tuple[int] = Backfield()
    OUTPUT: np.ndarray
    

    @staticmethod
    @abstractmethod
    def open_data(files: list[Path], *args, **kwargs):
        pass


    def compile(self):
        status = super().compile()
        if not status or len(self.OUTPUT.shape) < 2: return False
        self.shape = self.OUTPUT.shape[1:]
        return status
    