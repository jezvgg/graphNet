from Src.Config.Annotations.annotation import Annotation

import dearpygui.dearpygui as dpg



class AFloat(Annotation):


    @staticmethod
    def build(*args, **kwargs):
        return dpg.add_input_float(**Annotation.check_kwargs(dpg.add_input_float, kwargs))
    

    @staticmethod
    def get(input_id: int | str):
        if dpg.get_item_type(input_id) != "mvAppItemType::mvInputFloat":
            raise Exception(f"Incompatable item for AFloat.get - {dpg.get_item_type(input_id)}")
        
        return dpg.get_value(input_id)
    

    @staticmethod
    def set(input_id: str| int, value: float) -> bool: 
        if not isinstance(value, float) or dpg.get_item_type(input_id) != "mvAppItemType::mvInputFloat": 
            return False
        
        dpg.set_value(input_id, value)
        return True