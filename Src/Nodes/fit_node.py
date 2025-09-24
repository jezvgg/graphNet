import keras
import dearpygui.dearpygui as dpg
import numpy as np

from Src.Nodes import AbstractNode



class FitNode(AbstractNode):
    color = (151, 0, 191, 255)


    @staticmethod
    def fit(model: keras.models.Model, **kwargs):
        if kwargs['epochs']<=0:
            raise AttributeError("Колличество эпох должно быть больше нуля!")
        
        if not(kwargs['x'].shape[0] and kwargs['x'].shape[1]):
            raise AttributeError('Не верная размерность или пустуе данные X!')
        
        if not(kwargs['y'].shape[0] and kwargs['y'].shape[1]) :
            raise AttributeError('Не верная размерность или пустуе данные Y!')
        
        if kwargs['x'].shape[0]!=kwargs['y'].shape[0]:
            raise AttributeError('Размерности X и Y не совпадают!')
        
        if not np.issubdtype(kwargs['x'].dtype, np.floating) or np.isnan(kwargs['x']).any() :
            raise AttributeError('Данные содержат неверный формат X!')
        
        if not np.issubdtype(kwargs['y'].dtype, np.floating) or np.isnan(kwargs['y']).any():
            raise AttributeError('Данные содержат неверный формат Y!')

        with dpg.window(label="Обучение", modal=True, no_close=True,tag="fit_window") as popup:
            dpg.add_loading_indicator(width=100, height=100)
        
        model.fit(**kwargs, verbose=False)

        dpg.delete_item(popup)

        return model
    


