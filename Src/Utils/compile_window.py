from Src.Utils.singleton import singleton
from Src.Utils.viewport import on_viewport_resize_callback
import dearpygui.dearpygui as dpg
@singleton
class CompileWindow():
    def __init__(self, max_lines: int = 7):
        self.log_items = [] #все логи
        self.max_lines = max_lines #максимальная вместимость в окне
        self.log_group = None

    def create_window(self): #создание окна
        with dpg.window(label="Компиляция графа", modal=True, no_resize=True, no_move=True, no_scrollbar=True,width=500,height=300, tag="compile_window") as window:
            with dpg.group() as self.log_group:
                pass
            dpg.add_button(label="Закрыть", callback=lambda: dpg.configure_item(window, show=False))

        on_viewport_resize_callback()
    
    def push(self, text, flag: bool = True):
        children = dpg.get_item_children(self.log_group, slot=1)
        first_child = children[0] if children else None
        if flag:
            item = dpg.add_text(text, wrap=460, parent=self.log_group,color=[255, 255, 255, 255])
        else:
            item = dpg.add_text(text, wrap=460, parent=self.log_group,color=[239, 83, 80, 255])
        if first_child:
            dpg.move_item(item, parent=self.log_group, before=first_child)
        self.log_items.append(item)
        self.pop()

    def pop(self): 
        if len(self.log_items) > self.max_lines:
            dpg.delete_item(self.log_items.pop(0))





    
