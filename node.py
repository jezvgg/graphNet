from dataclasses import dataclass

import dearpygui.dearpygui as dpg



class Node:
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
        self.node_tag = node_tag
        self.incoming = []
        self.outcoming = []


    def __repr__(self):
        return f"{self.node_tag}"


    def __str__(self):
        return f"{self.node_tag} {dict(incoming=self.incoming, outcoming=self.outcoming)}"
    

    def add_link(self, in_node: "Node"):

        in_node: "Node" = dpg.get_item_user_data(in_node.node_tag)

        self.outcoming.append(in_node)
        in_node.incoming.append(self)

        return True
    

    def remove_link(self, in_node: "Node"):

        in_node: "Node" = dpg.get_item_user_data(in_node.node_tag)

        self.outcoming.remove(in_node)
        in_node.incoming.remove(self)

        return True
    

    def delete(self):
        for node_in in self.incoming: node_in.remove_link(self)
        for node_out in self.outcoming: self.remove_link(node_out)

        dpg.delete_item(self.node_tag)
    


@dataclass
class node_link:
    outcoming: Node
    incoming: Node