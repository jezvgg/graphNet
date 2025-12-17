import numpy as np

from Src.Enums import Themes
from Src.Nodes import ShapeNode



class TableDataNode(ShapeNode):
    theme_name: Themes = Themes.TABLE_DATA


    @staticmethod
    def open_data(files: str, *args, **kwargs):
        if not files: 
            raise AttributeError("Вы не выбрали данные, которые нужно открыть!")
        
        return np.genfromtxt(files, *args, **kwargs, ndmin=2)