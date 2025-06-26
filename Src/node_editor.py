import json

import dearpygui.dearpygui as dpg

from Src.Nodes import AbstractNode, node_link
from Src.node_builder import NodeBuilder
from Src.Logging import Logger_factory, Logger
from Src.Nodes.node_list import node_list, listNode
from Src.size_manager import SizeManager


class NodeEditor:
    '''
    Класс реализующий логику управления нодами.

    Attributes:
        logger: Logger - логировщик
        builder: NodeBuilder - построитель узлов
        size_manager: SizeManager - менеджер размеров и шрифтов
    '''
    logger: Logger
    builder: NodeBuilder
    __stage_tag: str | int
    __group_tag: str | int

    size_manager: SizeManager

    def __init__(self,
                 size_manager: SizeManager,
                 *args, **kwargs):
        '''
        Инициализирует редактор узлов.

        Args:
            size_manager (SizeManager): Менеджер размеров и шрифтов.
            *args, **kwargs: Аргументы, передаваемые в dpg.node_editor.
        '''

        self.size_manager = size_manager

        with open("Src/Logging/logger_config_debug.json") as f:
            config = json.load(f)

        self.logger = Logger_factory.from_instance()("nodes", config)
        self.builder = NodeBuilder(node_list)
        self.__stage_tag = dpg.generate_uuid()
        self.__group_tag = dpg.generate_uuid()

        dpg.set_viewport_resize_callback(callback=self.on_viewport_resize_callback)
        with dpg.handler_registry():
            dpg.add_mouse_wheel_handler(callback=self.mouse_wheel_zoom_callback)

        with dpg.stage(tag=self.__stage_tag):
            # Делим окно на 2, чтоб слева были блоки, а справа конструктор графа
            with dpg.group(horizontal=True, tag=self.__group_tag) as group:
                self.builder.build_list(parent=group)

                # Именно в группу задаём drop_callback, который создаёт ноду по перетягиванию её с окна справа
                with dpg.group(tag="editor_group", drop_callback=self.drop_callback):
                    # Используем редактор нодов из DearPyGUI
                    with dpg.node_editor(tag="node_editor", callback=self.link_callback, \
                                         delink_callback=self.delink_callback, *args, **kwargs) as self.node_editor:
                        input_id = self.builder.build_input("node_editor", shape=(8, 8, 1))
                        # Применяем начальный шрифт к input_node через size_manager
                        dpg.bind_item_font(input_id, self.size_manager.node_font)

                    dpg.add_button(label="Собрать модель", callback=self.builder.compile_graph)

    def mouse_wheel_zoom_callback(self, sender: str | int, app_data: float):
        '''
        Callback для масштабирования с помощью колеса мыши.
        Масштабирует редактор узлов, если зажат Shift и курсор над редактором ('editor_group').
        В противном случае масштабирует всё приложение, если зажат Shift.

        Args:
            sender: Идентификатор отправителя события (handler_registry).
            app_data: Данные события (значение прокрутки колеса мыши, float).
        '''

        if dpg.is_key_down(dpg.mvKey_LShift):
            item_processed_for_zoom = False
            for item in dpg.get_all_items():
                item_state = dpg.get_item_state(item)
                if 'hovered' in item_state and item_state['hovered']:
                    item_type = dpg.get_item_type(item)
                    if item_type == 'mvAppItemType::mvNode':
                        self.size_manager.resize_object(item, app_data)
                        item_processed_for_zoom = True
                    elif item_type == 'mvAppItemType::mvWindowAppItem':
                        self.size_manager.resize_global(app_data)
                        item_processed_for_zoom = True

            if not item_processed_for_zoom:
                self.size_manager.resize_node_editor(self.node_editor,app_data)

    def on_viewport_resize_callback(self, sender, app_data):
        '''
        Callback для изменения размера node_editor'a
        '''
        if dpg.does_item_exist('node_editor'):
            dpg.configure_item('node_editor', height=dpg.get_viewport_height() * 0.9)

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

        node_data: listNode = dpg.get_item_user_data(app_data)
        node_id = self.builder.build_node(node_data, parent="node_editor")
        dpg.set_item_pos(node_id, pos)

        dpg.bind_item_font(node_id, self.size_manager.node_font)


    def link_callback(self, sender: str | int, app_data: tuple[str | int, str | int]):
        '''
        Функция, которая вызывается, когда создаётся новая связь между нодами.

        Args:
            sender: int | str - зачастую является окном редакторивания графа (dpg.node_editor)
            app_data: tuple(str | int, str | int) - исходящий и приходящий нод.
        '''
        self.logger.debug(f"На вход пришло {app_data}")

        node_out: AbstractNode = dpg.get_item_user_data(dpg.get_item_parent(app_data[0]))
        node_in: AbstractNode = dpg.get_item_user_data(dpg.get_item_parent(app_data[1]))

        self.logger.debug(f"Node_out - {dpg.get_item_label(dpg.get_item_parent(app_data[0]))}")

        dpg.add_node_link(app_data[0], app_data[1], parent=sender, user_data=node_link(node_out, node_in))

        self.logger.debug(f"Связи до: {node_out} {node_in}")

        data: list | None = dpg.get_item_user_data(app_data[1])
        if not data: data = []
        data.append(node_out)
        dpg.set_item_user_data(app_data[1], data)

        node_out.outcoming.append(node_in)
        node_in.incoming.append(node_out)

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

        link.outcoming.outcoming.remove(link.incoming)
        link.incoming.incoming.remove(link.outcoming)

        self.logger.debug(f"Связи после: {link.outcoming} {link.incoming}")

        dpg.delete_item(app_data)


    def delete_node(self, node_id: str | int):
        '''
        Функция для удаления нода, вместе с его связями.

        Args:
            node_id: str | int - индетификатор нода, которого нужно удалить (dpg.node)
        '''
        node_data: AbstractNode = dpg.get_item_user_data(node_id)

        # TODO Вынести логику из AbstractNode
        node_data.delete()

        dpg.delete_item(node_id)


    def show(self, parent: str | int):
        '''
        Отобразить элемент.

        Args:
            parent: str | int - родительское окно в котором отобразить.
        '''
        dpg.move_item(self.__group_tag, parent=parent)


    def hide(self):
        '''
        Спрятать элемент
        '''
        dpg.move_item(self.__group_tag, parent=self.__stage_tag)
