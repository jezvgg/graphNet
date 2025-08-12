from typing import Callable

import dearpygui.dearpygui as dpg
from keras import layers

from Src.Enums.attr_type import AttrType
from Src.Logging import Logger_factory, Logger
from Src.Nodes import AbstractNode, InputLayerNode
from Src.Config.node_list import NodeAnnotation, Parameter, ANode



class NodeBuilder:
    '''
    Класс реализующий логику связывания Keras и Нодов.

    Attributes:
        factory: InputsFactory - фабрика конвертации аннотаций в инпуты
        layers_list: dict[str: AbstractNode] - список слоёв с параметрами, которые использовать в конструкторе
    '''
    node_list: dict[str, dict[str, list[NodeAnnotation]]]
    delete_callback: Callable
    logger: Logger


    def __init__(self, 
                 node_list: dict[str: AbstractNode],
                 delete_callback: Callable):
        '''
        Args:
            layers_list: dict[str: AbstractNode] - список слоёв с параметрами, которые использовать в конструкторе
        '''
        self.logger = Logger_factory.from_instance()("nodes")
        self.delete_callback = delete_callback
        self.node_list = node_list


    def build_list(self, parent: str | int) -> str | int:
        '''
        Построить список (tree_node) из списка слоёв. Используется для панели слева в конструкторе.

        Args:
            parent: str | int - родительский элемент в котором создать список.

        Returns:
            str | int - индетификатор списка
        '''
        with dpg.group(parent=parent) as list:
            for anchor in self.node_list.keys():
                with dpg.tree_node(label=anchor) as tree_anchor:

                    for subanchor in self.node_list[anchor].keys():
                        with dpg.tree_node(label=subanchor) as tree_subanchor:

                            for node in self.node_list[anchor][subanchor]:
                                btn = dpg.add_button(label=node.label, user_data=node)
                                
                                with dpg.drag_payload(parent=btn, drag_data=btn):
                                    dpg.add_text(node.label)

        return list


    def build_node(self, node_data: NodeAnnotation, parent: str | int) -> str | int:
        '''
        Построение dpg.node из класса AbstractNode. Используется, для создания новых нодов в редакторе. Ноды берутся из user_data в списке слева.

        Args:
            node: AbstractNode - нода из которой создать dpg.node
            parent: str | int - родитель, внутри которого создать ноду. Чаще всего это dpg.node_editor.

        Returns:
            str | int - индетификатор новой dpg.node.
        '''
        node_id = dpg.generate_uuid()
        node: AbstractNode = node_data.node_type(node_id, **node_data.kwargs)

        with dpg.node(label=node_data.label, parent=parent, user_data=node, tag=node_id):
            if node.input:
                with dpg.node_attribute(label="INPUT", attribute_type=dpg.mvNode_Attr_Input):
                    dpg.add_text("INPUT")
                
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                with dpg.tree_node(label="Docs"):
                    dpg.add_text(node.docs)

            for label, attribute in node.annotations.items():
                self.logger.info(f"Attribute label: {label}")
                attr = attribute.build(label=label, parent=node_id)

            with dpg.node_attribute(label="Delete", attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_button(label="Delete", callback=lambda: self.delete_callback(node_id))

            if node.output:
                with dpg.node_attribute(label="OUTPUT", attribute_type=dpg.mvNode_Attr_Output):
                    dpg.add_text("OUTPUT")

        return node_id
    

    def build_input(self, parent: str | int) -> str | int:
        '''
        Особенный метод, реализующий построение слоя входа.

        Args:
            parent: str | int - родительский элемент в котором построить нод. Чаще всего node_editor.
            shape: tuple[int] - форма данных, передаётся в входной слой.

        Returns:
            str | int - индетификатор новой ноды
        '''
        layer = NodeAnnotation(
            label="Input",
            node_type=InputLayerNode, 
            logic = layers.Input,
            annotations = {
                    "shape": Parameter(AttrType.INPUT, ANode),
                }
            )

        node_id = self.build_node(layer, parent=parent)

        return node_id
    

    def compile_graph(self, start_nodes: list[AbstractNode]):
        '''
        Компиляция графа, от его концов. Работает через обход в ширину. Вызывает метод compile у нода, если все ноды, пришедшие к нему уже скомпилированы. Начинает с нодов, у которых нет входов.
        '''

        visited = set()
        queue = start_nodes[:]
        self.logger.info("Началась сборка графа.")

        while queue:
            current_node = queue.pop()
            self.logger.debug(f"Текущая очередь - {queue}")
            self.logger.debug(f"Текущая нода - {current_node}")

            if set(current_node.incoming.values()) | visited == visited:
                self.logger.debug("Нода подошла.")

                layer = current_node.compile()
                self.logger.debug(str(layer))

                for attr_id in current_node.outgoing.values():
                    neightbor: AbstractNode = dpg.get_item_user_data(dpg.get_item_parent(attr_id))
                    if neightbor not in queue:
                        queue = [neightbor] + queue

                visited.add(current_node)
