import dearpygui.dearpygui as dpg
from Src.Utils.children import get_children

def test_get_children_empty(env):
    # Button is a leaf element and has no children
    btn = dpg.add_button(label="Leaf", parent=env)
    assert get_children(btn) == set()


def test_get_children_flat(env):
    # Setup a parent group with multiple direct children
    group = dpg.add_group(parent=env)
    btn1 = dpg.add_button(label="Child 1", parent=group)
    btn2 = dpg.add_button(label="Child 2", parent=group)
    text1 = dpg.add_text(default_value="Child 3", parent=group)

    # Calling with default slot and depth (None)
    result = get_children(group)
    assert result == {btn1, btn2, text1}


def test_get_children_nested_no_depth(env):
    # Parent (Group) -> Child (Sub-group) -> Grandchildren (Buttons)
    parent_group = dpg.add_group(parent=env)
    child_group = dpg.add_group(parent=parent_group)
    btn_grandchild1 = dpg.add_button(label="Grandchild 1", parent=child_group)
    btn_grandchild2 = dpg.add_button(label="Grandchild 2", parent=child_group)

    # Without depth restriction, should gather all descendants recursively
    result = get_children(parent_group)
    assert result == {child_group, btn_grandchild1, btn_grandchild2}


def test_get_children_nested_with_depth(env):
    # Parent -> Level 1 (group) -> Level 2 (sub_group) -> Level 3 (button)
    level0 = dpg.add_group(parent=env)
    level1 = dpg.add_group(parent=level0)
    level2 = dpg.add_group(parent=level1)
    level3 = dpg.add_button(label="Leaf Button", parent=level2)

    # 1. Depth = 1: should return only Level 1 items
    assert get_children(level0, depth=1) == {level1}

    # 2. Depth = 2: should return Level 1 and Level 2 items
    assert get_children(level0, depth=2) == {level1, level2}

    # 3. Depth = 3: should return Level 1, 2, and 3 items
    assert get_children(level0, depth=3) == {level1, level2, level3}

    # 4. Depth = 10 (exceeds actual depth): should return everything
    assert get_children(level0, depth=10) == {level1, level2, level3}


def test_get_children_with_aliases(env):
    parent_alias = "parent_container_alias"
    child_alias = "child_button_alias"
    
    parent_win = dpg.add_window(tag=parent_alias)
    btn_child = dpg.add_button(tag=child_alias, parent=parent_alias)

    child_integer_id = dpg.get_alias_id(child_alias)

    # Verify lookups by string/alias
    children_by_alias = get_children(parent_alias)
    assert children_by_alias == {child_integer_id}

    # Verify lookups by integer ID
    parent_integer_id = dpg.get_alias_id(parent_alias)
    children_by_id = get_children(parent_integer_id)
    assert children_by_id == {child_integer_id}

def test_get_children_different_slots(env):
    # DPG items can have children in different slots (slot=0, slot=1, slot=2 etc.)
    # For example, node_editor nodes are typically in slot 1.
    # We can test by query on standard items where we specify children slots.
    # Although slot 1 is standard for most, we check slot 2 returns empty or valid container children.
    group = dpg.add_group(parent=env)
    btn = dpg.add_button(label="Child in default slot", parent=group)

    # Slot 1 is the default and should have the button
    assert get_children(group, slot=1) == {btn}

    # Slot 2 should be empty
    assert get_children(group, slot=2) == set()
