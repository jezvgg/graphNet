import dearpygui.dearpygui as dpg
from Src.Utils.userdata import get_userdata, set_userdata, clear_userdata

def test_set_get_userdata_integer_id(env):
    # Create simple button to get a valid DPG integer ID
    btn = dpg.add_button(label="Test Button", parent=env)
    
    # 1. Test setting with default key "self"
    obj_self = {"name": "test_object"}
    res = set_userdata(btn, value=obj_self)
    assert res == obj_self
    assert get_userdata(btn) == obj_self
    assert get_userdata(btn, "self") == obj_self

    # Verify dpg's built-in userdata has the full dictionary
    expected_dpg_data = {"self": obj_self}
    assert dpg.get_item_user_data(btn) == expected_dpg_data

    # 2. Test setting with custom key
    res_custom = set_userdata(btn, key="custom_key", value="custom_value")
    assert res_custom == "custom_value"
    assert get_userdata(btn, "custom_key") == "custom_value"
    
    # Verify both keys exist in cache and DPG
    assert get_userdata(btn, "self") == obj_self
    assert dpg.get_item_user_data(btn) == {"self": obj_self, "custom_key": "custom_value"}

    # 3. Test non-existent keys
    assert get_userdata(btn, "non_existent_key") is None

    # 4. Test default value parameter for set_userdata
    res_none = set_userdata(btn, key="none_key")
    assert res_none is None
    assert get_userdata(btn, "none_key") is None


def test_set_get_userdata_string_id_and_alias(env):
    # Add alias and button
    alias = "my_custom_button_alias"
    btn = dpg.add_button(label="Button with Alias", tag=alias, parent=env)
    alias_id = dpg.get_alias_id(alias)
    assert btn == alias
    assert isinstance(alias_id, int)

    # Set user data using string ID (alias)
    obj = {"data": 123}
    res = set_userdata(alias, "self", obj)
    assert res == obj

    # Retrieve using string ID (alias)
    assert get_userdata(alias) == obj

    # Retrieve using integer ID (as string ID resolves to alias)
    assert get_userdata(alias_id) == obj

    # Verify key modification works using alias or alias_id interchangeably
    set_userdata(alias_id, "foo", "bar")
    assert get_userdata(alias, "foo") == "bar"
    assert get_userdata(alias_id, "foo") == "bar"


def test_clear_userdata_no_children(env):
    # Create simple button
    btn_parent = dpg.add_button(label="Parent Button", parent=env)
    set_userdata(btn_parent, "self", "parent_val")

    # Clear with children=False
    clear_userdata(btn_parent, children=False)
    assert get_userdata(btn_parent) is None


def test_clear_userdata_with_children(env):
    # Create group with buttons (children)
    group = dpg.add_group(parent=env)
    btn1 = dpg.add_button(label="Child 1", parent=group)
    btn2 = dpg.add_button(label="Child 2", parent=group)

    set_userdata(group, "self", "group_val")
    set_userdata(btn1, "self", "btn1_val")
    set_userdata(btn2, "self", "btn2_val")

    # Verify everything retrieved
    assert get_userdata(group) == "group_val"
    assert get_userdata(btn1) == "btn1_val"
    assert get_userdata(btn2) == "btn2_val"

    # Clear with children=True (default)
    clear_userdata(group)

    # Everything in the tree should be cleared
    assert get_userdata(group) is None
    assert get_userdata(btn1) is None
    assert get_userdata(btn2) is None


def test_clear_userdata_string_id_alias(env):
    alias = "clear_alias_btn"
    btn = dpg.add_button(label="Button", tag=alias, parent=env)
    alias_id = dpg.get_alias_id(alias)

    set_userdata(alias, "self", "alias_val")
    assert get_userdata(alias) == "alias_val"
    assert get_userdata(alias_id) == "alias_val"

    # Clear by alias string
    clear_userdata(alias, children=False)

    assert get_userdata(alias) is None
    assert get_userdata(alias_id) is None


def test_get_userdata_invalid_id():
    # Calling get_userdata with non-cached, non-dpg ID
    assert get_userdata(999999) is None
    assert get_userdata("non_existent_alias") is None
