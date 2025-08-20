import keras
import dearpygui.dearpygui as dpg

from Src.Nodes import ParameterNode



class FitNode(ParameterNode):
    logic: "FitNode.fit"


    @staticmethod
    def fit(**kwargs):
        keras.models.Model.fit(**kwargs)
        return kwargs.get('self')


    def compile(self):
        with dpg.window(label="Обучение", modal=True, no_close=True) as popup:
            dpg.add_loading_indicator(width=100, height=100)

        status = super().compile(kwargs={"verbose": False})

        dpg.delete_item(popup)

        return status