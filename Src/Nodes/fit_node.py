import keras
import dearpygui.dearpygui as dpg

from Src.Nodes import AbstractNode



class FitNode(AbstractNode):
    color = (151, 0, 191, 255)


    @staticmethod
    def fit(model: keras.models.Model, **kwargs):
        with dpg.window(label="Обучение", modal=True, no_close=True) as popup:
            dpg.add_loading_indicator(width=100, height=100)
        
        model.fit(**kwargs, verbose=False)

        dpg.delete_item(popup)

        return model
    