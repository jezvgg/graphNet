import os
import platform

from dataclasses import dataclass

from typing import Protocol, List

from pathlib import Path




@dataclass(frozen=True)
class ShortcutItem:
    """Represents a single shortcut entry in the file manager sidebar.

    Each shortcut has a symbolic icon, human-readable label, and a canonical filesystem path.
    Shortcuts are immutable and intended for UI rendering and navigation.
    """
    icon_tag: str      #: Icon identifier (e.g., "home", "hd", "folder").
    label: str         #: Display name shown to the user (e.g., "Documents", "C:").
    path: Path         #: Absolute filesystem path to navigate to on activation.


@dataclass(frozen=True)
class LinuxBasedShortcuts:
    """Configuration for Linux and macOS (Darwin) desktop environment shortcuts.

    Provides a curated list of conventional user directories and system mount points
    commonly found on Unix-like systems. Follows XDG Base Directory Specification
    and typical desktop environment (GNOME, KDE, etc.) conventions.

    The ``items`` list is filtered to include only *existing and accessible* paths,
    ensuring robustness in minimal or non-standard environments (e.g., servers,
    containers, or custom setups without ~/Videos).

    Note:
        - Paths like ``~/Desktop`` may be localized (e.g., ``~/Рабочий стол``),
          but this implementation assumes English or symlinked standard names.
        - ``/media`` and ``/mnt`` are included as conventional mount points,
          but filtered out if absent (common on headless systems).
    """
    items: List[ShortcutItem]

    @classmethod
    def create(cls) -> "LinuxBasedShortcuts":
        """Construct a Linux/macOS-specific shortcuts configuration.

        Detects the current user's home directory and builds a list of standard
        shortcuts, then filters out non-existent paths.

        Returns:
            A new :class:`LinuxBasedShortcuts` instance with validated shortcuts.

        Example:
            >>> cfg = LinuxBasedShortcuts.create()
            >>> "Home" in [item.label for item in cfg.items]
            True
        """
        home = Path.home()
        candidates = [
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
        existing = [item for item in candidates if item.path.exists()]
        return cls(existing)
    
@staticmethod
def _get_drive_letters() -> str:
    return "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

@dataclass(frozen=True)
class WindowsBasedShortcuts:
    """Configuration for Windows desktop environment shortcuts.

    Provides a list of standard user profile directories and system drives,
    respecting Windows environment variables (``USERPROFILE``, ``APPDATA``, etc.).

    Includes:
      - Core user folders (Desktop, Documents, etc.),
      - Application data locations (AppData, LocalAppData),
      - All detected fixed and removable drives (C:\\, D:\\, …).

    Drives are probed heuristically via drive letters A–Z; only existing,
    accessible roots are retained. Network or disconnected drives are excluded.

    Note:
        - Paths are case-insensitive but stored in conventional uppercase form (e.g., "C:\\").
        - ``AppData`` and ``LocalAppData`` may be hidden in Explorer, but are valid and
          frequently used by power users and developers.
    """
    items: List[ShortcutItem]

    @classmethod
    def create(cls) -> "WindowsBasedShortcuts":
        """Construct a Windows-specific shortcuts configuration.

        Uses environment variables to locate user directories, then enumerates
        available drive letters (A–Z), testing existence of each root (e.g., ``C:\\``).

        Returns:
            A new :class:`WindowsBasedShortcuts` instance with platform-native shortcuts.

        Example:
            >>> cfg = WindowsBasedShortcuts.create()
            >>> any(item.label == "C:" for item in cfg.items)
            True
        """
        user_profile = Path(os.environ.get("USERPROFILE", "C:\\"))
        appdata = Path(os.environ.get("APPDATA", user_profile / "AppData"))
        localappdata = Path(os.environ.get("LOCALAPPDATA", user_profile / "AppData" / "Local"))

        candidates = [
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

        # Probe all possible drive letters (A–Z)
        possible_letters = _get_drive_letters()
        for drive_letter in possible_letters.upper():
            drive = Path(f"{drive_letter}:\\")
            try:
                # exists() on Windows may trigger autorun prompts for removable media;
                # is_dir() is safer, but root is always a dir if exists
                if drive.exists():
                    candidates.append(ShortcutItem("hd", f"{drive_letter}:", drive))
            except OSError:
                # Skip inaccessible drives (e.g., CD-ROM without disc)
                continue

        # Filter to existing paths (some user dirs may be missing)
        existing = [item for item in candidates if item.path.exists()]
        return cls(existing)
    

class Shortcuts(Protocol):
    """Protocol describing the configuration interface for platform-specific sidebar shortcuts.

    A conforming class must provide a read-only list of :class:`ShortcutItem` instances.
    The list should reflect user-accessible, existing directories typical for the host OS
    (e.g., Home, Desktop, system drives).

    This protocol enables structural subtyping: no inheritance is required —
    only the presence of the ``items`` attribute with the correct type.

    Example:
        >>> cfg = LinuxBasedShortcuts.create()
        >>> isinstance(cfg, Shortcuts)
        True
        >>> len(cfg.items) > 0
        True
    """

    @property
    def items(self) -> List[ShortcutItem]:
        """List of shortcut entries available on the current platform.

        The list is:
        - Sorted in UI display order (not alphabetically),
        - Filtered to include only existing paths,
        - Immutable (recommended to use frozen dataclasses or tuples).

        Returns:
            A non-empty list of :class:`ShortcutItem` instances.
        """
        ...

def get_shortcuts_via_platform() -> Shortcuts:
    """Factory function that returns a platform-appropriate shortcuts configuration.

    Detects the current operating system via :func:`platform.system()` and instantiates
    the corresponding configuration class that satisfies the :class:`Shortcuts` protocol.

    Supported platforms:
      - **Windows**: returns :class:`WindowsBasedShortcuts`
      - **Linux** / **macOS** (Darwin): returns :class:`LinuxBasedShortcuts`

    The returned object is guaranteed to have an ``items`` attribute containing
    a list of existing, user-relevant directory shortcuts.

    Returns:
        A platform-specific instance conforming to the :class:`Shortcuts` protocol.

    Raises:
        NotImplementedError: If the current OS is not supported (e.g., " FreeBSD", "Java", etc.).

    Example:
        >>> config = get_shortcuts_via_platform()
        >>> isinstance(config, Shortcuts)
        True
        >>> all(item.path.exists() for item in config.items)
        True
    """
    system = platform.system()
    if system == "Windows":
        return WindowsBasedShortcuts.create()
    elif system in ("Linux", "Darwin"): 
        return LinuxBasedShortcuts.create()
    else:
        raise NotImplementedError(
            f"Shortcuts configuration is not implemented for OS: {system!r}"
        )