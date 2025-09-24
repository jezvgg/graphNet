from .config import FileDialogConfig
from .state import FileDialogState
from .core import FileDialogCore
from .ui import FileDialogUI
from typing import List

class FileDialog:
    def __init__(self, **kwargs):
        self.configure(**kwargs)
        self._result_ready = False
        self._result = []

    def configure(self, **kwargs):
        """Перенастраивает диалог без пересоздания UI."""
        self.config = FileDialogConfig(**kwargs)
        self.state = FileDialogState()
        self.core = FileDialogCore(self.config, self.state)
        # UI пересоздаётся только при первом show(), или можно обновить динамически
        if not hasattr(self, 'ui'):
            self.ui = FileDialogUI(self.core, self.config)
        else:
            # Можно обновить UI (например, заголовок окна)
            import dearpygui.dearpygui as dpg
            dpg.set_item_label(self.ui.window_tag, self.config.title)
            # Остальное состояние сбросится при refresh_directory()
            
            
    @staticmethod
    def _default_filter_list():
        return [
            ".*", ".exe", ".bat", ".sh", ".msi", ".apk", ".bin", ".cmd", ".com", ".jar", ".out", ".py", ".pyl", ".phs", ".js", ".json", ".java", ".c", ".cpp", ".cs", ".h", ".rs", ".vbs", ".php", ".pl", ".rb", ".go", ".swift", ".ts", ".asm", ".lua", ".sh", ".bat", ".r", ".dart", ".ps1", ".html", ".htm", ".xml", ".css", ".ini", ".yaml", ".yml", ".config", ".md", ".rst", ".txt", ".rtf", ".doc", ".docx", ".pdf", ".odt", ".tex", ".log", ".csv", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".svg", ".webp", ".ico", ".psd", ".ai", ".eps", ".tga", ".wav",
            ".mp3", ".ogg", ".flac", ".aac", ".m4a", ".wma", ".aiff", ".mid", ".midi", ".opus", ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mpeg", ".mpg", ".3gp", ".m4v", ".blend", ".fbx", ".obj", ".stl", ".3ds", ".dae", ".ply", ".glb", ".gltf", ".csv", ".sql", ".db", ".dbf", ".mdb", ".accdb", ".sqlite", ".xml", ".json", ".zip", ".rar", ".7z", ".tar", ".gz", ".iso", ".bz2", ".xz", ".tgz", ".cab", ".vdi", ".vmdk", ".vhd", ".vhdx", ".ova", ".ovf", ".qcow2", ".dockerfile", ".bak", ".old", ".sav", ".tmp", ".bk", ".ppack", ".mlt", ".torrent", ".ics"
        ]

    def show(self):
        self.ui.show()
        
    def show_and_get_result(self) -> List[str]:
        """
        Показывает диалог и блокирует выполнение до его закрытия.
        Возвращает список выбранных путей.
        """
        self.show()
        
        # Ждём, пока результат не будет готов
        while not self.core._result_ready:
            import dearpygui.dearpygui as dpg
            dpg.split_frame()  # отдаём управление DearPyGui
        
        return self.core._result
        