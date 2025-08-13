import keras
import dearpygui.dearpygui as dpg

from Src.Nodes import ParameterNode




class PredictNode(ParameterNode):
    logic: keras.models.Model.predict


    def compile(self):
        with dpg.window(label="Предсказание", modal=True, no_close=True) as popup:
            dpg.add_loading_indicator(width=100, height=100)

        super().compile(kwargs={"verbose": False})

        dpg.delete_item(popup)