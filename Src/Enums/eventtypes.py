from enum import Enum

import dearpygui.dearpygui as dpg




class EventType(Enum):
    """
    Перечисление типов событий, сопоставленных с соответствующими
    функциями-создателями обработчиков в DearPyGui.
    """

    # Обработчики специфичные для объектов
    CLICK = dpg.add_item_clicked_handler
    DOUBLE_CLICK = dpg.add_item_double_clicked_handler
    HOVER = dpg.add_item_hover_handler
    FOCUS = dpg.add_item_focus_handler
    VISIBLE = dpg.add_item_visible_handler
    ACTIVATED = dpg.add_item_activated_handler
    DEACTIVATED = dpg.add_item_deactivated_handler
    EDITED = dpg.add_item_edited_handler
    RESIZED = dpg.add_item_resize_handler

    # Глобальные обработчики
    KEY_PRESS = dpg.add_key_press_handler
    KEY_RELEASE = dpg.add_key_release_handler
    KEY_DOWN = dpg.add_key_down_handler
    MOUSE_CLICK = dpg.add_mouse_click_handler
    MOUSE_DOUBLE_CLICK = dpg.add_mouse_double_click_handler
    MOUSE_DOWN = dpg.add_mouse_down_handler
    MOUSE_RELEASE = dpg.add_mouse_release_handler
    MOUSE_WHEEL = dpg.add_mouse_wheel_handler
    MOUSE_MOVE = dpg.add_mouse_move_handler
    MOUSE_DRAG = dpg.add_mouse_drag_handler

    # Обработчик для viewport'а
    VIEWPORT_RESIZE = dpg.set_viewport_resize_callback