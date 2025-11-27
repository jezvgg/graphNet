from typing import List

from pathlib import Path

from datetime import datetime




class FileItem:
    """Represents a file or directory entry for UI display.

    Encapsulates all metadata needed for rendering file items in the file dialog,
    including formatted size, date, and appropriate icon tags. Immutable after creation.

    Attributes:
        name: Display name of the item (filename or directory name).
        path: Absolute filesystem path as a string.
        is_dir: True if the item is a directory, False otherwise.
        size_str: Human-readable size string (e.g., "1.2 KB", "DIR" for directories).
        date_str: Last modified timestamp formatted as "YYYY-MM-DD HH:MM".
        type_str: Type description ("Folder" for directories, file extension or "File" for files).
        icon_tag: Identifier for the icon to display (matches texture tags in Dear PyGui).
    """

    def __init__(
        self,
        name: str,
        path: str,
        is_dir: bool,
        size: int,
        mtime: float,
        icon_tag: str
    ):
        """Initializes a file item with raw filesystem data.

        Converts raw filesystem metadata into UI-ready formatted strings.
        Directories have special handling for size ("DIR") and type ("Folder").

        Args:
            name: Base name of the file/directory.
            path: Absolute filesystem path.
            is_dir: Whether the item is a directory.
            size: File size in bytes (ignored for directories).
            mtime: Last modification time as a Unix timestamp.
            icon_tag: Pre-determined icon identifier based on file type.
        """
        self.name = name
        self.path = path
        self.is_dir = is_dir
        self.size_str = self._format_size(size) if not is_dir else "DIR"
        self.date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        self.type_str = "Folder" if is_dir else (Path(name).suffix or "File")
        self.icon_tag = icon_tag

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Converts byte count to human-readable string.

        Uses standard binary prefixes (KB, MB, etc.) with one decimal place precision.

        Args:
            size_bytes: File size in bytes.

        Returns:
            Formatted size string (e.g., "1.2 KB", "345.0 B", "1.0 TB").

        Example:
            >>> FileItem._format_size(1536)
            '1.5 KB'
        """
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"


class FileScanner:
    """Scans filesystem directories and generates UI-ready file items.

    Handles platform-agnostic directory scanning with filtering capabilities.
    Applies hidden file rules, search queries, and extension filters before sorting results.

    Note:
        This class contains no UI dependencies - it operates purely on filesystem data
        and returns domain objects (FileItem instances).
    """

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
        """Initializes the scanner with filtering preferences.

        Args:
            show_hidden: Whether to include hidden files/directories (dotfiles on Unix).
            dirs_only: Whether to scan only directories (ignore files).
        """
        self.show_hidden = show_hidden
        self.dirs_only = dirs_only

    def scan_directory(
        self,
        path: Path,
        search_query: str = "",
        file_filter: str = ".*"
    ) -> List[FileItem]:
        """Scans a directory and returns filtered, sorted file items.

        Applies all configured filters (hidden files, directory-only mode), then applies
        search query and file extension filters. Results are sorted with directories first.

        Args:
            path: Directory path to scan.
            search_query: Optional case-insensitive substring filter for item names.
            file_filter: File extension filter (e.g., ".py", ".*" for all).

        Returns:
            List of FileItem objects ready for UI display, sorted with directories first.

        Raises:
            OSError: If the directory cannot be accessed (handled internally, returns empty list).
        """
        try:
            items = self._list_items(path)
            items = self._apply_filters(items, search_query, file_filter)
            items.sort(key=lambda x: (not x.is_dir, x.name.lower()))  # Directories first
            return [self._create_file_item(item) for item in items]
        except (OSError, PermissionError) as e:
            print(f"❌ Access denied to {path}: {e}")
            return []

    def _list_items(self, path: Path) -> List[Path]:
        """Retrieves raw filesystem items with basic filtering.

        Applies show_hidden and dirs_only rules at the filesystem level.

        Args:
            path: Directory path to enumerate.

        Returns:
            List of Path objects for visible items in the directory.
        """
        items = []
        for item in path.iterdir():
            if not self.show_hidden and item.name.startswith('.'):
                continue
            if self.dirs_only and not item.is_dir():
                continue
            items.append(item)
        return items

    def _apply_filters(
        self,
        items: List[Path],
        search_query: str,
        file_filter: str
    ) -> List[Path]:
        """Applies search and extension filters to items.

        Filters are applied sequentially: search query first, then file extension.

        Args:
            items: List of Path objects to filter.
            search_query: Case-insensitive substring to match in item names.
            file_filter: Extension filter ("*" matches all, ".ext" matches specific).

        Returns:
            Filtered list of Path objects.
        """
        if search_query:
            query = search_query.lower()
            items = [i for i in items if query in i.name.lower()]
        
        if file_filter != ".*":
            ext = file_filter.lower()
            items = [
                i for i in items
                if i.is_dir() or i.suffix.lower() == ext
            ]
        
        return items

    def _create_file_item(self, path: Path) -> FileItem:
        """Converts a filesystem path to a UI-ready FileItem.

        Handles permission errors gracefully by returning a special "access denied" item.

        Args:
            path: Filesystem path to convert.

        Returns:
            FileItem instance with formatted metadata and appropriate icon.
        """
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
        """Determines appropriate icon tag based on file extension.

        Uses internal mapping with fallback to default document icon.

        Args:
            path: Filesystem path to determine icon for.

        Returns:
            Icon tag identifier compatible with texture registry.
        """
        return self._ICON_MAP.get(path.suffix.lower(), self._DEFAULT_ICON)