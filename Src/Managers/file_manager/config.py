from dataclasses import dataclass, field
from typing import List, Callable
from pathlib import Path

@dataclass
class FileDialogConfig:
    title: str = "File dialog"
    tag: str = "file_dialog"
    width: int = 950
    height: int = 650
    min_size: tuple = (460, 320)
    dirs_only: bool = False
    default_path: Path = field(default_factory=Path.cwd())
    filter_list: List[str] = field(default_factory=lambda: [
        ".*", ".exe", ".bat", ".sh", ".msi", ".apk", ".bin", ".cmd", ".com", ".jar", ".out", ".py", ".pyl", ".phs", ".js", ".json", ".java", ".c", ".cpp", ".cs", ".h", ".rs", ".vbs", ".php", ".pl", ".rb", ".go", ".swift", ".ts", ".asm", ".lua", ".sh", ".bat", ".r", ".dart", ".ps1", ".html", ".htm", ".xml", ".css", ".ini", ".yaml", ".yml", ".config", ".md", ".rst", ".txt", ".rtf", ".doc", ".docx", ".pdf", ".odt", ".tex", ".log", ".csv", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".svg", ".webp", ".ico", ".psd", ".ai", ".eps", ".tga", ".wav",
        ".mp3", ".ogg", ".flac", ".aac", ".m4a", ".wma", ".aiff", ".mid", ".midi", ".opus", ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mpeg", ".mpg", ".3gp", ".m4v", ".blend", ".fbx", ".obj", ".stl", ".3ds", ".dae", ".ply", ".glb", ".gltf", ".csv", ".sql", ".db", ".dbf", ".mdb", ".accdb", ".sqlite", ".xml", ".json", ".zip", ".rar", ".7z", ".tar", ".gz", ".iso", ".bz2", ".xz", ".tgz", ".cab", ".vdi", ".vmdk", ".vhd", ".vhdx", ".ova", ".ovf", ".qcow2", ".dockerfile", ".bak", ".old", ".sav", ".tmp", ".bk", ".ppack", ".mlt", ".torrent", ".ics"
    ])
    file_filter: str = ".*"
    callback: Callable= lambda x: print("ARE YOU STUPID?")
    show_dir_size: bool = False
    allow_drag: bool = True
    multi_selection: bool = True
    show_shortcuts_menu: bool = True
    no_resize: bool = True
    modal: bool = True
    show_hidden_files: bool = False
    user_style: int = 0