from typing import Callable
from functools import singledispatchmethod

import dearpygui.dearpygui as dpg

from Src.Logging import Logger_factory, Logger
from Src.Models import File


class InputsFactory:
    '''
    Фабрика, реализующая инпуты, в зависимости от переданных в неё типов.
    '''
    map: dict[type, Callable]
    logger: Logger


    def __init__(self):
        '''
        Фабрика, реализующая инпуты, в зависимости от переданных в неё типов.
        '''
        self.map = {
            int: dpg.add_input_int,
            str: dpg.add_input_text,
            float: dpg.add_input_float,
            bool: dpg.add_checkbox,
            File: self.build_file
        }
        self.logger = Logger_factory.from_instance()('nodes')


    @singledispatchmethod
    def build(self, hint, *args, **kwargs):
        '''
        # ! Опасный метод

        Реализует проверку, через рефлексию, подходят ли kwargs переданому типу. Может вызвать непредвиденные ошибки, если в self.map неправильная фцнкция.

        Args:
            hint: type | tuple - аннотация, по которой строить инпут.
            *args, **kwargs - аргументы передающиеся в инпут, для его создания.
        '''
        if hint not in self.map:
            self.logger.error(f"Отсутствует обработчик для {hint}")
            return

        func = self.map[hint]
        tkwargs = {}

        for key in kwargs.keys():
            if key in func.__code__.co_varnames:
                tkwargs[key] = kwargs[key]
        return func(*args, **tkwargs)
    

    @build.register
    def build_tuple(self, hint: tuple, *args, **kwargs):
        '''
        Если передан tuple, то создаётся группа инпутов.
        '''
        with dpg.group(horizontal=True, *args, **kwargs) as item:
                for hint_ in hint:
                    self.build(hint_, parent=item)
                if 'label' in kwargs:
                    dpg.add_text(kwargs['label'])
        return item
    

    def build_file(self, label: str = 'files', *args, **kwargs):
        '''
        Если передан File, то создаётся группа из файлового выбора и их просмотра.
        '''
        browser_id = dpg.generate_uuid()
        group_id = dpg.generate_uuid()

        with dpg.file_dialog(directory_selector=False, show=False, modal=True, \
                              width=1400 ,height=800, tag=browser_id, 
                              callback=lambda _, appdata: dpg.set_item_user_data(group_id,  appdata)):
            dpg.add_file_extension(".*")

        with dpg.group(*args, **kwargs, tag=group_id, label=label) as item:
            dpg.add_button(label="Choose file...", callback=lambda: dpg.show_item(browser_id))

        return item
    