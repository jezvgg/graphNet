import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from icon_handler import IconHandler, ICON_NAMES, DEFAULT_ICON, FOLDER_ICON




@pytest.fixture
def fs() -> FakeFilesystem:
    """pyfakefs fixture — virtual in-memory filesystem."""
    # Автоматически активируется pytest-pyfakefs
    pass


@pytest.fixture
def icon_dir(fs: FakeFilesystem) -> Path:
    """Create a virtual icon directory with a few real and missing icons."""
    icon_path = Path("/assets/icons")
    fs.create_dir(icon_path)

    # Create some real icons (as empty files — content doesn't matter for load_image mock)
    for name in ["home", "folder", "document", "python"]:
        fs.create_file(icon_path / f"{name}.png", contents=b"fake_png_data")

    # Leave others missing (e.g., "music", "video", "gears")
    return icon_path


@pytest.fixture
def mock_dpg(mocker):
    """Mock Dear PyGui functions used in IconHandler."""
    mock_registry = mocker.MagicMock()
    mock_add_static_texture = mocker.patch("dearpygui.dearpygui.add_static_texture")
    mock_load_image = mocker.patch("dearpygui.dearpygui.load_image")

    # Simulate dpg.load_image: return (16, 16, 4, [fake RGBA data])
    mock_load_image.side_effect = lambda path: (
        16, 16, 4, [100, 150, 200, 255] * (16 * 16)
    )

    return {
        "add_static_texture": mock_add_static_texture,
        "load_image": mock_load_image,
    }


@pytest.fixture
def handler(icon_dir: Path, mock_dpg) -> IconHandler:
    """IconHandler instance ready for testing."""
    return IconHandler(icon_dir)



def test_init(handler: IconHandler, icon_dir: Path):
    assert handler.image_dir == icon_dir
    assert handler.registered_icons == {}


def test_load_icons_registers_all(handler: IconHandler, mock_dpg, caplog):
    # Act
    with caplog.at_level(logging.WARNING):
        handler.load_icons()

    # Assert
    # 1. Все имена из ICON_NAMES зарегистрированы
    assert set(handler.registered_icons.keys()) == ICON_NAMES

    # 2. add_static_texture вызван для каждого
    assert mock_dpg["add_static_texture"].call_count == len(ICON_NAMES)

    # 3. Для существующих иконок load_image вызван
    existing_icons = {"home", "folder", "document", "python"}
    assert mock_dpg["load_image"].call_count == len(existing_icons)
    for name in existing_icons:
        mock_dpg["load_image"].assert_any_call(str(handler.image_dir / f"{name}.png"))

    # 4. Предупреждения только для отсутствующих иконок
    missing_count = len(ICON_NAMES - existing_icons)
    warning_logs = [r for r in caplog.records if r.levelname == "WARNING"]
    assert len(warning_logs) == missing_count
    assert all("not found" in r.message for r in warning_logs)


def test_get_icon_tag_valid(handler: IconHandler):
    handler.load_icons()
    tag = handler.get_icon_tag("home")
    assert tag == "home"


def test_get_icon_tag_invalid_name_raises(handler: IconHandler):
    handler.load_icons()
    with pytest.raises(ValueError, match="Unknown icon name"):
        handler._register_icon("nonexistent_icon")  # private, но проверяем логику


def test_get_icon_tag_before_load_raises(handler: IconHandler):
    with pytest.raises(KeyError, match="not registered"):
        handler.get_icon_tag("home")


def test_get_file_icon(handler: IconHandler):
    handler.load_icons()

    # Папка → folder
    folder_path = Path("/home/user/Documents")
    # В pyfakefs по умолчанию нет путей — создадим как dir
    from pyfakefs.fake_filesystem import set_uid
    handler.image_dir.fs.create_dir(folder_path)
    assert handler.get_file_icon(folder_path) == handler.get_icon_tag(FOLDER_ICON)

    # Файл с известным расширением
    assert handler.get_file_icon(Path("script.py")) == handler.get_icon_tag("python")
    assert handler.get_file_icon(Path("data.zip")) == handler.get_icon_tag("zip")

    # Неизвестное расширение → document
    assert handler.get_file_icon(Path("file.xyz")) == handler.get_icon_tag(DEFAULT_ICON)

    # Без расширения → document
    assert handler.get_file_icon(Path("Makefile")) == handler.get_icon_tag(DEFAULT_ICON)


def test_placeholder_used_for_missing_icons(handler: IconHandler, mock_dpg, fs: FakeFilesystem):
    # Удалим один из "существующих" файлов после инициализации
    (handler.image_dir / "home.png").unlink()

    handler.load_icons()

    # load_image не должен вызываться для home.png
    calls = [str(call) for call in mock_dpg["load_image"].call_args_list]
    assert "home.png" not in str(calls)

    # Но add_static_texture — вызван для всех
    assert mock_dpg["add_static_texture"].call_count == len(ICON_NAMES)

    # Проверим, что данные placeholder использованы (по умолчанию [255,255,255,255] * 4)
    # Соберём все default_value из вызовов
    placeholder_4px = [255, 255, 255, 255] * 4
    for call in mock_dpg["add_static_texture"].call_args_list:
        kwargs = call.kwargs
        if kwargs["tag"] == "home":
            assert kwargs["default_value"] == placeholder_4px
            assert kwargs["width"] == 16
            assert kwargs["height"] == 16
            break
    else:
        pytest.fail("home icon registration not found")


def test_directory_validation(handler: IconHandler, fs: FakeFilesystem):
    # Удалим директорию
    handler.image_dir.rmdir()
    with pytest.raises(ValueError, match="does not exist"):
        handler.load_icons()


def test_icon_handler_with_shortcuts(handler: IconHandler, mocker):
    # Подменим shortcuts, чтобы они использовали известные icon_tag
    from shortcuts import ShortcutItem

    handler.load_icons()

    # Пример ярлыка из LinuxBasedShortcuts
    item = ShortcutItem(icon_tag="home", label="Home", path=Path("/home/user"))
    tag = handler.get_icon_tag(item.icon_tag)
    assert tag == "home"  # и точно зарегистрирован

    # Проверим, что все shortcut.icon_tag из ваших классов — валидны
    valid_shortcut_icon_tags = {
        "home", "desktop", "downloads", "documents",
        "picture_folder", "music", "videos", "hd",
    }
    for tag in valid_shortcut_icon_tags:
        assert tag in ICON_NAMES, f"Shortcut icon '{tag}' not in ICON_NAMES!"
        # И можно получить
        assert handler.get_icon_tag(tag) == tag



def test_image_load_failure_fallback(handler: IconHandler, mock_dpg, caplog):
    # Заставим dpg.load_image кинуть исключение для "document.png"
    def failing_load(path):
        if "document.png" in path:
            raise RuntimeError("Corrupted PNG")
        return 16, 16, 4, [0, 0, 0, 255] * 256

    mock_dpg["load_image"].side_effect = failing_load

    with caplog.at_level(logging.WARNING):
        handler.load_icons()

    # Должно быть предупреждение про "document.png"
    assert any("Corrupted PNG" in r.message for r in caplog.records)
    assert any("Using placeholder" in r.message for r in caplog.records)

    # И document всё равно зарегистрирован (через placeholder)
    assert "document" in handler.registered_icons