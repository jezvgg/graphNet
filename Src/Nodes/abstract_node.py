from dataclasses import dataclass
from abc import ABC
from typing import Callable
import inspect

import dearpygui.dearpygui as dpg

from Src.Logging import Logger_factory, Logger
from Src.Config.parameter import Parameter, AttrType


class AbstractNode(ABC):
    '''
    Нода (узел графа), класс который используется для сохранения связей в графе, а также информации о ноде. 

    Attributes:
        node_tag: str | int - индетификатор ноды (dpg.node)
        incoming: list[Node] - связи с нодами, которые подключенны к этой ноде. (Приходящие)
        outgoing: list[Node] - связи с нодами, к которым подключенна эта нода. (Уходящие)
    '''
    node_tag: str | int
    # Устанавливаем связи не между узлами, а между их аттрибутами
    incoming: dict[str | int, str | int]
    outgoing: dict[str | int, str | int]
    annotations: dict[str, Parameter]
    logic: Callable
    docs: str
    input: bool
    output: bool
    logger: Logger


    def __init__(self, node_tag: int | str, annotations: dict[str: type], \
                 logic: Callable, docs: str = None, input = True, output = True):
        '''
        Нода (узел графа), класс который используется для сохранения связей в графе, а также информации о ноде. 

        Args:
            layer: keras.layers.Layer - слой, логику которого нода хранит.
            annotations: dict[str, type] - аннотации на аргументы, которые нужно вводить, для создания слоя.
            docs: str - документация к слою
            node_tag: str | int = None - индетификатор ноды (dpg.node)
        '''
        self.node_tag = node_tag
        self.annotations = annotations
        self.logic = logic
        self.incoming = {}
        self.outgoing = {}
        self.input = input
        self.output = output
        self.OUTPUT = None

        if not docs: docs = inspect.getdoc(self.logic)
        self.docs = docs

        self.logger = Logger_factory.from_instance()("nodes")


    def __repr__(self) -> str:
        return f"{self.node_tag}"


    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.node_tag} {dict(incoming=self.incoming, outgoing=self.outgoing)}"
    

    def __hash__(self):
        return self.node_tag


    def compile(self, kwargs: dict = None):
        '''
        Основной метод нодов, содержащий логику их работы. Тут создаются слои нейронной сети, проходит обучение и т.д. В зависимости от ноды, будет разная логика.
        '''
        if not kwargs: kwargs = {}
        arguments = dpg.get_item_children(self.node_tag)[1]

        self.logger.info(f"Компиляция ноды - {self.__class__.__name__}")
        self.logger.debug(f"Аргументы ноды - {arguments}")

        for argument in arguments:
            name = dpg.get_item_label(argument)

            if name not in self.annotations or \
            self.annotations[name].attr_type == AttrType.OUTPUT: continue

            kwargs[name] = self.annotations[name].get_value(argument)

            self.logger.debug(kwargs)
            
        self.OUTPUT = self.logic(**kwargs)
        return self.OUTPUT
    


@dataclass
class node_link:
    '''
    Класс для dpg.add_node_link, указывает какие аттрибуты узлов связываются.
    '''
    outgoing: str | int
    incoming: str | int