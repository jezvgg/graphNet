from dataclasses import dataclass

import keras
import dearpygui.dearpygui as dpg
import numpy as np

from Src.Enums import Themes
from Src.Nodes import DataNode



class FitNode(DataNode):
    theme_name: Themes = Themes.FIT
    history: np.ndarray


    def compile(self):
        status = super().compile()
        if not status: return False
        self.history: np.ndarray = np.array(self.OUTPUT.history.history['loss'])
        return status


    @staticmethod
    def fit(model: keras.models.Model, **kwargs) -> keras.Model:
        if kwargs['epochs']<=0:
            raise AttributeError("Колличество эпох должно быть больше нуля!")
        
        if kwargs['x'].shape[0]!=kwargs['y'].shape[0]:
            raise AttributeError('Размерности X и Y не совпадают!')
        
        if kwargs['x'].dtype == np.object_ or np.isnan(kwargs['x']).any() :
            raise AttributeError('Данные содержат неверный формат X!')
        
        if kwargs['y'].dtype == np.object_ or np.isnan(kwargs['y']).any():
            raise AttributeError('Данные содержат неверный формат Y!')

        with dpg.window(label="Обучение", modal=True, no_close=True,tag="fit_window") as popup:
            dpg.add_loading_indicator(width=100, height=100)
        
        history = model.fit(**kwargs, verbose=False)

        dpg.delete_item(popup)

        return model
    


