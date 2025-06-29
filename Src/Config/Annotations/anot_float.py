from Src.Config.Annotations.annotation import Annotation

import dearpygui.dearpygui as dpg



class AFloat(Annotation):


    @staticmethod
    def build(*args, **kwargs):
        return dpg.add_input_float(**Annotation.check_kwargs(dpg.add_input_float, kwargs))
    

    @staticmethod
    def get(input_field: int | str):
        return dpg.get_value(input_field)
    

    @staticmethod
    def set(): pass