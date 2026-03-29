from keras import callbacks

from Src.Nodes import AbstractNode



class Log2Window(callbacks.Callback):
    '''
    Колбэк для вывода логов обучения в окно сборки модели.
    '''

    def on_train_begin(self, logs: dict | None = None):
        '''
        Вывод в окно сборки модели сообщения о начале обучения.
        '''
        AbstractNode.log2window("Обучение начато!")


    def on_epoch_begin(self, epoch: int, logs: dict | None = None):
        '''
        Вывод в окно сборки модели сообщения о начале эпохи.
        '''
        AbstractNode.log2window(f"Эпоха {epoch + 1} началась...")


    def on_epoch_end(self, epoch: int, logs: dict | None = None):
        '''
        Вывод в окно сборки модели сообщения о конце эпохи.
        '''
        AbstractNode.log2window(f"Эпоха {epoch + 1} закончилась: {logs}")


    def on_train_end(self, logs: dict | None = None):
        '''
        Вывод в окно сборки модели сообщения о конце обучения.
        '''
        AbstractNode.log2window("Обучение завершено!")
