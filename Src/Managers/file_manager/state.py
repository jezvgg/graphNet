from typing import List, Optional, Set, Callable, Dict, Any
from pathlib import Path
import time

class ObservableState:
    """Базовый класс для наблюдаемого состояния."""
    def __init__(self):
        self._observers: List[Callable[[str, Dict[str, Any]], None]] = []
        self._lock = False  # для предотвращения рекурсивных уведомлений

    def add_observer(self, observer: Callable[[str, Dict[str, Any]], None]):
        """Подписаться на события состояния."""
        self._observers.append(observer)

    def _notify(self, event: str, payload: Dict[str, Any] = None):
        """Уведомить наблюдателей об изменении."""
        if self._lock:
            return
        try:
            self._lock = True
            for observer in self._observers:
                observer(event, payload or {})
        finally:
            self._lock = False


class FileDialogState(ObservableState):
    """Состояние файлового диалога с поддержкой наблюдения."""
    
    def __init__(self):
        super().__init__()
        self._current_path: str = str(Path.home())
        self._selected_files: Set[str] = set()
        self._search_query: str = ""
        self._filter_selected: str = ".*"
        self._last_click_time: float = 0.0
        self._anchor_index: Optional[int] = None
        self._last_selected_index: Optional[int] = None
        self._file_list_cache: List[Dict[str, Any]] = []  # временно для совместимости
        self._on_close: bool = False

    
    @property
    def current_path(self) -> str:
        return self._current_path
    
    @current_path.setter
    def current_path(self, value: str):
        if self._current_path != value:
            self._current_path = value
            self._notify("current_path_changed", {"path": value})

    @property
    def selected_files(self) -> List[str]:
        return list(self._selected_files)
    
    @selected_files.setter
    def selected_files(self, value: List[str]):
        new_set = set(value)
        if self._selected_files != new_set:
            self._selected_files = new_set
            self._notify("selection_changed", {"files": value})

    @property
    def search_query(self) -> str:
        return self._search_query
    
    @search_query.setter
    def search_query(self, value: str):
        if self._search_query != value:
            self._search_query = value
            self._notify("search_changed", {"query": value})

    # === Методы для управления выделением (инкапсулируем логику) ===
    
    def select_file(
        self,
        path: str,
        *,
        ctrl_pressed: bool = False,
        shift_pressed: bool = False,
        file_list: List[Dict[str, Any]] = None
    ):
        """Центральный метод для изменения выделения файлов."""
        now = time.time()
        
        # Двойной клик — поддержка совместимости
        if now - self._last_click_time < 0.3 and self._last_clicked_path == path:
            self._handle_double_click(path)
            self._last_click_time = 0
            self._last_clicked_path = None
            return
        
        self._last_click_time = now
        self._last_clicked_path = path

        # Определяем индекс файла в текущем списке
        index = None
        if file_list:
            for i, item in enumerate(file_list):
                if item["path"] == path:
                    index = i
                    break
        
        # Логика выделения (ранее в _on_file_click)
        if not ctrl_pressed and not shift_pressed:
            self.selected_files = [path]  # сброс выделения
            self._anchor_index = index
            self._last_selected_index = index
            
        elif ctrl_pressed:
            new_selection = set(self.selected_files)
            if path in new_selection:
                new_selection.remove(path)
                if self._last_selected_index == index:
                    self._last_selected_index = None
                if self._anchor_index == index:
                    self._anchor_index = None
            else:
                new_selection.add(path)
                self._last_selected_index = index
                if self._anchor_index is None:
                    self._anchor_index = index
            self.selected_files = list(new_selection)
            
        elif shift_pressed and self._anchor_index is not None and index is not None:
            start = min(self._anchor_index, index)
            end = max(self._anchor_index, index)
            new_selection = []
            for i in range(start, end + 1):
                if i < len(file_list):
                    new_selection.append(file_list[i]["path"])
            self.selected_files = new_selection
            self._last_selected_index = index

    def _handle_double_click(self, path: str):
        """Обработка двойного клика (пока пустой — перенесём в контроллер)."""
        pass

    @property
    def file_list_cache(self) -> List[Dict[str, Any]]:
        return self._file_list_cache
    
    @file_list_cache.setter
    def file_list_cache(self, value: List[Dict[str, Any]]):
        self._file_list_cache = value

    @property
    def anchor_index(self) -> Optional[int]:
        return self._anchor_index
    
    @property
    def last_selected_index(self) -> Optional[int]:
        return self._last_selected_index
    
    @property
    def on_close(self) -> bool:
        return self._on_close
    
    @on_close.setter
    def on_close(self, value: bool):
        self._on_close = value