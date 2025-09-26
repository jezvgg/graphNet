# manager.py

from typing import Optional, List
import dearpygui.dearpygui as dpg
from .dialog import FileDialog
from typing import Callable
class FileDialogManager:
    _instance: Optional['FileDialogManager'] = None
    _dialog: Optional['FileDialog'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._dialog = None

    def _ensure_dialog(self):
        """Гарантирует, что диалог создан."""
        if self._dialog is None:
            print("file dialog intializes")
            self._dialog = FileDialog()

    def show(
        self,
        *,
        title: str = "File dialog",
        tag: str = "file_dialog",
        width: int = 950,
        height: int = 650,
        min_size: tuple = (460, 320),
        dirs_only: bool = False,
        default_path: str = None,
        filter_list: list = None,
        file_filter: str = ".*",
        callback: Callable = lambda: print("FUCK YOU"),
        show_dir_size: bool = False,
        allow_drag: bool = True,
        multi_selection: bool = True,
        show_shortcuts_menu: bool = True,
        no_resize: bool = True,
        modal: bool = True,
        show_hidden_files: bool = False,
        user_style: int = 0,
    ) -> None:
        """Показывает диалог с заданными параметрами (callback-стиль)."""
        self._ensure_dialog()
        self._dialog.configure(
            title=title,
            tag=tag,
            width=width,
            height=height,
            min_size=min_size,
            dirs_only=dirs_only,
            default_path=default_path,
            filter_list=filter_list,
            file_filter=file_filter,
            callback=callback,
            show_dir_size=show_dir_size,
            allow_drag=allow_drag,
            multi_selection=multi_selection,
            show_shortcuts_menu=show_shortcuts_menu,
            no_resize=no_resize,
            modal=modal,
            show_hidden_files=show_hidden_files,
            user_style=user_style,
        )
        self._dialog.show()

    def show_and_get_result(self, **kwargs) -> List[str]:
        """Показывает диалог и возвращает результат (синхронный стиль)."""
        self._ensure_dialog()
        self._dialog.configure(**kwargs)
        return self._dialog.show_and_get_result()