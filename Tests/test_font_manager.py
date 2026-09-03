from pathlib import Path
import dearpygui.dearpygui as dpg

from Src.Managers.font_manager.font_manager import FontManager
from Src.Managers.font_manager.font import FontUnit
from Src.Utils.userdata import get_userdata


def test_font_manager_default_config(env):
    manager = FontManager(Path("Assets/fonts_config.json"))
    
    # Verify fonts map is populated
    assert "notomono-regular.ttf" in manager.fonts
    
    # Verify default FontUnit
    default_font = manager.default
    assert isinstance(default_font, FontUnit)
    assert default_font.name == "notomono-regular.ttf"
    assert default_font.size == 14
    assert default_font.id is not None

    # Create dummy item and verify get returns default font
    btn = dpg.add_button(label="Dummy", parent=env)
    font = manager.get(btn)
    assert font == default_font


def test_font_manager_set_and_get(env):
    manager = FontManager(Path("Assets/fonts_config.json"))
    btn = dpg.add_button(label="Test Button", parent=env)

    # Set to a non-default size (e.g., 20)
    font_20 = manager.set(btn, font_name="notomono-regular.ttf", size=20)
    assert isinstance(font_20, FontUnit)
    assert font_20.size == 20

    # Verify get returns this font
    retrieved_font = manager.get(btn)
    assert retrieved_font == font_20

    # Verify DPG's item config reflects the font ID
    assert dpg.get_item_font(btn) == font_20.id

    # Verify min font size is set in userdata to 7 (smallest configured size)
    min_font = get_userdata(btn, "min_font_size")
    assert isinstance(min_font, FontUnit)
    assert min_font.size == 7


def test_font_manager_increase_and_reduce(env):
    manager = FontManager(Path("Assets/fonts_config.json"))
    btn = dpg.add_button(label="Test Button", parent=env)

    # Set to size 14
    manager.set(btn, size=14)
    assert manager.get(btn).size == 14

    # Increase font. The configured sizes are [7, 8, 9, 10, 11, 12, 13, 14, 15, ...]
    # So increasing from 14 should change it to 15.
    increased_font = manager.increase(btn)
    assert increased_font.size == 15
    assert manager.get(btn).size == 15

    # Reduce font from 15 should go back to 14
    reduced_font = manager.reduce(btn)
    assert reduced_font.size == 14
    assert manager.get(btn).size == 14


def test_font_manager_boundaries(env):
    manager = FontManager(Path("Assets/fonts_config.json"))
    btn = dpg.add_button(label="Test Button", parent=env)

    # 1. Test minimum size boundary (7)
    manager.set(btn, size=7)
    assert manager.get(btn).size == 7

    # Reducing a minimum size font should keep it at 7
    reduced_font = manager.reduce(btn)
    assert reduced_font.size == 7
    assert manager.get(btn).size == 7

    # 2. Test maximum size boundary (72)
    manager.set(btn, size=72)
    assert manager.get(btn).size == 72

    # Increasing a maximum size font should keep it at 72
    increased_font = manager.increase(btn)
    assert increased_font.size == 72
    assert manager.get(btn).size == 72
