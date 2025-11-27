import dearpygui.dearpygui as dpg

from typing import Dict, Set, Final

from pathlib import Path

import logging




ICON_NAMES: Final[Set[str]] = frozenset({
    # UI controls
    "add_file", "add_folder", "back", "refresh", "search",
    
    # Generic items
    "app", "document", "folder", "link", "note", "object", "script", "url",
    
    # File types
    "c", "iso", "python", "vector", "zip",
    
    # Media
    "music", "music_note", "picture", "video",
    
    # Folders (semantic)
    "desktop", "documents", "downloads", "home", "picture_folder", "videos",
    
    # Devices & system
    "gears", "hd", "big_picture", "mini_document", "mini_error", "mini_folder",
})

DEFAULT_ICON: Final[str] = "document"
FOLDER_ICON: Final[str] = "folder"


logger = logging.getLogger(__name__)


class IconHandler:
    """Handles loading, registration, and resolution of icons for Dear PyGui.

    Manages static textures for UI icons. Ensures every requested icon name
    either loads from disk or falls back to a safe default.

    Icons are registered with their base name as the Dear PyGui **tag**.
    
    Example:
        >>> handler = IconHandler(Path("assets/icons"))
        >>> handler.load_icons()
        >>> tag = handler.get_icon_tag("home")  # → "home"
        >>> dpg.add_image(tag)
    """

    def __init__(self, image_dir: Path):
        """Initialize handler with icon directory.

        Args:
            image_dir: Directory containing ``{name}.png`` icon files.
        """
        self.image_dir: Path = image_dir
        self.registered_icons: Dict[str, str] = {}  # name → tag (same)
        self._placeholder_data: Final[list] = [255, 255, 255, 255] * 4  # 2x2 white

    def load_icons(self) -> None:
        """Load and register all icons from `ICON_NAMES`.

        For each name in `ICON_NAMES`:
          - tries to load `{name}.png`,
          - falls back to 2x2 white placeholder if missing,
          - registers texture with `tag=name`.

        Raises:
            OSError: If `image_dir` is inaccessible.
        """
        if not self.image_dir.is_dir():
            raise ValueError(f"Icon directory does not exist: {self.image_dir}")

        with dpg.texture_registry():
            for name in ICON_NAMES:
                tag = self._register_icon(name)
                self.registered_icons[name] = tag

    def _register_icon(self, name: str) -> str:
        """Register a single icon texture and return its tag.

        Args:
            name: Icon base name (e.g., "home").

        Returns:
            Dear PyGui texture tag (same as `name`).

        Raises:
            ValueError: If `name` is not in `ICON_NAMES` (defensive).
        """
        if name not in ICON_NAMES:
            known = ", ".join(sorted(ICON_NAMES)[:5]) + ", ..."
            raise ValueError(f"Unknown icon name: {name!r}. Known: {known}")

        file_path = self.image_dir / f"{name}.png"
        width, height, channels, data = 16, 16, 4, self._placeholder_data.copy()

        if file_path.exists():
            try:
                width, height, channels, data = dpg.load_image(str(file_path.resolve()))
                logger.debug(f"Loaded icon: {name} ({width}x{height}, {channels}ch)")
            except Exception as e:
                logger.warning(f"Failed to load {file_path}: {e}. Using placeholder.")
        else:
            logger.warning(f"Icon file not found: {file_path}. Using placeholder.")

        # Dear PyGui requires tag to be str, and static textures are global
        tag = name
        dpg.add_static_texture(
            width=width,
            height=height,
            default_value=data,
            tag=tag,
        )
        return tag

    def get_icon_tag(self, name: str) -> str:
        """Get Dear PyGui texture tag for an icon name.

        Validates input and ensures the icon is registered.

        Args:
            name: Icon name (case-sensitive, must be in `ICON_NAMES`).

        Returns:
            Texture tag (same as `name`), ready for `dpg.add_image()`.

        Raises:
            KeyError: If icon is not registered (e.g., call before `load_icons()`).
        """
        if name not in self.registered_icons:
            raise KeyError(
                f"Icon '{name}' not registered. "
                f"Did you call `load_icons()`? Available: {sorted(self.registered_icons)}"
            )
        return self.registered_icons[name]

    def get_file_icon(self, path: Path) -> str:
        """Get icon tag for a file path (by extension or type).

        Rules:
          - Folders → "folder"
          - Known extensions → mapped icon (e.g., ".py" → "python")
          - Unknown → "document"

        Args:
            path: File or directory path.

        Returns:
            Valid icon tag.
        """
        if path.is_dir():
            return self.get_icon_tag(FOLDER_ICON)

        suffix = path.suffix.lower().lstrip(".")
        ext_map = {
            # Languages
            "c": "c",
            "h": "c",
            "py": "python",
            # Archives
            "zip": "zip",
            "rar": "zip",
            "7z": "zip",
            # Media
            "mp3": "music",
            "wav": "music",
            "png": "picture",
            "jpg": "picture",
            "jpeg": "picture",
            "mp4": "video",
            "avi": "video",
            # Documents
            "txt": "document",
            "pdf": "document",
            "doc": "document",
            "docx": "document",
        }

        icon_name = ext_map.get(suffix, DEFAULT_ICON)
        if icon_name in ICON_NAMES:
            return self.get_icon_tag(icon_name)
        return self.get_icon_tag(DEFAULT_ICON)