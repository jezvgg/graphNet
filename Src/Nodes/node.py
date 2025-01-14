from dataclasses import dataclass

import dearpygui.dearpygui as dpg



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


    def __init__(self, node_tag: str | int):
        '''
        Нода (узел графа), класс который используется для сохранения связей в графе, а также информации о ноде. 

        Args:
            node_tag: str | int - индетификатор ноды (dpg.node)
        '''
        self.node_tag = node_tag
        self.incoming = []
        self.outcoming = []


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
        in_node: "Node" = dpg.get_item_user_data(in_node.node_tag)

        self.outcoming.remove(in_node)
        in_node.incoming.remove(self)

        return True
    

    def delete(self):
        '''
        Удалить текущую ноду. Также убирает все связи с этой нодой.
        '''
        for node_in in self.incoming: node_in.remove_link(self)
        for node_out in self.outcoming: self.remove_link(node_out)

        dpg.delete_item(self.node_tag)
    


@dataclass
class node_link:
    '''
    Класс для dpg.add_node_link, указывает какие ноды связываются.
    '''
    outcoming: Node
    incoming: Node