import enum
from pathlib import Path
from functools import singledispatchmethod
import json

from Src.Nodes.abstract_node import AbstractNode




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
        Делегирует сборку самому узлу, соблюдая принцип инкапсуляции.
        """
        return node.to_dict(self.serialize)


    def default(self, obj: any) -> any:
        """
        Переопределенный стандартный метод JSON-энкодера.
        Вызывается только для типов, которые стандартный энкодер не умеет обработать.
        Использует LBYL (Look Before You Leap): явная проверка типа перед вызовом serialize.
        Для нераспознанных типов вызывает super().default(), чтобы получить
        правильное исключение вместо бесконечной рекурсии.
        """
        if isinstance(obj, AbstractNode):
            return self.serialize(obj)
        return super().default(obj)


