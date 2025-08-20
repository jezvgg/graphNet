import keras
import dearpygui.dearpygui as dpg

from Src.Nodes import ParameterNode




class PredictNode(ParameterNode):
    logic: keras.models.Model.predict


    def compile(self):
        return super().compile(kwargs={"verbose": False})