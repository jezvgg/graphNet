from dataclasses import dataclass

import keras
import dearpygui.dearpygui as dpg
import numpy as np
from tensorflow.keras import callbacks

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
        
        trainingCallback = TrainingCallback()
        history = model.fit(**kwargs, verbose=False, callbacks=[trainingCallback])

        return model
    



class TrainingCallback(callbacks.Callback):
    '''
    Колбэк для вывода логов обучения в окно сборки модели.
    '''

    def on_train_begin(self, logs: dict | None = None):
        '''
        Вывод в окно сборки модели сообщения о начале обучения.
        '''
        FitNode.add_message_to_compile_window_static("Обучение начато!")


    def on_epoch_begin(self, epoch: int, logs: dict | None = None):
        '''
        Вывод в окно сборки модели сообщения о начале эпохи.
        '''
        FitNode.add_message_to_compile_window_static(f"Эпоха {epoch + 1} началась...")


    def on_epoch_end(self, epoch: int, logs: dict | None = None):
        '''
        Вывод в окно сборки модели сообщения о конце эпохи.
        '''
        FitNode.add_message_to_compile_window_static(f"Эпоха {epoch + 1} закончилась")


    def on_train_end(self, logs: dict | None = None):
        '''
        Вывод в окно сборки модели сообщения о конце обучения.
        '''
        FitNode.add_message_to_compile_window_static("Обучение завершено!")
