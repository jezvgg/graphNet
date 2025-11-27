from pathlib import Path
from typing import List
from datetime import datetime

class FileItem:
    """Dataclass с информацией о файле/папке для UI. Чистая доменная модель."""
    name: str
    path: str
    is_dir: bool
    size_str: str  # "1.2 KB"
    date_str: str  # "2023-01-01 12:30"
    type_str: str  # "Folder", ".py", "File"
    icon_tag: str  # "folder", "python"

    def __init__(self, name: str, path: str, is_dir: bool, size: int, mtime: float, icon_tag: str):
        self.name = name
        self.path = path
        self.is_dir = is_dir
        self.size_str = self._format_size(size) if not is_dir else "DIR"
        self.date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        self.type_str = "Folder" if is_dir else (Path(name).suffix or "File")
        self.icon_tag = icon_tag

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"


class FileScanner:
    """Сканирует директорию и возвращает данные в формате для UI. """    
    _ICON_MAP = {
        ".py": "python", ".js": "script", ".html": "document", ".css": "document",
        ".json": "document", ".xml": "document", ".txt": "note", ".md": "note",
        ".jpg": "picture", ".jpeg": "picture", ".png": "picture", ".gif": "picture",
        ".svg": "vector", ".mp3": "music_note", ".wav": "music_note", ".mp4": "video",
        ".zip": "zip", ".rar": "zip", ".7z": "zip", ".exe": "app", ".msi": "app",
        ".iso": "iso",
    }
    _DEFAULT_ICON = "mini_document"
    _FOLDER_ICON = "folder"

    def __init__(self, show_hidden: bool = False, dirs_only: bool = False):
        self.show_hidden = show_hidden
        self.dirs_only = dirs_only

    def scan_directory(self, path: Path, search_query: str = "", file_filter: str = ".*") -> List[FileItem]:
        """Основной метод: сканирует директорию с фильтрами и сортировкой."""
        try:
            items = self._list_items(path)
            items = self._apply_filters(items, search_query, file_filter)
            items.sort(key=lambda x: (not x.is_dir, x.name.lower()))  # папки вверху
            return [self._create_file_item(item) for item in items]
        except (OSError, PermissionError) as e:
            print(f"❌ Access denied to {path}: {e}")
            return []

    def _list_items(self, path: Path) -> List[Path]:
        """Читает список файлов/папок с учётом скрытых файлов."""
        items = []
        for item in path.iterdir():
            if not self.show_hidden and item.name.startswith('.'):
                continue
            if self.dirs_only and not item.is_dir():
                continue
            items.append(item)
        return items

    def _apply_filters(self, items: List[Path], search_query: str, file_filter: str) -> List[Path]:
        """Применяет поиск и фильтр по расширению."""
        if search_query:
            query = search_query.lower()
            items = [i for i in items if query in i.name.lower()]
        
        if file_filter != ".*":
            ext = file_filter.lower()
            items = [i for i in items if i.is_dir() or i.suffix.lower() == ext]
        
        return items

    def _create_file_item(self, path: Path) -> FileItem:
        """Создаёт FileItem с обработкой ошибок доступа."""
        try:
            stat = path.stat()
            is_dir = path.is_dir()
            icon_tag = self._FOLDER_ICON if is_dir else self._get_file_icon(path)
            return FileItem(
                name=path.name or str(path),
                path=str(path.resolve()),
                is_dir=is_dir,
                size=stat.st_size,
                mtime=stat.st_mtime,
                icon_tag=icon_tag
            )
        except (OSError, PermissionError):
            return FileItem(
                name=path.name or str(path),
                path=str(path),
                is_dir=False,
                size=0,
                mtime=0,
                icon_tag="mini_error"
            )

    def _get_file_icon(self, path: Path) -> str:
        """Определяет иконку по расширению файла."""
        return self._ICON_MAP.get(path.suffix.lower(), self._DEFAULT_ICON)