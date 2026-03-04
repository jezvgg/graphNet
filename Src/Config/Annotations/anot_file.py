from pathlib import Path

import dearpygui.dearpygui as dpg

from Src.Config.Annotations.annotation import Annotation
from Src.Enums import DPGType


class AFile(Annotation):


    @staticmethod
    def build(*args, **kwargs):
        kwargs = Annotation.check_kwargs(dpg.node_attribute, kwargs)
        browser_id = dpg.generate_uuid()
        group_id = dpg.generate_uuid()

        with dpg.file_dialog(directory_selector=False, show=False, modal=True, \
                              width=1400 ,height=800, tag=browser_id, 
                              callback=lambda _, appdata: 
                                dpg.set_item_user_data(group_id, 
                                        list(map(Path, appdata['selections'].values())))):
            dpg.add_file_extension(".*")

        with dpg.group(*args, **kwargs, tag=group_id, user_data=None) as item:
            dpg.add_button(label="Choose file...", callback=lambda: dpg.show_item(browser_id))

        return item
    

    @staticmethod
    def get(input_id: int | str):
        if DPGType(input_id) != DPGType.GROUP:
            raise Exception(f"Incompatable item for AFile.get - {dpg.get_item_type(input_id)}") 
        
        return dpg.get_item_user_data(input_id)
    

    @staticmethod
    def set(input_id: str| int, value: Path) -> bool:
        if not (isinstance(value, list) and \
            all(isinstance(sub, Path) for sub in value) and \
            DPGType(input_id) == DPGType.GROUP):
            return False
        
        dpg.set_item_user_data(input_id, value)
        return True
