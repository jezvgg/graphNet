from pathlib import Path
from typing import Any 

import dearpygui.dearpygui as dpg

from Src.Nodes.abstract_node import AbstractNode
from Src.Config.Annotations import AFile, AEnum, ASequence




# Словарь-диспетчер: Класс аннотации -> Функция десериализации
DESERIALIZE_REGISTRY = {
    AFile: lambda hint, val: [Path(p) for p in val],
    AEnum: lambda hint, val: next((m for m in hint.source if m.value == val), None),
    ASequence: lambda hint, val: tuple(val)
}


def deserialize_parameter_value(hint: Any, value: Any) -> Any:
    """
    Преобразует JSON-совместимое значение обратно в исходный тип Python
    на основе словаря-диспетчера.
    """
    if value is None:
        return None
    
    hint_cls = hint if isinstance(hint, type) else type(hint)

    handler = DESERIALIZE_REGISTRY.get(hint_cls)
    if handler:
        return handler(hint, value)
    
    return value



def deserialize_node(node: AbstractNode, data: dict) -> bool:
    """
    Заполняет параметры воссозданного узла сохраненными значениями.
    """
    if "position" in data:
        dpg.set_item_pos(node.node_tag, data["position"])

    param_value = data.get("parameters", {})
    arguments = dpg.get_item_children(node.node_tag, slot=1)

    success = True

    for argument in arguments:
        name = dpg.get_item_label(argument)

        if name not in node.annotations or name not in param_value:
            continue
        
        parameter = node.annotations[name]
        saved_val = param_value[name]

        python_val = deserialize_parameter_value(parameter.hint, saved_val)

        res = parameter.set_value(argument, python_val)
        if not res:
            success = False

    return success
