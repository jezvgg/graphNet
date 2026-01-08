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


    def compile(self):
        status = super().compile()
        if not status or len(self.OUTPUT.shape) < 2: return False
        self.shape = self.OUTPUT.shape[1:]
        return status


    @staticmethod
    def open_table_data(files: str, *args, **kwargs):
        if not files: 
            raise AttributeError("Вы не выбрали данные, которые нужно открыть!")
        
        return np.genfromtxt(files, *args, **kwargs, ndmin=2)

    
    @staticmethod
    def open_image_data(files: str, *args, **kwargs):
        if not files: 
            raise AttributeError("Вы не выбрали данные, которые нужно открыть!")

        images = []
        for image_path in sorted(Path(files).iterdir()):
            image = keras.utils.load_img(image_path, *args, **kwargs)
            image = keras.utils.img_to_array(image)
            images.append(image)

        return np.array(images)
    