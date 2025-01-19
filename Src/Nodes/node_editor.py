import json

import dearpygui.dearpygui as dpg

from Src.page import Page
from Src.Logging import Logger_factory, Logger
from Src.Nodes import Node, node_link, NodeBuilder, layers_list, Layer


class NodeEditor(Page):
    '''
    Является страницей, конструктором графа неронной сети.

    Класс реализующий логику управления нодами.

    Attributes:
        logger: Logger - логировщик
    '''
    logger: Logger
    builder: NodeBuilder


    def __init__(self, *args, **kwargs):
        '''
        Вызвать окно, для создания графа. 

        Args:
            *args, **kwargs - передаются в dpg.node_editor
        '''
        super().__init__()

        with open("Src/Logging/logger_config_debug.json") as f:
            config = json.load(f)

        self.logger = Logger_factory.from_instance()("nodes", config)
        self.builder = NodeBuilder(layers_list)

        with dpg.stage(tag=self.stage_tag):
            # Делим окно на 2, чтоб слева были блоки, а справа конструктор графа
            with dpg.group(horizontal=True, tag=self.page_tag) as group:

                self.builder.build_list(parent=group)

                # Именно в группу задаём drop_callback, который создаёт ноду по перетягиванию её с окна справа
                with dpg.group(tag="editor_group", drop_callback=self.drop_callback):
                    
                    # Используем редактор нодов из DearPyGUI
                    with dpg.node_editor(tag="node_editor", callback=self.link_callback, \
                                        delink_callback=self.delink_callback, *args, **kwargs):

                        input_id = self.builder.build_input("node_editor", shape=(28, 28, 1))

                    dpg.add_button(label="Собрать модель", callback=lambda: self.builder.build_model(dpg.get_item_user_data(input_id)))


    def drop_callback(self, sender: str | int, app_data: str | int):
        '''
        Функция, которая выполняется, при перетягивания блока в окно редакторования графа. Создаём новую ноду в окне.

        Args:
            sender: str | int - зачастую является окном редакторивания графа (dpg.node_editor)
            app_data: str | int - элемент, который перетащили.
        '''
        self.logger.debug(f"На вход пришло {sender}, {app_data}, {dpg.get_item_user_data(app_data)}")

        # Реализовать создание нода, через обычные координаты мыши не получится
        # потому что координаты в node_editor отличаются от координат мыши
        # поэтому координаты размещения нового нода рассчитываются относительно уже стоящего нода (input_node)
        pos = dpg.get_mouse_pos(local=False)
        ref_node = dpg.get_item_children("node_editor", slot=1)[0]
        ref_screen_pos = dpg.get_item_rect_min(ref_node)
        ref_grid_pos = dpg.get_item_pos(ref_node)

        NODE_PADDING = (8, 8)

        pos[0] = pos[0] - (ref_screen_pos[0] - NODE_PADDING[0]) + ref_grid_pos[0]
        pos[1] = pos[1] - (ref_screen_pos[1] - NODE_PADDING[1]) + ref_grid_pos[1]

        self.logger.info(f"Рассчитанная позиция - {pos}")

        node: Layer = dpg.get_item_user_data(app_data)
        node_id = self.builder.build_node(node, parent="node_editor")
        dpg.set_item_pos(node_id, pos)


    def link_callback(self, sender: str | int, app_data: tuple[str | int, str | int]):
        '''
        Функция, которая вызывается, когда создаётся новая связь между нодами.

        Args:
            sender: int | str - зачастую является окном редакторивания графа (dpg.node_editor)
            app_data: tuple(str | int, str | int) - исходящий и приходящий нод.
        '''
        self.logger.debug(f"На вход пришло {app_data}")

        node_out: Node = dpg.get_item_user_data(dpg.get_item_parent(app_data[0]))
        node_in: Node = dpg.get_item_user_data(dpg.get_item_parent(app_data[1]))

        self.logger.debug(f"Node_out - {dpg.get_item_label(dpg.get_item_parent(app_data[0]))}")

        dpg.add_node_link(app_data[0], app_data[1], parent=sender, user_data=node_link(node_out, node_in))

        self.logger.debug(f"Связи до: {node_out} {node_in}")

        node_out.add_link(node_in)

        self.logger.debug(f"Связи после: {node_out} {node_in}")

        # Для дебага
        # Node.print_tree(dpg.get_item_user_data("node_input"))


    def delink_callback(self, sender: int | str, app_data: int | str):
        '''
        Функция, которая вызывается, когда создаётся убирается связь между нодами.

        Args:
            sender: int | str - зачастую является окном редакторивания графа (dpg.node_editor)
            app_data: str | int - связь между нодами (dpg.add_node_link)
        '''
        link: node_link = dpg.get_item_user_data(app_data)

        self.logger.debug(f"Связи до: {link.outcoming} {link.incoming}")

        link.outcoming.remove_link(link.incoming)

        self.logger.debug(f"Связи после: {link.outcoming} {link.incoming}")

        dpg.delete_item(app_data)


    def delete_node(self, node_id: str | int):
        '''
        Функция для удаления нода, вместе с его связями.

        Args:
            node_id: str | int - индетификатор нода, которого нужно удалить (dpg.node)
        '''
        node_data: Node = dpg.get_item_user_data(node_id)
        
        node_data.delete()

        dpg.delete_item(node_id)
