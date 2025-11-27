# file_manager/dialog.py
from typing import List, Callable, Optional, Tuple
from pathlib import Path
from .file_dialog_controller import FileDialogController
from .state import FileDialogState
from .file_scanner import FileScanner
from .ui import FileDialogUI
from .icon_handler import IconHandler

class FileDialog:
    """Современный файловый диалог без синглтона и конфигурационного объекта.
    
    Все параметры хранятся напрямую в экземпляре класса.
    
    Режимы работы:
    1. Асинхронный (callback):
        dialog = FileDialog(callback=lambda res: ...)
        dialog.show()
    
    2. Синхронный (блокирующий):
        dialog = FileDialog()
        result = dialog.show_and_get_result()
    """
    
    def __init__(
        self,
        *,
        title: str = "File dialog",
        tag: str = "file_dialog",
        width: int = 950,
        height: int = 650,
        min_size: Tuple[int, int] = (460, 320),
        dirs_only: bool = False,
        default_path: Optional[str] = None,
        filter_list: Optional[List[str]] = None,
        file_filter: str = ".*",
        callback: Optional[Callable[[List[str]], None]] = None,
        show_dir_size: bool = False,
        allow_drag: bool = True,
        multi_selection: bool = True,
        show_shortcuts_menu: bool = True,
        no_resize: bool = True,
        modal: bool = True,
        show_hidden_files: bool = False,
        user_style: int = 0,
        icon_handler: Optional[IconHandler] = None
    ):
        # === Храним все параметры напрямую ===
        self.title = title
        self.tag = tag
        self.width = width
        self.height = height
        self.min_size = min_size
        self.dirs_only = dirs_only
        self.default_path = default_path or str(Path.home())
        self.filter_list = filter_list or self._default_filter_list()
        self.file_filter = file_filter
        self.callback = callback
        self.show_dir_size = show_dir_size
        self.allow_drag = allow_drag
        self.multi_selection = multi_selection
        self.show_shortcuts_menu = show_shortcuts_menu
        self.no_resize = no_resize
        self.modal = modal
        self.show_hidden_files = show_hidden_files
        self.user_style = user_style
        
        # === Инициализация остального состояния ===
        self._result_ready = False
        self._result: List[str] = []
        
        # === Сборка зависимостей ===
        self._setup_dependencies(icon_handler)

    def _setup_dependencies(self, icon_handler: Optional[IconHandler]):
        """Собирает зависимости для диалога без использования конфигурационного объекта."""
        
        # FileScanner получает только необходимые параметры
        scanner = FileScanner(
            show_hidden=self.show_hidden_files,
            dirs_only=self.dirs_only
        )
        
        # Controller получает только бизнес-параметры
        self.controller = FileDialogController(
            scanner=scanner,
            callback=self._handle_callback,
            dirs_only=self.dirs_only
        )
        
        # IconHandler: используем внешний или создаём по умолчанию
        icon_handler = icon_handler or IconHandler(
            Path(__file__).parent.parent / "assets" / "icons"
        )
        icon_handler.load_icons()  # загружаем один раз при инициализации
        
        # UI получает только UI-специфичные параметры
        self.ui = FileDialogUI(
            controller=self.controller,
            title=self.title,
            tag=self.tag,
            width=self.width,
            height=self.height,
            min_size=self.min_size,
            show_shortcuts_menu=self.show_shortcuts_menu,
            no_resize=self.no_resize,
            modal=self.modal,
            icon_handler=icon_handler
        )

    def _handle_callback(self, result: List[str]):
        """Обработчик результата из контроллера."""
        self._result = result
        self._result_ready = True
        if self.callback:
            self.callback(result)

    def show(self):
        """Показать диалог в асинхронном режиме."""
        self.ui.show()

    def show_and_get_result(self) -> List[str]:
        """Показать диалог и дождаться результата (блокирующий режим)."""
        self.show()
        while not self._result_ready:
            import dearpygui.dearpygui as dpg
            dpg.split_frame()
        return self._result

    @staticmethod
    def _default_filter_list() -> List[str]:
        """Статический метод для получения фильтров по умолчанию."""
        return [
            ".*", ".txt", ".py", ".png", ".jpg", ".jpeg", ".gif", ".bmp", 
            ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip", ".rar", ".7z"
        ]