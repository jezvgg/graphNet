from subprocess import Popen, PIPE
import numpy as np

from Src.Enums import Themes
from Src.Nodes import DataNode

class TrainTestSplitNode(DataNode):
    theme_name: Themes = Themes.UTILS
    @staticmethod
    def split(x: np.ndarray, y: np.ndarray, test_size: float = 0.25, train_size:float | None = None, random_state: int | None = None, **kwargs):
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
        indices = np.arange(n_samples)
        rng = np.random.default_rng(random_state)
        rng.shuffle(indices)
        
        n_train = indices[:train_size]
        n_test = indices[train_size:train_size+test_size]
        X_train, X_test = x[n_train], x[n_test]
        y_train, y_test = y[n_train], y[n_test]
        return X_train, X_test, y_train, y_test if y is not None else X_train, X_test

    def compile(self) -> bool:
        status = super().compile()
        if not status:
            return False

        try:
            result = self.OUTPUT
            if not isinstance(result, tuple):
                raise AttributeError("split вернул некорректный формат")

            if len(result) == 2:
                self.X_train, self.X_test = result
                self.y_train = self.y_test = None
            elif len(result) == 4:
                self.X_train, self.X_test, self.y_train, self.y_test = result
            else:
                raise AttributeError("split вернул некорректное количество выходов")

        except Exception as ex:
            self.raise_error(ex, "Ошибка при split")
            return False

        return status

