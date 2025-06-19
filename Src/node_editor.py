import json

import dearpygui.dearpygui as dpg

from Src.Nodes import AbstractNode, node_link
from Src.node_builder import NodeBuilder
from Src.Logging import Logger_factory, Logger
from Src.Nodes.node_list import node_list, listNode
from Src.font_manager import FontManager


class NodeEditor:
    '''
    Класс реализующий логику управления нодами.

    Attributes:
        logger: Logger - логировщик
        builder: NodeBuilder - построитель узлов
        font_manager: FontManager - менеджер шрифтов
    '''
    logger: Logger
    builder: NodeBuilder
    __stage_tag: str | int
    __group_tag: str | int

    font_manager: FontManager
    current_node_font_size: int
    min_node_font_size_limit: int
    max_node_font_size_limit: int

    max_font_scale: float = 2.0
    min_font_scale: float = 0.5
    font_scale_increment: float = 0.1
    current_app_font_scale: float = 1.0


    def __init__(self,
                 font_manager: FontManager,
                 initial_node_font_size: int,
                 min_node_font_size_limit: int = 8,
                 max_node_font_size_limit: int = 28,
                 *args, **kwargs):
        '''
        Инициализирует редактор узлов.

        Args:
            font_manager (FontManager): Менеджер шрифтов для управления шрифтами узлов.
            initial_node_font_size (int): Начальный размер шрифта для узлов.
            min_node_font_size_limit (int, optional): Минимальный допустимый размер шрифта для узлов. По умолчанию 8.
            max_node_font_size_limit (int, optional): Максимальный допустимый размер шрифта для узлов. По умолчанию 28.
            *args, **kwargs: Аргументы, передаваемые в dpg.node_editor.
        '''

        self.font_manager = font_manager
        self.min_node_font_size_limit = min_node_font_size_limit
        self.max_node_font_size_limit = max_node_font_size_limit

        self.current_node_font_size = max(
            self.min_node_font_size_limit,
            min(self.max_node_font_size_limit, initial_node_font_size)
        )

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
                                         delink_callback=self.delink_callback, *args, **kwargs):

                        input_id = self.builder.build_input("node_editor", shape=(8, 8, 1))

                    dpg.add_button(label="Собрать модель", callback=self.builder.compile_graph)


    def zoom_global(self, zoom_delta: float):
        '''
        Изменяет глобальный масштаб шрифта приложения.

        Args:
            zoom_delta (float): Значение изменения масштаба. Положительное для увеличения, отрицательное для уменьшения.
                                Обычно это значение от app_data при событии колеса мыши.
        '''
        self.current_app_font_scale += zoom_delta * self.font_scale_increment
        self.current_app_font_scale = max(self.min_font_scale,
                                          min(self.max_font_scale, self.current_app_font_scale))
        dpg.set_global_font_scale(self.current_app_font_scale)
        self.logger.info(f'Глобальный масштаб шрифта в приложении: {self.current_app_font_scale:.2f}')


    def zoom_node_editor(self, zoom: int):
        '''
        Изменяет размер шрифта для всех узлов в редакторе узлов.

        Args:
            zoom (int): Значение изменения размера шрифта. Положительное для увеличения, отрицательное для уменьшения.
                        Обычно это значение от app_data при событии колеса мыши.
        '''
        self.current_node_font_size += zoom
        self.current_node_font_size = max(self.min_node_font_size_limit,
                                          min(self.max_node_font_size_limit, self.current_node_font_size))

        node_ids = dpg.get_item_children('node_editor', slot=1)
        node_font = self.font_manager.get_node_font_by_size(self.current_node_font_size)

        if not node_font:
            self.logger.warning(
                f"Не удалось получить шрифт узла для размера {self.current_node_font_size}. Масштабирование шрифта узлов не будет применено.")
            return

        for node_id in node_ids:
            if dpg.does_item_exist(node_id) and dpg.get_item_info(node_id)['type'] == "mvAppItemType::mvNode":
                dpg.bind_item_font(node_id, node_font)

        self.logger.info(f'Размер шрифта редактора узлов изменен на: {self.current_node_font_size}')


    def mouse_wheel_zoom_callback(self, sender: str | int, app_data: float):
        '''
        Callback для масштабирования с помощью колеса мыши.
        Масштабирует редактор узлов, если зажат Shift и курсор над редактором ('editor_group').
        В противном случае масштабирует всё приложение, если зажат Shift.

        Args:
            sender: Идентификатор отправителя события (handler_registry).
            app_data: Данные события (значение прокрутки колеса мыши, float).
        '''
        mouse_pos = dpg.get_mouse_pos(local=False)
        is_over_editor = False

        editor_rect_min = dpg.get_item_rect_min('editor_group')
        editor_rect_max = dpg.get_item_rect_max('editor_group')
        if editor_rect_min and editor_rect_max:
            is_over_editor = (editor_rect_min[0] <= mouse_pos[0] <= editor_rect_max[0] and
                              editor_rect_min[1] <= mouse_pos[1] <= editor_rect_max[1])

        if dpg.is_key_down(dpg.mvKey_LShift):
            if is_over_editor:
                self.zoom_node_editor(int(app_data))
            else:
                self.zoom_global(app_data)


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

        current_node_font_tag = self.font_manager.get_node_font_by_size(self.current_node_font_size)
        dpg.bind_item_font(node_id, current_node_font_tag)


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
