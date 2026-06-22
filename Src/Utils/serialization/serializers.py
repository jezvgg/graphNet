import enum
from pathlib import Path
from functools import singledispatchmethod
import json 
import dearpygui.dearpygui as dpg

from Src.Nodes.abstract_node import AbstractNode
from Src.Enums.attr_type import AttrType
from Src.Config.Annotations import ANode




class ProjectEncoder(json.JSONEncoder):
    """
    Кастомный JSON-энкодер, инкапсулирующий в себе всю логику
    сериализации сложных и неизвестных типов данных.
    """


    @singledispatchmethod
    def serialize(self, obj: any) -> any:
        """
        Базовый метод диспетчеризации.
        Для стандартных типов данных (str, int, float, bool, list, dict)
        он просто возвращает значение как есть.
        """
        return obj


    @serialize.register(Path)
    def _serialize_path(self, obj: Path) -> str:
        """
        Преобразует объект pathlib.Path в строку.
        """
        return str(obj)


    @serialize.register(enum.Enum)
    def _serialize_enum(self, obj: enum.Enum) -> str:
        """
        Преобразует элемент Enum в его строковое значение.
        """
        return obj.value


    @serialize.register(tuple)
    def _serialize_tuple(self, obj: tuple) -> list:
        """
        Рекурсивно сериализует элементы кортежа и упаковывает их в список.
        """
        return [self.serialize(item) for item in obj]


    @serialize.register(AbstractNode)
    def _serialize_node(self, node: AbstractNode) -> dict:
        """
        Преобразует объект узла графа (AbstractNode) в JSON-совместимый словарь.
        """
        pos = dpg.get_item_pos(node.node_tag)

        param_values = {}
        arguments = dpg.get_item_children(node.node_tag, slot=1)
        
        for argument in arguments:
            name = dpg.get_item_label(argument)
            if name not in node.annotations:
                continue
            parameter = node.annotations[name]

            if parameter.attr_type in (AttrType.INPUT, AttrType.STATIC):
                if isinstance(parameter.hint, ANode) or parameter.hint is ANode:
                    continue

                raw_val = parameter.get_value(argument)
                param_values[name] = self.serialize(raw_val)

        return {
            "label": dpg.get_item_label(node.node_tag),
            "position": pos,
            "parameters": param_values
        }


    def default(self, obj: any) -> any:
        """
        Переопределенный стандартный метод JSON-энкодера.
        """
        try:
            return self.serialize(obj)
        except TypeError:
            return super().default(obj)
    

def serialize_project(nodes: list[AbstractNode]) -> dict:
    """
    Сериализует весь холст: преобразует граф узлов и связей
    в абстрактный JSON-совместимый формат, решая проблему динамических UUID.
    """
    node_tag_to_id = {node.node_tag: f"node_{i}" for i, node in enumerate(nodes)}
    
    serialized_nodes = []
    serialized_links = []

    encoder = ProjectEncoder()

    for node in nodes:
        node_data = encoder.serialize(node)

        node_data["id"] = node_tag_to_id(node.node_tag)
        serialized_nodes.append(node_data)
        for attr_incoming, attr_outgoing_list in node.incoming.items():

            receiver_pin_label = dpg.get_item_label(attr_incoming)

            for attr_outgoing in attr_outgoing_list:
                receiver_pin_label = dpg.get_item_label(attr_incoming)
                for attr_outgoing in attr_outgoing_list:
                    sender_node_tag = dpg.get_item_parent(attr_outgoing)
                    sender_node = dpg.get_item_user_data(sender_node_tag)
                    sender_pin_label = dpg.get_item_label(attr_outgoing)

                    link_data = {
                        "sender_node_id": node_tag_to_id[sender_node.node_tag],
                        "sender_pin": sender_pin_label,
                        "receiver_node_id": node_tag_to_id[node.node_tag],
                        "receiver_pin": receiver_pin_label
                    }
                    serialized_links.append(link_data)

    return {
        "nodes": serialized_nodes,
        "links": serialized_links
    }         
