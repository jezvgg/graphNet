from pathlib import Path
from abc import abstractmethod

import numpy as np

from Src.Enums import Themes
from Src.Utils import Backfield
from Src.Nodes import DataNode



class ShapeNode(DataNode):
    '''
    Нода, которая содержит в себе данные. (файлы или табличные)
    '''
    shape: tuple[int] = Backfield()
    theme_name: Themes = Themes.SHAPE
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
    