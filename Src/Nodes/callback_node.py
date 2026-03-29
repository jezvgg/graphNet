from Src.Enums import Themes
from Src.Nodes import AbstractNode
from Src.Config.TrainingCallbacks import callbacks_list



class CallbackNode(AbstractNode):
    """
    Нода для подключения callback'ов при обучении модели.
    """
    theme_name: Themes = Themes.CALLBACK


    @staticmethod
    def get_callback(*args, **kwargs):
        """
        Метод для получения callback'а и его параметров по его имени из словаря callback'ов.
        """
        callback = callbacks_list[kwargs["callback"]]
        return callback["class"](**callback["kwargs"])
