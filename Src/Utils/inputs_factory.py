from functools import wraps
from typing import Hashable

import dearpygui.dearpygui as dpg

from Src.Utils import ItemsFactory, TypesFactory
from Src.Models import File



class InputsFactory(TypesFactory, ItemsFactory):

    def __init__(self):
        ItemsFactory.__init__(self)
        TypesFactory.__init__(self)
        self.mapping(int, dpg.add_input_int)
        self.mapping(str, dpg.add_input_text)
        self.mapping(float, dpg.add_input_float)
        self.mapping(bool, dpg.add_checkbox)
        self.mapping_type(tuple, self.build_tuple)
        self.mapping(File, self.build_file)


    def build(self, value: type | Hashable ,*args, **kwargs):
        return super().build(value, *args, **kwargs) or \
                self.build_by_type(value, *args, **kwargs)


    @wraps(dpg.group, assigned=())
    def build_tuple(self, shape: tuple, *args, **kwargs):
        '''
        Если передан tuple, то создаётся группа инпутов.
        '''
        with dpg.group(horizontal=True, *args, **kwargs) as item:
            for hint in shape:
                self.build(hint, parent=item)

            # Если отсутсвует label, то создаст пустой текст
            dpg.add_text(kwargs.get('label') or '')
        return item
    

    @wraps(dpg.group, assigned=())
    def build_file(self, *args, **kwargs):
        '''
        Если передан File, то создаётся группа из файлового выбора и их просмотра.
        '''
        browser_id = dpg.generate_uuid()
        group_id = dpg.generate_uuid()

        with dpg.file_dialog(directory_selector=False, show=False, modal=True, \
                              width=1400 ,height=800, tag=browser_id, 
                              callback=lambda _, appdata: dpg.set_item_user_data(group_id,  appdata)):
            dpg.add_file_extension(".*")

        with dpg.group(*args, **kwargs, tag=group_id) as item:
            dpg.add_button(label="Choose file...", callback=lambda: dpg.show_item(browser_id))

        return item
    