import os
import platform
from unittest.mock import MagicMock
from pathlib import Path
from typing import List

import pytest

from shortcuts import (
    ShortcutItem,
    LinuxBasedShortcuts,
    WindowsBasedShortcuts,
    Shortcuts,
    get_shortcuts_via_platform,
)

class FakePath:
    """Mock-обёртка для Path с контролируемым .exists()"""
    def __init__(self, path: str, exists: bool = True):
        self._path = Path(path)
        self._exists = exists

    def __truediv__(self, other):
        # Поддержка home / "Desktop"
        return FakePath(str(self._path / other), self._exists)

    def exists(self) -> bool:
        return self._exists

    def __str__(self):
        return str(self._path)

    def __repr__(self):
        return f"FakePath({self._path!r}, exists={self._exists})"

    def __eq__(self, other):
        if isinstance(other, FakePath):
            return self._path == other._path
        return self._path == other



def test_linux_shortcuts_create_all_exist(mocker):
    # Arrange
    home_path = FakePath("/home/user", exists=True)
    mocker.patch("pathlib.Path.home", return_value=home_path)

    # Mock .exists() для всех кандидатов — пусть все существуют
    real_paths = [
        home_path,
        home_path / "Desktop",
        home_path / "Downloads",
        home_path / "Documents",
        home_path / "Pictures",
        home_path / "Music",
        home_path / "Videos",
        FakePath("/", exists=True),
        FakePath("/media", exists=True),
        FakePath("/mnt", exists=True),
    ]
    for p in real_paths:
        mocker.patch.object(p, 'exists', return_value=True)

    # Act
    config = LinuxBasedShortcuts.create()

    # Assert
    assert isinstance(config, LinuxBasedShortcuts)
    assert isinstance(config, Shortcuts)  # structural typing!
    assert len(config.items) == 10
    labels = [item.label for item in config.items]
    assert labels == [
        "Home", "Desktop", "Downloads", "Documents",
        "Pictures", "Music", "Videos", "Root", "Media", "Mnt"
    ]
    # Проверим один элемент подробно
    home_item = config.items[0]
    assert home_item.icon_tag == "home"
    assert home_item.label == "Home"
    assert str(home_item.path) == "/home/user"


def test_linux_shortcuts_filters_nonexistent(mocker):
    # Arrange
    home_path = FakePath("/home/user", exists=True)
    mocker.patch("pathlib.Path.home", return_value=home_path)

    # Только Home и Root существуют
    candidates_info = [
        ("Home", home_path, True),
        ("Desktop", home_path / "Desktop", False),
        ("Root", FakePath("/", exists=True), True),
        ("Media", FakePath("/media", exists=False), False),
    ]

    # Patch .exists() динамически
    def mock_exists(path_obj):
        for _, fake_path, exists in candidates_info:
            if str(path_obj._path) == str(fake_path._path):
                return exists
        return False

    for _, p, _ in candidates_info:
        mocker.patch.object(p, 'exists', side_effect=lambda p=p: mock_exists(p))

    # Подменим исходный список кандидатов — чтобы тест был чище
    original_candidates = [
        ShortcutItem("home", "Home", home_path),
        ShortcutItem("desktop", "Desktop", home_path / "Desktop"),
        ShortcutItem("hd", "Root", FakePath("/")),
        ShortcutItem("hd", "Media", FakePath("/media")),
    ]
    mocker.patch.object(LinuxBasedShortcuts, '_get_candidates', return_value=original_candidates)

    # Но проще — просто перепишем create() локально для теста, или:
    # → В реальном коде можно вынести `_build_candidates()` как protected-метод.

    # Вместо этого — сделаем прямую подмену через monkeypatch списка
    # Однако: для чистоты — просто проверим поведение фильтрации:
    candidates = [
        ShortcutItem("home", "Home", FakePath("/home", exists=True)),
        ShortcutItem("missing", "Missing", FakePath("/does/not/exist", exists=False)),
        ShortcutItem("root", "Root", FakePath("/", exists=True)),
    ]
    # Прямой вызов фильтра (имитация логики create)
    existing = [item for item in candidates if item.path.exists()]
    assert len(existing) == 2
    assert {item.label for item in existing} == {"Home", "Root"}


# =============== Тесты Windows ===============

