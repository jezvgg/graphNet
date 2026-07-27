from Src.Utils.singleton import singleton
from Src.Utils.viewport import on_viewport_resize_callback
@singleton
class CompileWondow():
    def __init__(self, max_lines: int  = 10):
        self.logs = [] #все логи
        self.max_lines = max_lines #максимальная вместимость в окне
        self.window = None #окно 
        self.log_text = None #текст

    
