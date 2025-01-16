from dataclasses import dataclass
import inspect

import dearpygui.dearpygui as dpg
from keras import layers

# from Src.Logging import Logger_factory, Logger


# TODO ===================
# TODO Сделать чтоб ноде, была необязательна ссылка на ноду
# TODO ===================


class Node:
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
    layer: layers.Layer
    annotations: dict[str, type]
    docs: str
    # logger: Logger


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


    def __init__(self, layer: layers.Layer, annotations: dict[str, type], \
                 docs: str = None, node_tag: int | str = None):
        '''
        Нода (узел графа), класс который используется для сохранения связей в графе, а также информации о ноде. 

        Args:
            node_tag: str | int - индетификатор ноды (dpg.node)
        '''
        self.node_tag = node_tag
        self.incoming = []
        self.outcoming = []

        self.layer = layer
        self.annotations = annotations
        if not docs: docs = inspect.getdoc(layer)
        self.docs = docs

        # self.logger = Logger_factory.from_instance()("nodes")


    def __repr__(self) -> str:
        return f"{self.node_tag}"


    def __str__(self) -> str:
        return f"{self.node_tag} {dict(incoming=self.incoming, outcoming=self.outcoming)}"
    

    def add_link(self, in_node: "Node") -> bool:
        '''
        Добавить связь с другой нодой. Текущая нода будет исходящая.

        Args:
            in_node: Node - нода в которую будет приходить связь.

        Returns:
            bool: если True, то связь поставлена.
        '''
        # if not self.node_tag:
        #     self.logger.error("Нельзя связать ноды, без ссылки на настощую ноду.")
        #     return
        
        in_node: "Node" = dpg.get_item_user_data(in_node.node_tag)

        self.outcoming.append(in_node)
        in_node.incoming.append(self)

        return True
    

    def remove_link(self, in_node: "Node") -> bool:
        '''
        Убрать связь с другой нодой. Текущая нода считается исходящей.

        Args:
            in_node: Node - нода связь с который, нужно убрать.

        Returns:
            bool: если True, то связь убрана.
        '''
        # if not self.node_tag:
        #     self.logger.error("Нельзя развязать ноды, без ссылки на настощую ноду.")
        #     return
        
        in_node: "Node" = dpg.get_item_user_data(in_node.node_tag)

        self.outcoming.remove(in_node)
        in_node.incoming.remove(self)

        return True
    

    def delete(self):
        '''
        Удалить текущую ноду. Также убирает все связи с этой нодой.
        '''
        # if not self.node_tag:
        #     self.logger.error("Нельзя удалить ноды, без ссылки на настощую ноду.")
        #     return
        
        for node_in in self.incoming: node_in.remove_link(self)
        for node_out in self.outcoming: self.remove_link(node_out)

        dpg.delete_item(self.node_tag)


    def copy(self) -> "Node":
        return Node(layer=self.layer, annotations=self.annotations, docs=self.docs, node_tag=self.node_tag)
    


@dataclass
class node_link:
    '''
    Класс для dpg.add_node_link, указывает какие ноды связываются.
    '''
    outcoming: Node
    incoming: Node