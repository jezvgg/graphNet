import dearpygui.dearpygui as dpg

def on_viewport_resize_callback(**kwargs):
    '''
    Callback для изменения размера node_editor'a
    '''
    if dpg.does_item_exist('node_editor'):
        dpg.configure_item('node_editor',height=dpg.get_viewport_height()*0.9)

    modal_windows = [
        "error_window",
        "fit_window",
        ]

    for window in modal_windows:
        if dpg.does_item_exist(window):
            dpg.set_item_pos(window, [(dpg.get_viewport_width() - dpg.get_item_width(window)) //2,(dpg.get_viewport_height() - dpg.get_item_height(window)) // 2])