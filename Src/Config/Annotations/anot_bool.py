from Src.Config.Annotations.annotation import Annotation

import dearpygui.dearpygui as dpg



class ABoolean(Annotation):


    @staticmethod
    def build(*args, **kwargs):
        return dpg.add_checkbox(**Annotation.check_kwargs(dpg.add_checkbox, kwargs))
    

    @staticmethod
    def get(input_field: int | str):
        return dpg.get_value(input_field)
    

    @staticmethod
    def set(input_id: str| int): pass