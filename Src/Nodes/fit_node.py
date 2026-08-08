from dataclasses import dataclass

import keras
import dearpygui.dearpygui as dpg
import numpy as np
from keras.callbacks import LambdaCallback
from Src.Enums import Themes
from Src.Nodes import DataNode
from Src.Utils.compile_window import CompileWindow

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

        epochs = kwargs['epochs']
        window = CompileWindow()
        window.push("Идет процесс обучения.")
        def on_epoch_end(epoch, logs):
            dpg.set_value(window.progress, (epoch + 1) / epochs)
            dpg.split_frame()
        history = model.fit(**kwargs, verbose=False,callbacks=[LambdaCallback(on_epoch_end=on_epoch_end)])

        return model


