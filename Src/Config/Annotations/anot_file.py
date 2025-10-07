from pathlib import Path

import dearpygui.dearpygui as dpg

from Src.Config.Annotations.annotation import Annotation
from Src.Enums import DPGType
from file_manager import show_file_dialog, file_dialog
from file_manager.core import FileDialogCore
class AFile(Annotation):


    @staticmethod
    def build(*args, **kwargs):
        kwargs = Annotation.check_kwargs(dpg.node_attribute, kwargs)
        group_id = dpg.generate_uuid()


        def on_file_selected(sender, app_data):
            # app_data — данные от диалога (например, путь к файлу)
            print("Selected file:", app_data)
            # Если нужно сохранить в user_data группы:
            dpg.set_item_user_data(group_id, app_data)

        def on_button_click(sender, app_data, user_data):
            # user_data здесь — group_id
            show_file_dialog(callback=lambda x: on_file_selected(group_id, x))
            
        with dpg.group(*args, **kwargs, tag=group_id, user_data=None) as item:
            dpg.add_button(
                label="Choose file...",
                callback=on_button_click,
                user_data=group_id  # передаём group_id как user_data
            )
            
        return item
    

    @staticmethod
    def get(input_id: int | str):
        if DPGType(dpg.get_item_type(input_id)) != DPGType.GROUP:
            raise Exception(f"Incompatable item for AFile.get - {dpg.get_item_type(input_id)}") 
        
        return dpg.get_item_user_data(input_id)
    

    @staticmethod
    def set(input_id: str| int, value: Path) -> bool:
        if not (isinstance(value, list) and \
            all(isinstance(sub, Path) for sub in value) and \
            DPGType(dpg.get_item_type(input_id)) == DPGType.GROUP):
            return False
        
        dpg.set_item_user_data(input_id, value)
        return True
