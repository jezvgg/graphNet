import keras
import numpy as np

from Src.Nodes import AbstractNode



class UtilsNode(AbstractNode):
    color = (144, 144, 255, 255)


    @staticmethod
    def to_json(model: keras.models.Model, filename: str):
        json_string = model.to_json()

        try:
            with open(filename, 'w') as f:
                f.write(json_string)
        except Exception as ex:
            raise Exception(f"Непредвиденная ошибка с записью в файл: {ex}")


    @staticmethod
    def save_data(X, fname: str):
        '''
        Сохраняет данные (X) в текстовый файл.

        Args:
            X: Данные для сохранения (например, numpy array).
            fname: Имя файла для сохранения.
        '''
        data_to_save = [X] if not hasattr(X, '__len__') or isinstance(X, str) else X
        try:
            np.savetxt(fname, data_to_save)
        except Exception as ex:
            raise Exception(f"Непредвиденная ошибка при записи данных в файл: {ex}")
        