import dearpygui.dearpygui as dpg


from Src.Config.node_annotation import NodeAnnotation
from Src.Managers import ThemeManager
from Src.Config.Annotations import AEnum, ABoolean, AInteger, ANode

BUTTON_HEIGHT = 32
LINE_HEIGHT = 30
PADDING = 8


class ListNodeItem:
    btn: int | str

    def __init__(self, node_data: NodeAnnotation, parent: int | str):
        theme_name = str(node_data.node_type.theme_name)
        node_colors = ThemeManager._themes_config.get(theme_name, {}).get("mvNode", {})
        title_color = node_colors.get("mvNodeCol_TitleBar", [50, 50, 50, 255])
        height = 50
        params = [k for k in node_data.annotations if k != 'INPUT']

        extra_lines = 1
        if node_data.input:
            extra_lines += 1
        if node_data.output:
            extra_lines += 1

        height = BUTTON_HEIGHT + (len(params) + extra_lines) * LINE_HEIGHT + PADDING

        with dpg.theme() as colored_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, title_color)
      
        with dpg.child_window(width = 200, height = height, border=True,
                               parent=parent, user_data = node_data) as window:
          
#          with dpg.drag_payload(parent = window, drag_data = window):
#              dpg.add_text(node_data.label)
          self.btn = dpg.add_button(label = node_data.label, width = -1)
          dpg.bind_item_theme(self.btn, colored_theme)
          with dpg.drag_payload(parent = self.btn, drag_data = window):
              dpg.add_text(node_data.label)

          if node_data.input:
              text = dpg.add_text("INPUT", indent = 4)
              with dpg.drag_payload(parent = text, drag_data = window):
                  dpg.add_text(node_data.label)

          text = dpg.add_text("Docs", indent = 4)
          with dpg.drag_payload(parent = text, drag_data = window):
              dpg.add_text(node_data.label)
            
          for label, parameter in node_data.annotations.items():
              text = dpg.add_text(label, indent = 4)
              with dpg.drag_payload(parent = text, drag_data = window):
                dpg.add_text(node_data.label)

          if node_data.output:
              text = dpg.add_text("OUTPUT", indent = 4)
              with dpg.drag_payload(parent = text, drag_data = window):
                  dpg.add_text(node_data.label)
