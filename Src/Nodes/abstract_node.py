from dataclasses import dataclass
from abc import ABC
from typing import Callable
import inspect

import dearpygui.dearpygui as dpg

from Src.Logging import Logger_factory, Logger
from Src.Config.parameter import Parameter
from Src.Models import File


class AbstractNode(ABC):
    '''
    Нода (узел графа), класс который используется для сохранения связей в графе, а также информации о ноде. 

    Attributes:
        node_tag: str | int - индетификатор ноды (dpg.node)
        incoming: list[Node] - связи с нодами, которые подключенны к этой ноде. (Приходящие)
        outcoming: list[Node] - связи с нодами, к которым подключенна эта нода. (Уходящие)
    '''
    node_tag: str | int
    incoming: list["AbstractNode"]
    outcoming: list["AbstractNode"]
    annotations: dict[str, Parameter]
    logic: Callable
    docs: str
    input: bool
    output: bool
    logger: Logger


    # TODO Переписать это говно
    @staticmethod
    def print_tree(node: "AbstractNode"):
        '''
        Метод для дебага.
        Выводит дерево зависимостей по входящим нодам.

        Args:
            node: Node - нода с которой начинать построение.
        '''
        if len(node.outcoming) == 0: 
            print(node)
            return

        print(node, "->", end=' ')
        AbstractNode.print_tree(node.outcoming[0])


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
        self.incoming = []
        self.outcoming = []
        self.input = input
        self.output = output

        if not docs: docs = inspect.getdoc(self.logic)
        self.docs = docs

        self.logger = Logger_factory.from_instance()("nodes")


    def __repr__(self) -> str:
        return f"{self.node_tag}"


    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.node_tag} {dict(incoming=self.incoming, outcoming=self.outcoming)}"
    

    def __hash__(self):
        return self.node_tag
    

    def delete(self):
        '''
        Удалить текущую ноду. Также убирает все связи с этой нодой.
        '''
        for node_in in self.incoming: 
            node_in.outcoming.remove(self)
            self.incoming.remove(node_in)
        for node_out in self.outcoming: 
            node_out.incoming.remove(self)
            self.outcoming.remove(node_out)

        dpg.delete_item(self.node_tag)


    def compile(self, kwargs: dict = None):
        '''
        Основной метод нодов, содержащий логику их работы. Тут создаются слои нейронной сети, проходит обучение и т.д. В зависимости от ноды, будет разная логика.
        '''
        if not kwargs: kwargs = {}
        attributes = dpg.get_item_children(self.node_tag)
        arguments = [dpg.get_item_children(attribute)[1][0] for attribute in attributes[1]]

        self.logger.info(f"Компиляция ноды - {self.__class__.__name__}")
        self.logger.debug(f"Аргументы ноды - {arguments}")

        for argument in arguments:
            name = dpg.get_item_label(argument)

            if name not in self.annotations: continue

            kwargs[name] = self.annotations[name].get_value(argument)

            self.logger.debug(kwargs)
            
        return self.logic(**kwargs)
    


@dataclass
class node_link:
    '''
    Класс для dpg.add_node_link, указывает какие ноды связываются.
    '''
    outcoming: AbstractNode
    incoming: AbstractNode