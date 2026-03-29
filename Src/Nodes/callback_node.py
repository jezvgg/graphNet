from keras import callbacks

from Src.Enums import Themes
from Src.Nodes import AbstractNode



class CallbackNode(AbstractNode):
    theme_name: Themes = Themes.CALLBACK

    callbacks_classes = {
        "EarlyStopping": callbacks.EarlyStopping,
        "ReduceLROnPlateau": callbacks.ReduceLROnPlateau
    }

    @staticmethod
    def get_callback(*args, **kwargs):
        return CallbackNode.callbacks_classes[kwargs["callback"]]()