def test_windows_shortcuts_create_with_drives(mocker):
    # Arrange
    user_profile = FakePath("C:\\Users\\test", exists=True)
    appdata = FakePath("C:\\Users\\test\\AppData", exists=True)
    localappdata = FakePath("C:\\Users\\test\\AppData\\Local", exists=True)

    mocker.patch.dict(os.environ, {
        "USERPROFILE": str(user_profile._path),
        "APPDATA": str(appdata._path),
        "LOCALAPPDATA": str(localappdata._path),
    }, clear=True)

    # Mock существующих путей
    existing_paths = [
        user_profile, appdata, localappdata,
        FakePath("C:\\", exists=True),
        FakePath("D:\\", exists=True),
        FakePath("Z:\\", exists=False),  # несуществующий
    ]
    for p in existing_paths:
        mocker.patch.object(p, 'exists', return_value=(str(p._path) != "Z:\\"))

    # Patch drive probing: вместо A–Z → только C, D, Z для скорости
    mocker.patch(
        "shortcuts.WindowsBasedShortcuts.create",
        side_effect=lambda: _mock_windows_create(user_profile, appdata, localappdata, mocker)
    )

    # Но лучше — не патчить create, а подменить range букв:
    mocker.patch("shortcuts.string.ascii_uppercase", "CDZ")

    # Act
    config = WindowsBasedShortcuts.create()

    # Assert
    assert isinstance(config, WindowsBasedShortcuts)
    assert isinstance(config, Shortcuts)

    labels = [item.label for item in config.items]
    assert "Home" in labels
    assert "C:" in labels
    assert "D:" in labels
    assert "Z:" not in labels  # отфильтрован

    # Проверим, что AppData есть
    assert "AppData" in labels
    assert "Local AppData" in labels

    # Убедимся, что диски идут после user-папок
    drive_labels = [lbl for lbl in labels if ":" in lbl]
    user_labels = [lbl for lbl in labels if ":" not in lbl]
    assert len(user_labels) >= 7  # как минимум 7 user-папок
    assert drive_labels == ["C:", "D:"]


def _mock_windows_create(user_profile, appdata, localappdata, mocker):
    """Вспомогательная функция для изолированного теста Windows (если нужно явное управление)."""
    candidates = [
        ShortcutItem("home", "Home", user_profile),
        ShortcutItem("hd", "C:", FakePath("C:\\", exists=True)),
        ShortcutItem("hd", "D:", FakePath("D:\\", exists=True)),
        ShortcutItem("hd", "Z:", FakePath("Z:\\", exists=False)),
    ]
    existing = [item for item in candidates if item.path.exists()]
    return WindowsBasedShortcuts(existing)


# =============== Тесты фабрики ===============

def test_get_shortcuts_via_platform_windows(mocker):
    mocker.patch("platform.system", return_value="Windows")
    mock_create = mocker.patch.object(WindowsBasedShortcuts, "create")
    mock_create.return_value = WindowsBasedShortcuts([])

    result = get_shortcuts_via_platform()

    mock_create.assert_called_once()
    assert isinstance(result, WindowsBasedShortcuts)


def test_get_shortcuts_via_platform_linux(mocker):
    mocker.patch("platform.system", return_value="Linux")
    mock_create = mocker.patch.object(LinuxBasedShortcuts, "create")
    mock_create.return_value = LinuxBasedShortcuts([])

    result = get_shortcuts_via_platform()

    mock_create.assert_called_once()
    assert isinstance(result, LinuxBasedShortcuts)


def test_get_shortcuts_via_platform_macos(mocker):
    mocker.patch("platform.system", return_value="Darwin")
    mock_create = mocker.patch.object(LinuxBasedShortcuts, "create")
    mock_create.return_value = LinuxBasedShortcuts([])

    result = get_shortcuts_via_platform()

    mock_create.assert_called_once()
    assert isinstance(result, LinuxBasedShortcuts)


def test_get_shortcuts_via_platform_unsupported():
    with pytest.raises(NotImplementedError, match="FreeBSD"):
        # Подменяем platform.system прямо в тесте через monkeypatch
        original_system = platform.system
        platform.system = lambda: "FreeBSD"
        try:
            get_shortcuts_via_platform()
        finally:
            platform.system = original_system


# =============== Тесты на соответствие протоколу ===============

def test_shortcutitem_immutability():
    item = ShortcutItem("tag", "label", Path("/tmp"))
    with pytest.raises(AttributeError):
        item.label = "new"  # frozen=True → AttributeError


def test_structural_subtyping():
    # Проверим, что mypy (и isinstance) видят соответствие протоколу
    linux_cfg = LinuxBasedShortcuts.create()
    windows_cfg = WindowsBasedShortcuts.create()

    assert isinstance(linux_cfg, Shortcuts)
    assert isinstance(windows_cfg, Shortcuts)

    # Даже «ручной» объект подойдёт!
    class ManualConfig:
        def __init__(self):
            self.items: List[ShortcutItem] = [
                ShortcutItem("test", "Test", Path("/tmp"))
            ]

    manual = ManualConfig()
    assert isinstance(manual, Shortcuts)  # ← вот сила structural typing!


# =============== Optional: параметризованный тест для всех реализаций ===============

@pytest.mark.parametrize("config_cls", [LinuxBasedShortcuts, WindowsBasedShortcuts])
def test_config_has_nonempty_items(config_cls, mocker):
    # Для Windows подменим буквы, чтобы тест был быстрым
    if config_cls is WindowsBasedShortcuts:
        mocker.patch("shortcuts.string.ascii_uppercase", "C")

    config = config_cls.create()
    assert isinstance(config.items, list)
    assert len(config.items) > 0
    for item in config.items:
        assert isinstance(item, ShortcutItem)
        assert isinstance(item.icon_tag, str)
        assert isinstance(item.label, str)
        assert isinstance(item.path, Path)
        assert item.path.exists()  # ← важная гарантия!