import keras.metrics

from Src.Enums import Themes
from Src.Nodes import DataNode
from Src.Utils import Backfield



class MetricNode(DataNode):
    '''
    Узел для вычисления метрики между двумя наборами данных
    '''
    data: float = Backfield()
    theme_name: Themes = Themes.METRIC


    @staticmethod
    def calculate(y_true, y_pred, metric:str):
        '''
        Вычисляет указанную метрику с помощью Keras.

        Args:
            y_true: Истинные метки/значения.
            y_pred: Предсказанные метки/значения.
            metric: Название метрики для вычисления (например, 'accuracy').
        '''
        metric_fn: keras.metrics.Metric = keras.metrics.get(metric)

        metric_fn.update_state(y_true,y_pred)

        return [float(metric_fn.result().numpy())]


    def compile(self) -> bool:
        '''
        Выполняет логику узла и устанавливает значение для поля вывода 'data'.
        '''
        status = super().compile()
        if not status:
            return False

        self.data = self.OUTPUT[0]

        return status