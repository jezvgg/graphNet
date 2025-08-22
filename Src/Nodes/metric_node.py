import keras.metrics

from Src.Nodes import ParameterNode
from Src.Utils import Backfield



class MetricNode(ParameterNode):
    '''
    Узел для вычисления метрики между двумя наборами данных
    '''
    data: float = Backfield()


    @staticmethod
    def calculate(y_true, y_pred, metric:str):
        '''
        Вычисляет указанную метрику с помощью Keras.

        Args:
            y_true: Истинные метки/значения.
            y_pred: Предсказанные метки/значения.
            metric: Название метрики для вычисления (например, 'accuracy').
        '''
        metric_fn = keras.metrics.get(metric)

        metric_fn.update_state(y_true,y_pred)

        return metric_fn.result().numpy()