import dearpygui.dearpygui as dpg
from Src.Managers.event_manager import EventManager
from Src.Enums.eventtypes import EventType


def test_event_manager_add_item_handler(env):
    event_manager = EventManager()
    btn = dpg.add_button(label="Test Button", parent=env)
    
    called_args = []
    def handle_click(sender, app_data):
        called_args.append((sender, app_data))

    event_manager.add(EventType.CLICK, item_id=btn, handler=handle_click, user_data="btn_data")

    # Get handlers registry from DPG
    registry_id = dpg.get_item_info(btn).get("handlers")
    assert registry_id is not None
    assert dpg.does_item_exist(registry_id)

    # Get click handler from the registry
    handlers = dpg.get_item_children(registry_id, slot=1)
    assert len(handlers) == 1
    click_handler = handlers[0]

    # Retrieve and call the registered DPG callback function
    callback = dpg.get_item_configuration(click_handler).get("callback")
    assert callback is not None

    callback("test_btn_sender", "test_app_data")
    assert called_args == [("test_btn_sender", "test_app_data")]


def test_event_manager_add_global_handler(env):
    event_manager = EventManager()
    
    called_args = []
    def handle_key_press(sender, app_data):
        called_args.append((sender, app_data))

    event_manager.add(EventType.KEY_PRESS, handler=handle_key_press)

    global_reg = event_manager._EventManager__global_handler_registry
    assert global_reg is not None
    assert dpg.does_item_exist(global_reg)

    handlers = dpg.get_item_children(global_reg, slot=1)
    assert len(handlers) >= 1
    
    # Locate the most recently added key handler
    key_handler = handlers[-1]
    callback = dpg.get_item_configuration(key_handler).get("callback")
    assert callback is not None

    callback("keyboard_sender", "key_code_value")
    assert called_args == [("keyboard_sender", "key_code_value")]


def test_event_manager_add_viewport_handler(env, monkeypatch):
    event_manager = EventManager()
    
    called_with_callback = []
    def mock_set_viewport_resize_callback(callback):
        called_with_callback.append(callback)

    # Register the mock function in factorymethod
    original_func = dpg.set_viewport_resize_callback
    EventManager.add.registry[mock_set_viewport_resize_callback] = EventManager.add.registry[original_func]

    monkeypatch.setattr(EventType, "VIEWPORT_RESIZE", mock_set_viewport_resize_callback)

    called_args = []
    def handle_resize(sender, app_data):
        called_args.append((sender, app_data))

    event_manager.add(EventType.VIEWPORT_RESIZE, handler=handle_resize)

    # Verify that mock_set_viewport_resize_callback was invoked
    assert len(called_with_callback) == 1
    callback_wrapper = called_with_callback[0]

    # Verify calling the callback triggers the handler
    callback_wrapper("viewport_sender", "resize_app_data")
    assert called_args == [("viewport_sender", "resize_app_data")]


def test_event_manager_clear(env):
    event_manager = EventManager()
    btn = dpg.add_button(label="Clear Test Button", parent=env)

    called = []
    event_manager.add(EventType.CLICK, item_id=btn, handler=lambda s, a: called.append(1))

    # Clear handlers for the button
    registry_id = dpg.get_item_info(btn).get("handlers")
    assert registry_id is not None
    assert dpg.does_item_exist(registry_id)

    event_manager.clear(btn)

    # Verify DPG handlers registry is deleted
    assert not dpg.does_item_exist(registry_id)

    # Verify internal calls cache for this item is empty
    assert len(event_manager._EventManager__items_calls[btn]) == 0
