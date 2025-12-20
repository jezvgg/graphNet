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


    @staticmethod
    def as_tfjs(model: keras.models.Model, filepath: str):
        model.save(filepath+'.h5')
        converter = Popen(
            ["tensorflowjs_converter", "--input_format=keras", filepath+'h5', filepath], 
            stdout=PIPE, stderr=PIPE)
        stdout, stderr = converter.communicate()
        # Ваще пиздец, tfjs 100% всегда кидает ошибку, но работает при этом
        # if stderr: raise Exception(stderr)
        