from pathlib import Path
import dearpygui.dearpygui as dpg

from Src.Managers.font_manager.font_manager import FontManager
from Src.Managers.size_manager import SizeManager
from Src.Utils.userdata import get_userdata, set_userdata


def test_size_manager_initialization(env):
    # Reset SizeManager singleton if it exists
    orig_cls = getattr(SizeManager, "__wrapped__", None)
    if orig_cls and hasattr(orig_cls, "__instance"):
        delattr(orig_cls, "__instance")

    # Setup FontManager and items first
    FontManager(Path("Assets/fonts_config.json"))

    # We need a node_editor to satisfy the constructor logic
    # "for item in {'node_editor'} | get_children('node_editor'):"
    editor = dpg.add_node_editor(tag="node_editor", parent=env)
    target_node = dpg.add_node(parent=editor)
    node_attr = dpg.add_node_attribute(parent=target_node)
    btn_child = dpg.add_button(label="Child", parent=node_attr)

    # Initialize SizeManager
    size_mgr = SizeManager()

    # Verify that the initial min_width / min_height are computed and saved in userdata
    assert get_userdata(editor, 'min_width') is not None
    assert get_userdata(editor, 'min_height') is not None
    assert get_userdata(btn_child, 'min_width') is not None
    assert get_userdata(btn_child, 'min_height') is not None


def test_size_manager_get_and_set_bbox(env):
    # Prepare FontManager and item
    FontManager(Path("Assets/fonts_config.json"))
    editor = dpg.add_node_editor(tag="node_editor", parent=env)
    
    size_mgr = SizeManager()

    # DPG height / width defaults to 0 if not explicitly set
    dpg.set_item_height(editor, 100)
    dpg.set_item_width(editor, 200)

    height, width = size_mgr.get_bbox(editor)
    assert height == 100
    assert width == 200

    # Set new bounding box
    size_mgr.set_bbox(editor, 150, 250)
    assert dpg.get_item_height(editor) == 150
    assert dpg.get_item_width(editor) == 250

    # Test that TEXT type is ignored by set_bbox as per its inline comment
    target_node = dpg.add_node(parent=editor)
    node_attr = dpg.add_node_attribute(parent=target_node)
    txt = dpg.add_text(default_value="Unchangeable text", parent=node_attr)
    
    # Text doesn't support width/height, get_bbox should return 0, 0
    assert size_mgr.get_bbox(txt) == (0, 0)

    # Calling set_bbox should return early and do nothing
    size_mgr.set_bbox(txt, 100, 200)
    assert size_mgr.get_bbox(txt) == (0, 0)


def test_size_manager_get_min_bbox(env):
    FontManager(Path("Assets/fonts_config.json"))
    editor = dpg.add_node_editor(tag="node_editor", parent=env)
    
    size_mgr = SizeManager()

    # Set initial userdata values
    set_userdata(editor, 'min_height', 50)
    set_userdata(editor, 'min_width', 120)

    height, width = size_mgr.get_min_bbox(editor)
    assert height == 50
    assert width == 120


def test_size_manager_transform(env):
    FontManager(Path("Assets/fonts_config.json"))
    editor = dpg.add_node_editor(tag="node_editor", parent=env)
    dpg.set_item_height(editor, 100)
    dpg.set_item_width(editor, 200)

    size_mgr = SizeManager()
    set_userdata(editor, 'min_height', 100)
    set_userdata(editor, 'min_width', 200)

    # Transform with ratio 1.5
    size_mgr.transform(editor, 1.5, children=False)
    assert dpg.get_item_height(editor) == 150
    assert dpg.get_item_width(editor) == 300


def test_size_manager_increase_and_reduce(env):
    # Ensure fonts mapped correctly
    font_mgr = FontManager(Path("Assets/fonts_config.json"))
    
    editor = dpg.add_node_editor(tag="node_editor", parent=env)
    dpg.set_item_height(editor, 100)
    dpg.set_item_width(editor, 200)

    size_mgr = SizeManager()

    # Minimum font size is 7, current default is 14
    min_font = font_mgr.fonts["notomono-regular.ttf"][7]
    set_userdata(editor, 'min_font_size', min_font)
    set_userdata(editor, 'min_height', 50)
    set_userdata(editor, 'min_width', 100)

    # Font size grows from 14 to 15. The new layout scale should be 15/7
    size_mgr.increase(editor, children=False)
    
    expected_ratio = 15 / 7
    assert dpg.get_item_height(editor) == int(50 * expected_ratio)
    assert dpg.get_item_width(editor) == int(100 * expected_ratio)

    # Font size reduces from 15 to 14. The new layout scale should be 14/7
    size_mgr.reduce(editor, children=False)
    
    expected_ratio_reduced = 14 / 7
    assert dpg.get_item_height(editor) == int(50 * expected_ratio_reduced)
    assert dpg.get_item_width(editor) == int(100 * expected_ratio_reduced)
