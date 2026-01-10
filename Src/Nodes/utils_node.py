import keras
from subprocess import Popen, PIPE

from Src.Enums import Themes
from Src.Nodes import AbstractNode



class UtilsNode(AbstractNode):
    theme_name: Themes = Themes.UTILS


    @staticmethod
    def to_json(model: keras.models.Model, filename: str):
        json_string = model.to_json()

        try:
            with open(filename, 'w') as f:
                f.write(json_string)
        except Exception as ex:
            raise Exception(f"Непредвиденная ошибка с записью в файл: {ex}")

        