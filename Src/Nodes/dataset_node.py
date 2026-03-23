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
    def _size_to_int(size,n_samples):
        if isinstance(size,float):
                return int(size*n_samples)
        elif isinstance(size,int):
                return size
        else:
            raise ValueError("Размер должен быть числом с плавающей запятой или целым числом")


    @staticmethod
    def train_test_split(x: np.ndarray, y: np.ndarray, test_size: float = 0.25, train_size:float | None = None, random_state: int | None = None, **kwargs):
        x, y =np.asarray(x) , np.asarray(y) if y is not None else None
        n_samples = x.shape[0]
        if x.ndim ==0:
            raise ValueError("x должен быть массивом с размерностью не меньше 1")
        if y is not None and y.shape[0] != n_samples:
            raise ValueError("Количество образцов в x и y должно быть одинаковым")
        
        test_size = Dataset._size_to_int(test_size,n_samples) if test_size is not None else n_samples - train_size
        train_size = Dataset._size_to_int(train_size,n_samples) if train_size is not None else n_samples - test_size

        
        test_size = test_size or n_samples - (test_size or train_size - n_samples*0.75)
        train_size = train_size or n_samples - test_size
        if train_size + test_size > n_samples: raise Exception("Некорректные размеры тестовой и обучающей выборки")

        indices = np.arange(n_samples)
        rng = np.random.default_rng(random_state)
        rng.shuffle(indices)
        
        n_train = indices[:train_size]
        n_test = indices[train_size:train_size+test_size]
        X_train, X_test = x[n_train], x[n_test]
        y_train, y_test = y[n_train], y[n_test]
        return X_train, X_test, y_train, y_test if y is not None else (X_train, X_test)


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