from pathlib import Path
from typing import Any

import dearpygui.dearpygui as dpg

from Src.Nodes.abstract_node import AbstractNode
from Src.Config.Annotations import AFile, AEnum, ASequence


class ProjectDecoder:
    """
    Класс, инкапсулирующий логику десериализации сохраненного состояния проекта
    обратно в объекты Python. Симметричен ProjectEncoder.
    """

    _DESERIALIZERS: dict = {
        AFile:     lambda hint, val: [Path(p) for p in val],
        AEnum:     lambda hint, val: next((m for m in hint.source if m.value == val), None),
        ASequence: lambda hint, val: tuple(val),
    }

    @staticmethod
    def deserialize_value(hint: Any, value: Any) -> Any:
        """
        Преобразует JSON-совместимое значение обратно в исходный тип Python
        на основе словаря-диспетчера _DESERIALIZERS.
        """
        if value is None:
            return None

        hint_cls = hint if isinstance(hint, type) else type(hint)

        handler = ProjectDecoder._DESERIALIZERS.get(hint_cls)
        if handler:
            return handler(hint, value)

        return value

    @staticmethod
    def deserialize_node(node: AbstractNode, data: dict) -> bool:
        """
        Заполняет параметры воссозданного узла сохраненными значениями.
        """
        if "position" in data:
            dpg.set_item_pos(node.node_tag, data["position"])

        param_value = data.get("parameters", {})
        arguments = dpg.get_item_children(node.node_tag, slot=1)

        for argument in arguments:
            name = dpg.get_item_label(argument)

            if name not in node.annotations or name not in param_value:
                continue

            parameter = node.annotations[name]
            saved_val = param_value[name]

            python_val = ProjectDecoder.deserialize_value(parameter.hint, saved_val)

            if not parameter.set_value(argument, python_val):
                return False

        return True
