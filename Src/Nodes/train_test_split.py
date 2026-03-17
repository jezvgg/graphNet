import keras
from subprocess import Popen, PIPE
import numpy as np

from Src.Enums import Themes
from Src.Nodes import DataNode

class TrainTestSplitNode(DataNode):
    theme_name: Themes = Themes.UTILS
    @staticmethod
    def split(x: np.ndarray, y: np.ndarray, test_size: float = 0.25, train_size:float | None = None,**kwargs):
        x.assaray = np.asarray(x) 
        y.assaray = np.asarray(y) if y is not None else None
        if x.ndim ==0:
            raise ValueError("x должен быть массивом с размерностью не меньше 1")
        if y is not None and y.shape[0] == n_samples:
            raise ValueError("Количество образцов в x и y должно быть одинаковым")
        def _size_to_int(size,n_samples):
            if isinstance(size,float):
                return int(size*n_samples)
            elif isinstance(size,int):
                return size
            else:
                raise ValueError("Размер должен быть числом с плавающей запятой или целым числом")
        n_samples = x.shape[0]
        test_size = _size_to_int(test_size,n_samples) if test_size is not None else n_samples - train_size
        train_size = _size_to_int(train_size,n_samples) if train_size is not None else n_samples - test_size
        if train_size is None:
            train_size = n_samples -test_size
        if test_size is None:
            test_size = n_samples - train_size
        else:
            raise ValueError("Неккоректные размеры тестовой и обучающей выборки")
        

        


        return
