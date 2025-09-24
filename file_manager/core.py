# core.py
import os
from .state import FileDialogState
from .config import FileDialogConfig
from pathlib import Path
from datetime import datetime
from typing import List
import logging

logger = logging.getLogger("file_manager")

class FileDialogCore:
    def __init__(self, config: FileDialogConfig, state: FileDialogState):
        self.config = config
        self.state = state
        self.state.current_path = config.default_path
        self._table_tag = 'explorer'
        
        
        
    def _get_file_info(self, path: Path) -> dict:
        """Возвращает словарь с информацией о файле/папке для отображения."""
        try:
            stat = path.stat()
            is_dir = path.is_dir()
            size = "DIR" if is_dir else self._format_size(stat.st_size)
            mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")

            # Определяем иконку
            icon_tag = "mini_folder" if is_dir else self._get_file_icon(path)

            return {
                "name": path.name or str(path),  # для корня
                "path": str(path),
                "is_dir": is_dir,
                "size": size,
                "date": mtime,
                "type": "Folder" if is_dir else path.suffix or "File",
                "icon": icon_tag,
            }
        except (OSError, PermissionError):
            # Если нет доступа — показываем с ошибкой
            return {
                "name": path.name or str(path),
                "path": str(path),
                "is_dir": False,
                "size": "N/A",
                "date": "N/A",
                "type": "Access Denied",
                "icon": "mini_error",
            }

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Форматирует размер в человекочитаемый вид."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    @staticmethod
    def _get_file_icon(path: Path) -> str:
        """Возвращает тег иконки в зависимости от расширения файла."""
        ext = path.suffix.lower()
        icon_map = {
            ".py": "python",
            ".js": "script",
            ".html": "document",
            ".css": "document",
            ".json": "document",
            ".xml": "document",
            ".txt": "note",
            ".md": "note",
            ".jpg": "picture",
            ".jpeg": "picture",
            ".png": "picture",
            ".gif": "picture",
            ".svg": "vector",
            ".mp3": "music_note",
            ".wav": "music_note",
            ".mp4": "video",
            ".avi": "video",
            ".mkv": "video",
            ".zip": "zip",
            ".rar": "zip",
            ".7z": "zip",
            ".exe": "app",
            ".msi": "app",
            ".iso": "iso",
        }
        return icon_map.get(ext, "mini_document")
    
    def refresh_directory(self):
        """Обновить содержимое текущей директории — читает файлы, применяет фильтры и обновляет таблицу."""
        try:
            current_path = Path(self.state.current_path)
            if not current_path.exists() or not current_path.is_dir():
                raise FileNotFoundError(f"Directory not found: {current_path}")

            # Получаем все элементы
            items = []
            for item in current_path.iterdir():
                # Пропускаем скрытые, если не разрешено
                if not self.config.show_hidden_files and item.name.startswith('.'):
                    continue
                # Пропускаем файлы, если dirs_only=True
                if self.config.dirs_only and not item.is_dir():
                    continue
                items.append(item)

            # Применяем фильтр по расширению
            if self.state.filter_selected != ".*":
                filter_ext = self.state.filter_selected.lower()
                items = [
                    item for item in items
                    if item.is_dir() or (item.suffix.lower() == filter_ext)
                ]

            # Применяем поиск
            if self.state.search_query:
                query = self.state.search_query.lower()
                items = [item for item in items if query in item.name.lower()]

            # Сортируем: папки вверху, затем по имени
            items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))

            # Преобразуем в данные для UI
            file_infos = [self._get_file_info(item) for item in items]

            # Очищаем и перерисовываем таблицу
            self._update_table(file_infos)

        except Exception as e:
            logger.info(f"❌ Error refreshing directory: {e}")
            self._update_table([])  # очищаем таблицу
    
    def _update_table(self, file_infos: List[dict]):
        """Обновляет таблицу в UI на основе списка file_infos."""
        import dearpygui.dearpygui as dpg

        # Сохраняем список для поиска индексов
        self.state.file_list_cache = file_infos

        # Очищаем таблицу
        for child in dpg.get_item_children(self._table_tag, slot=1):
            dpg.delete_item(child)

        # Добавляем строки
        for idx, info in enumerate(file_infos):
            with dpg.table_row(parent=self._table_tag):
                # Имя (с иконкой)
                with dpg.table_cell():
                    with dpg.group(horizontal=True) as item:
                        dpg.add_image(info["icon"], width=16, height=16)
                        dpg.add_selectable(
                            label=info["name"],
                            span_columns=False,
                            height=20,
                            user_data={"path": info["path"], "index": idx},
                            default_value=info["path"] in self.state.selected_files,
                        )

                        with dpg.item_handler_registry() as handler:
                            dpg.add_item_double_clicked_handler(callback=self._on_file_double_click, user_data={"path": info["path"], "index": idx})
                            dpg.add_item_clicked_handler(callback=self._on_file_click, user_data={"path": info["path"], "index": idx})

                        dpg.bind_item_handler_registry(item, handler)
                    
                # Остальные ячейки
                with dpg.table_cell():
                    dpg.add_text(info["date"])
                with dpg.table_cell():
                    dpg.add_text(info["type"])
                with dpg.table_cell():
                    dpg.add_text(info["size"])
                    
    def on_path_enter(self, sender, app_data):
        """Обработчик ввода пути."""
        new_path = app_data.strip()
        if os.path.exists(new_path) and os.path.isdir(new_path):
            self.state.current_path = new_path
            self.refresh_directory()
            # Обновляем поле ввода (на случай нормализации пути)
            import dearpygui.dearpygui as dpg
            dpg.set_value("ex_path_input", new_path)
        else:
            logger.info(f"❌ Invalid path: {new_path}")

    def on_search(self, sender, app_data):
        """Обработчик поиска."""
        self.state.search_query = app_data
        self.refresh_directory()  # сразу применяем фильтр

    def on_filter_change(self, sender, app_data):
        """Обработчик смены фильтра."""
        self.state.filter_selected = app_data
        self.refresh_directory()  # сразу применяем фильтр

    def _on_file_click(self, sender, user_data):
        """Обработчик клика по файлу/папке с поддержкой Ctrl и Shift."""
        import dearpygui.dearpygui as dpg
        user_data = dpg.get_item_user_data(sender)
        clicked_path = user_data["path"]
        clicked_index = user_data["index"]


        # Получаем состояние клавиш
        ctrl_down = dpg.is_key_down(dpg.mvKey_LControl)
        shift_down = dpg.is_key_down(dpg.mvKey_LShift)

        # Сбрасываем выделение, если клик без Ctrl/Shift и multi_selection=True
        if not ctrl_down and not shift_down and self.config.multi_selection:
            self.state.selected_files = [clicked_path]
            self.state.anchor_index = clicked_index
            self.state.last_selected_index = clicked_index

        elif ctrl_down:
            if clicked_path in self.state.selected_files:
                self.state.selected_files.remove(clicked_path)
                if self.state.last_selected_index == clicked_index:
                    self.state.last_selected_index = None
                if self.state.anchor_index == clicked_index:
                    self.state.anchor_index = None
            else:
                self.state.selected_files.append(clicked_path)
                self.state.last_selected_index = clicked_index
                if self.state.anchor_index is None:
                    self.state.anchor_index = clicked_index

        elif shift_down and self.state.anchor_index is not None:
            start = min(self.state.anchor_index, clicked_index)
            end = max(self.state.anchor_index, clicked_index)
            new_selection = []
            for i in range(start, end + 1):
                if i < len(self.state.file_list_cache):
                    new_selection.append(self.state.file_list_cache[i]["path"])
            self.state.selected_files = new_selection
            self.state.last_selected_index = clicked_index

        elif not self.config.multi_selection:
            self.state.selected_files = [clicked_path]
            self.state.anchor_index = clicked_index
            self.state.last_selected_index = clicked_index

        self._sync_selection_state()

        logger.info(f"📁 Selected: {self.state.selected_files}")

    def _on_file_double_click(self, sender, user_data):
        """Обработчик двойного клика: открывает папку или принимает файл."""
        import dearpygui.dearpygui as dpg
        user_data = dpg.get_item_user_data(sender)
        clicked_path = user_data['path']
        path = Path(clicked_path)
    
        if path.is_dir():
            # Открываем папку
            self.state.current_path = str(path)
            self.refresh_directory()
            import dearpygui.dearpygui as dpg
            dpg.set_value("ex_path_input", str(path))
            logger.info(f"📂 Opened folder: {path}")
        else:
            # Это файл — ведём себя как при нажатии OK
            if clicked_path not in self.state.selected_files:
                self.state.selected_files = [clicked_path]
            self.on_ok() 
    
    def _sync_selection_state(self):
        """Синхронизирует визуальное состояние selectables с self.state.selected_files."""
        import dearpygui.dearpygui as dpg

        rows = dpg.get_item_children(self._table_tag, slot=1)
        for row in rows:
            cells = dpg.get_item_children(row, slot=1)
            if not cells:
                continue
            group = dpg.get_item_children(cells[0], slot=1)
            if not group:
                continue
            for item_t in group:
                gp = dpg.get_item_children(item_t, slot=1)
                for item in gp:
                    if dpg.get_item_type(item) == "mvAppItemType::mvSelectable":
                        user_data = dpg.get_item_user_data(item)
                        if isinstance(user_data, dict) and "path" in user_data:
                            path = user_data["path"]
                            dpg.set_value(item, path in self.state.selected_files)
                        break

    def on_ok(self):
        # Фильтруем только нужные типы (если dirs_only=False — только файлы)
        if self.config.dirs_only:
            self._result = [p for p in self.state.selected_files if Path(p).is_dir()]
        else:
            self._result = [p for p in self.state.selected_files if not Path(p).is_dir()]
        
        if self.config.callback:
            self.config.callback(self._result)
        
        self._result_ready = True
        self.close()

    def on_cancel(self):
        self.state.selected_files.clear()
        self._result = []  # пустой результат
        if self.config.callback:
            self.config.callback([])
        self._result_ready = True
        self.close()
                
        
    def go_back(self):
        """Переход на уровень вверх."""
        current = Path(self.state.current_path)
        parent = current.parent
        if parent != current:  # не корень
            self.state.current_path = str(parent)
            self.refresh_directory()
            import dearpygui.dearpygui as dpg
            dpg.set_value("ex_path_input", str(parent))
        
            
    def close(self):
        """Закрывает файловый диалог."""
        import dearpygui.dearpygui as dpg
        dpg.hide_item(self.config.tag + "_window")
        # self.state.selected_files.clear()
        
        self.state.on_close = True

        logger.info("📁 File dialog closed.")