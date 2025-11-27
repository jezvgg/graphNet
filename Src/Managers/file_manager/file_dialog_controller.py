# from typing import List, Callable
# from pathlib import Path
# from .state import FileDialogState
# from .file_scanner import FileScanner, FileItem

# class FileDialogController:
#     """Business logic layer. No Dear PyGui dependencies!"""
    
#     def __init__(
#         self,
#         state: FileDialogState,
#         scanner: FileScanner,
#         callback: Callable[[List[str]], None] = None,
#         dirs_only: bool = False
#     ):
#         self.state = state
#         self.scanner = scanner
#         self._callback = callback
#         self._dirs_only = dirs_only
#         self._result: List[str] = []
#         self._closed = False
#         self._result_ready = False  # ← добавляем флаг

        
#         # Подписываемся на изменения состояния для реакции
#         self.state.add_observer(self._on_state_changed)

#     def _on_state_changed(self, event: str, payload: dict):
#         """Реакция на внутренние события состояния (не UI!)."""
#         if event == "current_path_changed":
#             self.refresh_directory()
#         elif event == "search_changed" or event == "filter_changed":
#             self.refresh_directory()
    
#     def refresh_directory(self) -> List[FileItem]:
#         """Обновляет файлы в текущей директории. Возвращает данные для UI."""
#         files = self.scanner.scan_directory(
#             Path(self.state.current_path),
#             search_query=self.state.search_query,
#             file_filter=self.state._filter_selected
#         )
#         # Кэшируем для логики выделения (можно перенести в состояние позже)
#         self.state.file_list_cache = [
#             {
#                 "path": f.path,
#                 "is_dir": f.is_dir,
#                 "name": f.name
#             } for f in files
#         ]
#         return files

#     def navigate_to(self, path: str):
#         """Переход в директорию (от UI или ярлыков)."""
#         self.state.current_path = path

#     def go_back(self):
#         """Переход на уровень вверх."""
#         current = Path(self.state.current_path)
#         parent = current.parent
#         if parent != current:  # не корень
#             self.state.current_path = str(parent)

#     def set_search_query(self, query: str):
#         """Установить поисковый запрос."""
#         self.state.search_query = query

#     def set_file_filter(self, filter_ext: str):
#         """Установить фильтр по расширению."""
#         self.state._filter_selected = filter_ext
#         # Явное уведомление для совместимости
#         self.state._notify("filter_changed", {"filter": filter_ext})

#     def select_file(
#         self,
#         path: str,
#         *,
#         ctrl_pressed: bool = False,
#         shift_pressed: bool = False
#     ):
#         """Централизованная логика выделения файлов."""
#         self.state.select_file(
#             path,
#             ctrl_pressed=ctrl_pressed,
#             shift_pressed=shift_pressed,
#             file_list=self.state.file_list_cache
#         )

#     def handle_double_click(self, path: str):
#         """Обработка двойного клика: папка → открыть, файл → принять."""
#         item_path = Path(path)
#         if item_path.is_dir():
#             self.navigate_to(str(item_path))
#         else:
#             self.confirm_selection([path])

#     def confirm_selection(self, paths: List[str] = None):
#         """Подтвердить выбор (кнопка OK или двойной клик по файлу)."""
#         selected = paths or self.state.selected_files
#         if self._dirs_only:
#             self._result = [p for p in selected if Path(p).is_dir()]
#         else:
#             self._result = [p for p in selected if not Path(p).is_dir()]
#         self.close(confirm=True)

#     def cancel_selection(self):
#         """Отменить выбор (кнопка Cancel)."""
#         self._result = []
#         self.close(confirm=False)

#     # === Свойства для интеграции ===
    
#     def close(self, confirm: bool = False):
#         """Закрыть диалог. Вызывает callback если нужно."""
#         self._closed = True
#         self._result_ready = True  # ← для синхронного режима
#         if confirm and self._callback:
#             self._callback(self._result)
    
#     @property
#     def result(self) -> List[str]:
#         return self._result
    
#     @property
#     def closed(self) -> bool:
#         return self._closed



# file_manager/file_dialog_controller.py
from typing import List, Set, Optional, Dict, Any
from pathlib import Path
from .file_scanner import FileScanner, FileItem

class FileDialogController:
    """Единый класс для бизнес-логики И состояния."""
    
    def __init__(
        self,
        scanner: FileScanner,
        callback: callable = None,
        dirs_only: bool = False
    ):
        # === СОСТОЯНИЕ (ранее в FileDialogState) ===
        self.current_path: str = str(Path.home())
        self.selected_files: Set[str] = set()
        self.search_query: str = ""
        self.filter_selected: str = ".*"
        self.file_list_cache: List[Dict[str, Any]] = []  # кэш для индексов
        self.anchor_index: Optional[int] = None
        self.last_selected_index: Optional[int] = None
        self.last_click_time: float = 0.0
        self.last_clicked_path: Optional[str] = None
        self.closed: bool = False
        
        # === ЗАВИСИМОСТИ ===
        self.scanner = scanner
        self.callback = callback
        self.dirs_only = dirs_only
    
    # === ПУБЛИЧНЫЕ МЕТОДЫ ДЛЯ UI ===
    
    def refresh_directory(self) -> List[FileItem]:
        """Обновляет содержимое текущей директории."""
        items = self.scanner.scan_directory(
            Path(self.current_path),
            search_query=self.search_query,
            file_filter=self.filter_selected
        )
        # Обновляем кэш для выделения
        self.file_list_cache = [{
            "path": item.path,
            "is_dir": item.is_dir,
            "name": item.name
        } for item in items]
        return items

    def navigate_to(self, path: str):
        """Переход в директорию."""
        self.current_path = path
    
    def go_back(self):
        """Переход на уровень вверх."""
        current = Path(self.current_path)
        parent = current.parent
        if parent != current:
            self.current_path = str(parent)
    
    def set_search_query(self, query: str):
        self.search_query = query
    
    def set_file_filter(self, filter_ext: str):
        self.filter_selected = filter_ext
    
    def select_file(
        self,
        path: str,
        *,
        ctrl_pressed: bool = False,
        shift_pressed: bool = False
    ):
        """Центральная логика выделения файлов."""
        # ... (вся логика из старого FileDialogState.select_file)
        # Пример для сброса выделения:
        if not ctrl_pressed and not shift_pressed:
            self.selected_files = {path}
            # ... остальная логика индексов
    
    def handle_double_click(self, path: str):
        """Обработка двойного клика."""
        item_path = Path(path)
        if item_path.is_dir():
            self.navigate_to(str(item_path))
        else:
            self.confirm_selection([path])
    
    def confirm_selection(self, paths: List[str] = None):
        """Подтверждение выбора."""
        selected = paths or list(self.selected_files)
        if self.dirs_only:
            self._result = [p for p in selected if Path(p).is_dir()]
        else:
            self._result = [p for p in selected if not Path(p).is_dir()]
        self.closed = True
        if self.callback:
            self.callback(self._result)
    
    def cancel_selection(self):
        """Отмена выбора."""
        self.selected_files.clear()
        self.closed = True