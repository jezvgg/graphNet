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
    

    @staticmethod
    def split_Xy(data: np.ndarray):
        '''
            Разделение данных на X и y

        '''

        data = np.asarray(data)
        if data is None:
            raise Exception("Передаваемые данные пустые")
        data = np.squeeze(data, axis=0) if data.ndim > 2 and data.shape[0] == 1 else np.asarray(data)
        if data.ndim != 2 or data.shape[1] < 2:
             raise ValueError(f"Нужно 2D и ≥2 колонки, пришло {data.shape}")

        X = data[:, :-1]
        y = data[:, -1]
        return Dataset(X, y)



    @staticmethod
    def train_test_split(x: np.ndarray, y: np.ndarray, test_size: float = 0.25, random_state: int | None = None, **kwargs):
        '''

        Разделяет полученные данные на train и на test и перемешивает их для лучшего обучения

        '''
        x, y =np.asarray(x) , np.asarray(y) 
        n_samples = x.shape[0]
        if x.ndim ==0:
            raise ValueError("x должен быть массивом с размерностью не меньше 1")
        if y is not None and y.shape[0] != n_samples:
            raise ValueError("Количество образцов в x и y должно быть одинаковым")
        
        
        if not (test_size>0 and test_size<1): raise Exception('')
        test_size = int(test_size*n_samples)
        train_size = n_samples-test_size

        indices = np.arange(n_samples)
        np.random.default_rng(random_state).shuffle(indices)

        n_train , n_test = indices[:train_size],indices[train_size:train_size+test_size]
        X_train, X_test = x[n_train], x[n_test]
        y_train, y_test = y[n_train], y[n_test]
        return Dataset( X_train, X_test, y_train, y_test if y is not None else (X_train, X_test))


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
