from typing import Any, TypeVar

import dearpygui.dearpygui as dpg


def get_userdata(id: int | str, key: str = "self") -> Any:
    """
    Функция для взаимодействия с userdata объектов DPG.
    Позволяет удобно доставать значения по ключу.
    Если ключ не передан, возращается объект, который характерзует графический элемент.
    Например если получить объект у узла, то получете AbstractNode, а если у обычного граф. элемента - то словарь userdata.
    !Important Создан как костыль, для поддержки совместимости кастомных полей граф. объектов и объектов характеризующих их.
    """
    obj: dict = dpg.get_item_user_data(id) or {}
    return obj.get(key)


def set_userdata(id: int | str, key: str = "self", value: Any = None) -> None:
    """
    Функция для взаимодействия с userdata объектов DPG.
    Позволяет удобно вставлять значения по ключу.
    Если ключ не передан, то значение вставляет как объект характеризующий граф. элемент.
    !Important Создан как костыль, для поддержки совместимости кастомных полей граф. объектов и объектов характеризующих их.
    """
    obj: dict = dpg.get_item_user_data(id) or {}
    obj[key] = value
    dpg.set_item_user_data(id, obj)
