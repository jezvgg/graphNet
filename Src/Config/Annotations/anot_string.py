from Src.Config.Annotations.annotation import Annotation

import dearpygui.dearpygui as dpg



class AString(Annotation):


    @staticmethod
    def build(*args, **kwargs):
        return dpg.add_input_text(**Annotation.check_kwargs(dpg.add_input_text, kwargs))
    

    @staticmethod
    def get(input_field: int | str):
        return dpg.get_value(input_field)
    

    @staticmethod
    def set(input_id: str| int): pass