from dataclasses import dataclass
import subprocess

import keras.datasets
import numpy as np

from Src.Enums import Themes
from Src.Nodes import DataNode
from Src.Utils import Backfield
from Src.Exceptions import NetworkException


@dataclass(init=True)
class Dataset:
    X_train: np.ndarray
    y_train: np.ndarray
    X_test: np.ndarray
    y_test: np.ndarray


class DatasetNode(DataNode):
    '''
    Узел для вычисления метрики между двумя наборами данных
    '''
    theme_name: Themes = Themes.DATASET
    X_train: np.ndarray
    y_train: np.ndarray
    X_test: np.ndarray
    y_test: np.ndarray


    @staticmethod
    def load_data(dataset:str) -> Dataset:
        '''
        Скачивает указанный датасет из Keras.

        Args:
            metric: Название датасета (например, 'boston_housing').
        '''
        if (ping:=subprocess.run(['ping', '8.8.8.8'], capture_output=True)).returncode != 0:
            raise NetworkException(f"{ping.stderr[6:].decode()}Вероятнее всего, нет подключения к интернету.")

        dataset = getattr(keras.datasets, dataset)

        (X_train, y_train), (X_test, y_test) = dataset.load_data()

        return Dataset(X_train, y_train, X_test, y_test)


    def compile(self) -> bool:
        '''
        Выполняет логику узла и устанавливает значение для полей вывода данных.
        '''
        status = super().compile()
        if not status:
            return False

        # Универсиализировать бы как-нибудь
        self.X_train = self.OUTPUT.X_train
        self.y_train = self.OUTPUT.y_train
        self.X_test = self.OUTPUT.X_test
        self.y_test = self.OUTPUT.y_test

        return status