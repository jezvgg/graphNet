from Src.Utils.singleton import singleton
from Src.Utils.viewport import on_viewport_resize_callback
import dearpygui.dearpygui as dpg
@singleton
class CompileWindow():
    def __init__(self, max_lines: int = 7):
        self.logs = [] #все логи
        self.max_lines = max_lines #максимальная вместимость в окне
        self.log_text_item = None
    def create_window(self): #создание окна
        with dpg.window(label="Компиляция графа", modal=True, no_resize=True, no_move=True, no_scrollbar=True,width=500, tag="compile_window") as window:
            self.log_text_item= dpg.add_text("", wrap=460)
            dpg.add_button(label="Закрыть", callback=lambda: dpg.configure_item(window, show=False))

        on_viewport_resize_callback()
    def push(self, text): #добавление текста
        self.logs.insert(0, text)
        self.pop()
        dpg.set_value(self.log_text_item, "\n".join(self.logs))
        dpg.split_frame()
        w, h = dpg.get_item_rect_size(self.log_text_item)
        dpg.configure_item("compile_window", height=h + 75)
        dpg.split_frame()
        on_viewport_resize_callback()
    def pop(self): 
        if len(self.logs) > self.max_lines:
            self.logs.pop()


    
