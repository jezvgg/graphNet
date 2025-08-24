import logging
from threading import Timer

import dearpygui.dearpygui as dpg



class Logger(logging.Logger):
    '''
    Обёртка вокруг logging.Logger, для создания всплывающих окон с ошибками.
    '''
    layout_tag: str | int


    def __init__(self, name, layout_tag: str | int, level = 0):
        self.layout_tag = layout_tag
        super().__init__(name, level)


    def _log(self, level, msg, args, exc_info = None, extra = None, stack_info = False, stacklevel = 1):

        # if level >= self.level:
        #     dpg.push_container_stack(self.layout_tag)
        #     text_id = dpg.add_text(msg, parent=self.layout_tag, wrap=512)
        #     dpg.focus_item(self.layout_tag)
        #     Timer(10, dpg.delete_item, args=[text_id]).start()
        #     dpg.pop_container_stack()


        return super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)