from dataclasses import dataclass
import socket 

import keras.datasets
import numpy as np

from Src.Enums import Themes
from Src.Nodes import ShapeNode
from Src.Utils import Backfield
from Src.Exceptions import NetworkException
from Src.Logging import logging


@dataclass(init=True)
class Dataset:
    X_train: np.ndarray
    y_train: np.ndarray
    X_test: np.ndarray
    y_test: np.ndarray
    shape: tuple[int]


class DatasetNode(ShapeNode):
    '''
    Узел для вычисления метрики между двумя наборами данных
    '''
    theme_name: Themes = Themes.DATASET
    X_train: np.ndarray
    y_train: np.ndarray
    X_test: np.ndarray
    y_test: np.ndarray
    logger = logging()('functions')


    @staticmethod
    def open_data(dataset:str) -> Dataset:
        '''
        Скачивает указанный датасет из Keras.

        Args:
            metric: Название датасета (например, 'boston_housing').
        '''
        try: socket.create_connection(("www.geeksforgeeks.org", 80)) 
        except OSError as err: 
            raise NetworkException(f'{err}.\nСкорее всего отсутствует подключение к интернету.')

        dataset = getattr(keras.datasets, dataset)
        DatasetNode.logger.info(f"Датасет {dataset} начинает загрузку")
        (X_train, y_train), (X_test, y_test) = dataset.load_data()
        DatasetNode.logger.info(f"Датасет загрузился - ({X_train.shape}, {y_train.shape}), ({X_test.shape}, {y_test.shape})")
        return Dataset(X_train, y_train, X_test, y_test, X_train.shape)


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