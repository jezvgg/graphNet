from Src.Config.Annotations.annotation import Annotation

import dearpygui.dearpygui as dpg



class AString(Annotation):


    @staticmethod
    def build(*args, **kwargs):
        return dpg.add_input_text(**Annotation.check_kwargs(dpg.add_input_text, kwargs))
    

    @staticmethod
    def get(input_id: int | str):
        if dpg.get_item_type(input_id) != "mvAppItemType::mvInputText":
            raise Exception(f"Incompatable item for AString.get - {dpg.get_item_type(input_id)}") 
        return dpg.get_value(input_id)
    

    @staticmethod
    def set(input_id: str| int, value: str) -> bool: 
        if not isinstance(value, str) or dpg.get_item_type(input_id) != "mvAppItemType::mvInputText": 
            return False
        
        dpg.set_value(input_id, value)
        return True