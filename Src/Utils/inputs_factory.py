from typing import Callable
from functools import singledispatchmethod

import dearpygui.dearpygui as dpg

from Src.Logging import Logger_factory, Logger


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
            bool: dpg.add_checkbox
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
            pass

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
    