from typing import Any, TypeVar

import dearpygui.dearpygui as dpg

from Src.Utils.children import get_children


T = TypeVar("T")
__cache: dict[int | str, dict[str, Any]] = {}


def get_userdata(id: int | str, key: str = "self") -> Any:
    """
    Функция для взаимодействия с userdata объектов DPG.
    Позволяет удобно доставать значения по ключу.
    Если ключ не передан, возращается объект, который характерзует графический элемент.
    Например если получить объект у узла, то получете AbstractNode, а если у обычного граф. элемента - то словарь userdata.
    !Important Создан как костыль, для поддержки совместимости кастомных полей граф. объектов и объектов характеризующих их.
    """
    obj: dict = __cache.get(id, {})
    return obj.get(key)


def set_userdata(id: int | str, key: str = "self", value: T = None) -> T:
    """
    Функция для взаимодействия с userdata объектов DPG.
    Позволяет удобно вставлять значения по ключу.
    Если ключ не передан, то значение вставляет как объект характеризующий граф. элемент.
    !Important Создан как костыль, для поддержки совместимости кастомных полей граф. объектов и объектов характеризующих их.
    """
    obj: dict = __cache.get(id, {})
    obj[key] = value
    dpg.set_item_user_data(id, obj)
    __cache[id] = obj
    if isinstance(id, str): __cache[dpg.get_alias_id(id)] = obj
    return value


def clear_userdata(id: int | str, children: bool = True):
    '''
    Очищает кэш userdata
    '''
    items = {id}
    if children: items |= get_children(id)

    for item in items:
        __cache.pop(item, None)
        if isinstance(item, str): __cache.pop(dpg.get_alias_id(item), None)
