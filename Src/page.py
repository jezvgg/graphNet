from abc import ABC
from typing import Any

import dearpygui.dearpygui as dpg



class Page(ABC):
    '''
    Интерфейс страниц, которые будут показываться пользователю.
    '''
    user_data: Any
    state: int # Используется для понимания, куда переходить дальше в графе страниц

    page_tag: str | int
    stage_tag: str | int


    def __init__(self):
        self.page_tag = dpg.generate_uuid()
        self.stage_tag = dpg.generate_uuid()


    def show(self, parent: str | int, user_data: Any = None):
        '''
        Отобразить элемент.

        Args:
            parent: str | int - родительское окно в котором отобразить.
        '''
        dpg.move_item(self.page_tag, parent=parent)

    
    def hide(self):
        '''
        Спрятать элемент
        '''
        dpg.move_item(self.page_tag, parent=self.stage_tag)
