from Src.Utils.singleton import singleton
from Src.Utils.viewport import on_viewport_resize_callback
import dearpygui.dearpygui as dpg
@singleton
class CompileWindow():
    def __init__(self, max_lines: int = 7):
        self.logs = [] #все логи
        self.max_lines = max_lines #максимальная вместимость в окне
        self.log_text_item = None
        self.log_text = "" #текст
    def create_window(self): #создание окна
        with dpg.window(label="Компиляция графа", modal=True, no_title_bar=True, no_resize=True, no_move=True, tag="compile_window") as window:
            self.log_text_item= dpg.add_text(self.log_text)
            dpg.add_button(label="Close", callback=lambda: dpg.configure_item(window, show=False))

        on_viewport_resize_callback()
    def push(self, text): #добавление текста
        self.logs.insert(0, text)
        self.pop()
        self.log_text = "\n".join(self.logs)
        dpg.set_value(self.log_text_item, self.log_text)
    def pop(self): 
        if len(self.logs) > self.max_lines:
            self.logs.pop()


    
