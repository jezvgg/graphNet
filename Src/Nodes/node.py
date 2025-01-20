from dataclasses import dataclass
from abc import ABC
from typing import Callable
import inspect

import dearpygui.dearpygui as dpg



class Node(ABC):
    '''
    Нода (узел графа), класс который используется для сохранения связей в графе, а также информации о ноде. 

    Attributes:
        node_tag: str | int - индетификатор ноды (dpg.node)
        incoming: list[Node] - связи с нодами, которые подключенны к этой ноде. (Приходящие)
        outcoming: list[Node] - связи с нодами, к которым подключенна эта нода. (Уходящие)
    '''
    node_tag: str | int
    incoming: list["Node"]
    outcoming: list["Node"]
    annotations: dict[str: type]
    logic: Callable
    docs: str
    input: bool
    output: bool


    @staticmethod
    def print_tree(node: "Node"):
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
        Node.print_tree(node.outcoming[0])


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


    def compile(self):
        attributes = dpg.get_item_children(self.node_tag)
        arguments = dpg.get_item_children(attributes[1][2])[1]

        kwargs = {}

        for argument in arguments:
            name = dpg.get_item_label(argument)
            if name in self.annotations:
                if isinstance(self.annotations[name], tuple):
                    kwargs[name] = tuple(dpg.get_values(dpg.get_item_children(argument)[1])[:len(self.annotations[name])])
                    continue
                        
                kwargs[name] = dpg.get_value(argument)
            
        return self.logic(**kwargs)
    


@dataclass
class node_link:
    '''
    Класс для dpg.add_node_link, указывает какие ноды связываются.
    '''
    outcoming: Node
    incoming: Node