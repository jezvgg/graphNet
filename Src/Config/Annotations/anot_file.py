from pathlib import Path

import dearpygui.dearpygui as dpg

from Src.Config.Annotations.annotation import Annotation
from Src.Enums import DPGType
from Src.Utils.file_dialog import open_file_dialog


class AFile(Annotation):


    @staticmethod
    def build(*args, **kwargs):
        label = kwargs.pop('label', None)
        kwargs = Annotation.check_kwargs(dpg.node_attribute, kwargs)
        group_id = dpg.generate_uuid()

        with dpg.group(*args, **kwargs, label=label, tag=group_id, user_data=None) as item:
            dpg.add_button(
                label="Choose file...",
                callback=lambda: open_file_dialog(
                    callback=lambda result: dpg.set_item_user_data(group_id, result),
                ),
            )

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
