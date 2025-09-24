from dataclasses import dataclass, field
from typing import List, Optional, Callable
import os
@dataclass
class FileDialogConfig:
    title: str = "File dialog"
    tag: str = "file_dialog"
    width: int = 950
    height: int = 650
    min_size: tuple = (460, 320)
    dirs_only: bool = False
    default_path: str = field(default_factory=os.getcwd)
    filter_list: List[str] = field(default_factory=lambda: [
        ".*", ".exe", ".bat", ".sh", ".msi", ".apk", ".bin", ".cmd", ".com", ".jar", ".out", ".py", ".pyl", ".phs", ".js", ".json", ".java", ".c", ".cpp", ".cs", ".h", ".rs", ".vbs", ".php", ".pl", ".rb", ".go", ".swift", ".ts", ".asm", ".lua", ".sh", ".bat", ".r", ".dart", ".ps1", ".html", ".htm", ".xml", ".css", ".ini", ".yaml", ".yml", ".config", ".md", ".rst", ".txt", ".rtf", ".doc", ".docx", ".pdf", ".odt", ".tex", ".log", ".csv", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".svg", ".webp", ".ico", ".psd", ".ai", ".eps", ".tga", ".wav",
        ".mp3", ".ogg", ".flac", ".aac", ".m4a", ".wma", ".aiff", ".mid", ".midi", ".opus", ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mpeg", ".mpg", ".3gp", ".m4v", ".blend", ".fbx", ".obj", ".stl", ".3ds", ".dae", ".ply", ".glb", ".gltf", ".csv", ".sql", ".db", ".dbf", ".mdb", ".accdb", ".sqlite", ".xml", ".json", ".zip", ".rar", ".7z", ".tar", ".gz", ".iso", ".bz2", ".xz", ".tgz", ".cab", ".vdi", ".vmdk", ".vhd", ".vhdx", ".ova", ".ovf", ".qcow2", ".dockerfile", ".bak", ".old", ".sav", ".tmp", ".bk", ".ppack", ".mlt", ".torrent", ".ics"
    ])
    file_filter: str = ".*"
    callback: Optional[Callable] = None
    show_dir_size: bool = False
    allow_drag: bool = True
    multi_selection: bool = True
    show_shortcuts_menu: bool = True
    no_resize: bool = True
    modal: bool = True
    show_hidden_files: bool = False
    user_style: int = 0

@dataclass
class ShortcutItem:
    icon_tag: str      # например, "home", "hard_disk"
    label: str         # например, "Home", "C:\\"
    path: str          # реальный путь, который будет установлен при клике

@dataclass
class BaseShortcutsConfig:
    """Базовый класс конфигурации ярлыков. Все платформы должны его реализовывать."""
    items: List[ShortcutItem]
    
    
    
import os
from pathlib import Path

@dataclass
class LinuxBasedConfig(BaseShortcutsConfig):
    def __init__(self):
        home = Path.home()
        self.items = [
            ShortcutItem("home", "Home", home),
            ShortcutItem("desktop", "Desktop", home / "Desktop"),
            ShortcutItem("downloads", "Downloads", home / "Downloads"),
            ShortcutItem("documents", "Documents", home / "Documents"),
            ShortcutItem("picture_folder", "Pictures", home / "Pictures"),
            ShortcutItem("music", "Music", home / "Music"),
            ShortcutItem("videos", "Videos", home / "Videos"),
            ShortcutItem("hd", "Root", Path("/")),
            ShortcutItem("hd", "Media", Path("/media")),
            ShortcutItem("hd", "Mnt", Path("/mnt")),
        ]
        
        self.items = filter(lambda x: x.path.exists(), self.items)
        
    
import os

@dataclass
class WindowsBasedConfig(BaseShortcutsConfig):
    def __init__(self):
        user_profile = Path(os.environ.get("USERPROFILE", "C:\\"))
        appdata = Path(os.environ.get("APPDATA", user_profile / "AppData"))
        localappdata = os.environ.get("LOCALAPPDATA", user_profile / "AppData" / "Local")

        self.items = [
            ShortcutItem("home", "Home", user_profile),
            ShortcutItem("desktop", "Desktop", user_profile / "Desktop"),
            ShortcutItem("downloads", "Downloads", user_profile / "Downloads"),
            ShortcutItem("documents", "Documents", user_profile / "Documents"),
            ShortcutItem("picture_folder", "Pictures", user_profile / "Pictures"),
            ShortcutItem("music", "Music", user_profile / "Music"),
            ShortcutItem("videos", "Videos", user_profile / "Videos"),
            ShortcutItem("hd", "AppData", appdata),
            ShortcutItem("hd", "Local AppData", localappdata),
        ]

        
        # Добавляем доступные диски: C:\, D:\, ...
        import string
        for drive_letter in string.ascii_uppercase:
            drive = Path(f"{drive_letter}:\\")
            self.items.append(ShortcutItem("hd", f"{drive_letter}:", drive))
                
        self.items = filter(lambda x: x.path.exist(), self.items)
                
                
import platform

def get_shortcuts_config() -> BaseShortcutsConfig:
    system = platform.system()
    if system == "Windows":
        return WindowsBasedConfig()
    elif system in ("Linux", "Darwin"): 
        return LinuxBasedConfig()
    else:
        home = os.path.expanduser("~")
        return BaseShortcutsConfig([
            ShortcutItem("home", "Home", home)
        ])