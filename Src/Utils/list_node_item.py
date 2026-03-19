import dearpygui.dearpygui as dpg
from Src.Config.node_annotation import NodeAnnotation
from Src.Managers import ThemeManager

class ListNodeItem:
    btn: int | str

    def __init__(self, node_data: NodeAnnotation, parent: int | str):
        theme_name = str(node_data.node_type.theme_name)
        node_colors = ThemeManager._themes_config.get(theme_name, {}).get("mvNode", {})
        title_color = node_colors.get("mvNodeCol_TitleBar", [50, 50, 50, 255])

        with dpg.theme() as colored_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, title_color)

        with dpg.child_window(width=200, height=50, border=True, parent=parent):
            self.btn = dpg.add_button(label=node_data.label, user_data=node_data, width=-1)
            dpg.bind_item_theme(self.btn, colored_theme)
            
