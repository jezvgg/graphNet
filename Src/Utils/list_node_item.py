import dearpygui.dearpygui as dpg

from Src.Config.Annotations import ABoolean, AEnum, AFloat, AInteger, ANode, AString
from Src.Config.node_annotation import NodeAnnotation
from Src.Managers import ThemeManager


BUTTON_HEIGHT: int = 32
LINE_HEIGHT: int = 30
PADDING: int = 8


class ListNodeItem:
    '''
    Виджет-имитация ноды для левой панели списка.
    Визуально повторяет структуру ноды в workspace: цветной заголовок,
    поля параметров, INPUT/OUTPUT метки.
    Является источником drag-and-drop для редактора.
    '''

    btn: int | str


    def __init__(self, node_data: NodeAnnotation, parent: int | str) -> None:
        '''
        Создаёт виджет-имитацию ноды в списке.

        Args:
            node_data: NodeAnnotation - аннотация ноды из node_list
            parent:    int | str      - родительский элемент (tree_node)
        '''
        theme_name: str = str(node_data.node_type.theme_name)
        node_colors: dict = ThemeManager._themes_config.get(theme_name, {}).get("mvNode", {})
        title_color: list[int] = node_colors.get("mvNodeCol_TitleBar", [50, 50, 50, 255])

        params: list[str] = [
            k for k, v in node_data.annotations.items()
            if k != 'INPUT' and not isinstance(v.hint, ANode)
        ]

        extra_lines: int = 1
        if node_data.input:
            extra_lines += 1
        if node_data.output:
            extra_lines += 1

        height: int = BUTTON_HEIGHT + (len(params) + extra_lines) * LINE_HEIGHT + PADDING

        with dpg.theme() as colored_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, title_color)

        with dpg.child_window(width=200, height=height, border=True,
                               parent=parent, user_data=node_data) as window:

            self.btn = dpg.add_button(label=node_data.label, width=-1)
            dpg.bind_item_theme(self.btn, colored_theme)
            with dpg.drag_payload(parent=self.btn, drag_data=window):
                dpg.add_text(node_data.label)

            if node_data.input:
                text: int | str = dpg.add_text("INPUT", indent=4)
                with dpg.drag_payload(parent=text, drag_data=window):
                    dpg.add_text(node_data.label)

            text = dpg.add_text("Docs", indent=4)
            with dpg.drag_payload(parent=text, drag_data=window):
                dpg.add_text(node_data.label)

            for label, parameter in node_data.annotations.items():
                if label == 'INPUT':
                    continue
                if isinstance(parameter.hint, ANode):
                    continue

                if isinstance(parameter.hint, AEnum):
                    dpg.add_combo(
                        label=label,
                        items=parameter.hint.items,
                        default_value=parameter.hint.items[0] if parameter.hint.items else "",
                        width=100,
                        enabled=False
                    )
                elif parameter.hint is ABoolean:
                    dpg.add_checkbox(label=label, enabled=False)
                elif parameter.hint is AInteger:
                    dpg.add_input_int(label=label, width=50, enabled=False)
                elif parameter.hint is AFloat:
                    dpg.add_input_float(label=label, width=50, enabled=False)
                elif parameter.hint is AString:
                    dpg.add_input_text(label=label, width=50, enabled=False)
                else:
                    text = dpg.add_text(label, indent=4)
                    with dpg.drag_payload(parent=text, drag_data=window):
                        dpg.add_text(node_data.label)

            if node_data.output:
                text = dpg.add_text("OUTPUT", indent=4)
                with dpg.drag_payload(parent=text, drag_data=window):
                    dpg.add_text(node_data.label)
