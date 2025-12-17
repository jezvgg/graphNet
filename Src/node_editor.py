import json
from typing import get_args
from pathlib import Path
import sys

import dearpygui.dearpygui as dpg

from Src.Nodes import AbstractNode, node_link
from Src.node_builder import NodeBuilder
from Src.Logging import Logger_factory, Logger
from Src.Config.node_list import node_list, NodeAnnotation
from Src.Config.Annotations import ANode



class NodeEditor:
    '''
    Класс реализующий логику управления нодами.

    Attributes:
        logger: Logger - логировщик
    '''
    logger: Logger
    builder: NodeBuilder
    __stage_tag: str | int
    __group_tag: str | int
    __start_nodes: list[AbstractNode]


    def __init__(self, *args, **kwargs):
        '''
        Вызвать окно, для создания графа. 

        Args:
            *args, **kwargs - передаются в dpg.node_editor
        '''
        self.logger = Logger_factory.from_instance()("nodes", config)
        self.builder = NodeBuilder(node_list, self.delete_node)
        self.__stage_tag = dpg.generate_uuid()
        self.__group_tag = dpg.generate_uuid()
        self.__start_nodes = []

        dpg.set_viewport_resize_callback(callback=self.on_viewport_resize_callback)

        with dpg.stage(tag=self.__stage_tag):
            # Делим окно на 2, чтоб слева были блоки, а справа конструктор графа
            with dpg.group(horizontal=True, tag=self.__group_tag) as group:

                self.builder.build_list(parent=group)

                # Именно в группу задаём drop_callback, который создаёт ноду по перетягиванию её с окна справа
                with dpg.group(tag="editor_group", drop_callback=self.drop_callback):
                    
                    # Используем редактор нодов из DearPyGUI
                    with dpg.node_editor(tag="node_editor", callback=self.link_callback, \
                                        delink_callback=self.delink_callback, *args, **kwargs):

                        input_id = self.builder.build_input("node_editor")
                        self.__start_nodes.append(dpg.get_item_user_data(input_id))

                    dpg.add_button(label="Собрать модель", 
                                   callback = lambda: self.builder.compile_graph(self.__start_nodes))
        
        self.on_viewport_resize_callback()


    def on_viewport_resize_callback(self, **kwargs):
        '''
        Callback для изменения размера node_editor'a
        '''
        if dpg.does_item_exist('node_editor'):
            dpg.configure_item('node_editor',height=dpg.get_viewport_height()*0.9)


    def drop_callback(self, sender: str | int, app_data: str | int) -> str | int:
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

        self.logger.info(f"Узел поставлен на позиции - {pos}")

        node_data: NodeAnnotation = dpg.get_item_user_data(app_data)
        node_id = self.builder.build_node(node_data, parent="node_editor")
        dpg.set_item_pos(node_id, pos)

        # Мы только создали узел и у него ещё нет связей
        self.__start_nodes.append(dpg.get_item_user_data(node_id))

        self.logger.debug(f"Start nodes: {self.__start_nodes}")

        return node_id


    def link_callback(self, sender: str | int, app_data: tuple[str | int, str | int]) -> str | int:
        '''
        Функция, которая вызывается, когда создаётся новая связь между нодами.

        Args:
            sender: int | str - зачастую является окном редакторивания графа (dpg.node_editor)
            app_data: tuple(str | int, str | int) - исходящие и приходящие атрибуты нодов.
        '''
        self.logger.debug(f"На вход пришло {app_data}")

        node_out: AbstractNode = dpg.get_item_user_data(dpg.get_item_parent(app_data[0]))
        node_in: AbstractNode = dpg.get_item_user_data(dpg.get_item_parent(app_data[1]))

        # Проверка при связывании, что правильные узлы связываются
        accaptable: ANode = node_in.annotations[dpg.get_item_label(app_data[1])].hint
        if not isinstance(node_out, accaptable.node_type):
            self.logger.warning(f"Некорректная попытка связывания узлов: {node_out} -> {node_in}({dpg.get_item_label(app_data[1])}) должно быть {accaptable.node_type}")
            return
        # Проверка, что не больше одной связи, если нужно
        if accaptable.single and dpg.get_item_user_data(app_data[1]):
            self.logger.warning(f"Некорректная попытка связывания узлов: {node_out} -> {node_in}({dpg.get_item_label(app_data[1])}) связей не может быть больше 1!")
            return

        self.logger.debug(f"Node_out - {dpg.get_item_label(dpg.get_item_parent(app_data[0]))}")

        link_id = dpg.add_node_link(app_data[0], app_data[1], parent=sender, user_data=node_link(app_data[0], app_data[1]))

        self.logger.debug(f"Связи до: {node_out} {node_in}")

        data_in: list | None = dpg.get_item_user_data(app_data[1])
        if not data_in: data_in = []
        data_in.append(app_data[0])
        dpg.set_item_user_data(app_data[1], data_in)

        data_out: list | None = dpg.get_item_user_data(app_data[0])
        if not data_out: data_out = []
        data_out.append(app_data[1])
        dpg.set_item_user_data(app_data[0], data_out)

        node_out.outgoing[app_data[0]] = data_out
        node_in.incoming[app_data[1]] = data_in

        if node_in in self.__start_nodes: self.__start_nodes.remove(node_in)

        self.logger.debug(f"Связи после: {node_out} {node_in}")

        self.logger.debug(f"Start nodes: {self.__start_nodes}")

        return link_id


    def delink_callback(self, sender: int | str, app_data: int | str):
        '''
        Функция, которая вызывается, когда убирается связь между нодами.

        Args:
            sender: int | str - зачастую является окном редакторивания графа (dpg.node_editor)
            app_data: str | int - связь между нодами (dpg.add_node_link)
        '''
        link: node_link = dpg.get_item_user_data(app_data)

        self.delink(link.outgoing, link.incoming)

        dpg.delete_item(app_data)


    def delink(self, attr_outgoing: str | int, attr_incoming: str | int):
        self.logger.debug(f"Связи до: {attr_outgoing} {attr_incoming}")

        node_out: AbstractNode = dpg.get_item_user_data(dpg.get_item_parent(attr_outgoing))
        node_in: AbstractNode = dpg.get_item_user_data(dpg.get_item_parent(attr_incoming))

        node_out.outgoing[attr_outgoing].remove(attr_incoming)
        node_in.incoming[attr_incoming].remove(attr_outgoing)

        dpg.set_item_user_data(attr_outgoing, node_out.outgoing[attr_outgoing])
        dpg.set_item_user_data(attr_incoming, node_in.incoming[attr_incoming])

        if not node_out.outgoing[attr_outgoing]: del node_out.outgoing[attr_outgoing]
        if not node_in.incoming[attr_incoming]: del node_in.incoming[attr_incoming]

        if not node_in.incoming: self.__start_nodes.append(node_in)

        self.logger.debug(f"Связи после: {attr_outgoing} {attr_incoming}")
        self.logger.debug(f"Start nodes: {self.__start_nodes}")


    def delete_node(self, node_id: str | int):
        '''
        Функция для удаления нода, вместе с его связями.

        Args:
            node_id: str | int - индетификатор нода, которого нужно удалить (dpg.node)
        '''
        node: AbstractNode = dpg.get_item_user_data(node_id)
        if len(dpg.get_item_children("node_editor", slot=1)) == 1 and \
            dpg.get_item_children("node_editor", slot=1)[0] == node_id:
            node.raise_error("Нельзя удалять узел, когда он один на поле!", 
                             "Некорректное действие пользователя")
            return
        
        # Удаляем связи с этим узлом

        incoming = node.incoming.copy()
        outgoing = node.outgoing.copy()

        for attr_in in incoming.keys():
            for attr_out in incoming[attr_in]:
                self.delink(attr_out, attr_in)

        for attr_out in outgoing.keys():
            for attr_in in outgoing[attr_out]:
                self.delink(attr_out, attr_in)
        
        if node in self.__start_nodes: self.__start_nodes.remove(node)

        del node
        dpg.delete_item(node_id)

        self.logger.debug(f"Start nodes: {self.__start_nodes}")


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