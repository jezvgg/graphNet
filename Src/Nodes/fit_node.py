import keras
import numpy as np
import dearpygui.dearpygui as dpg

from Src.Nodes import ParameterNode



class FitNode(ParameterNode):
    logic: keras.models.Model.fit


    def compile(self):
        # data = np.loadtxt("res_oval.dat")
        # X, y = data[:, :-1], data[:, -1]
        # y = keras.utils.to_categorical(y)

        with dpg.window(label="Обучение", modal=True, no_close=True) as popup:
            dpg.add_loading_indicator()

        # super().compile(kwargs={"x":X, "y":y, "verbose": False})
        super().compile(kwargs={"verbose": False})

        dpg.delete_item(popup)