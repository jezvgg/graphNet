import dearpygui.dearpygui as dpg
from keras import layers

from Src.Nodes import Node, InputsFactory, Layer



class NodeBuilder:
    '''
    Класс реализующий логику связывания Keras и Нодов.

    Attributes:
        factory: InputsFactory - фабрика конвертации аннотаций в инпуты
        layers_list: dict[str: Node] - список слоёв с параметрами, которые использовать в конструкторе
    '''
    factory: InputsFactory
    layers_list: dict[str: Node]


    def __init__(self, layers_list: dict[str: Node]):
        '''
        Args:
            layers_list: dict[str: Node] - список слоёв с параметрами, которые использовать в конструкторе
        '''
        self.factory = InputsFactory()
        self.layers_list = layers_list


    def build_list(self, parent: str | int) -> str | int:
        '''
        Построить список (tree_node) из списка слоёв. Используется для панели слева в конструкторе.

        Args:
            parent: str | int - родительский элемент в котором создать список.

        Returns:
            str | int - индетификатор списка
        '''
        with dpg.group(parent=parent) as list:
            for anchor in self.layers_list.keys():
                with dpg.tree_node(label=anchor) as tree:
                    for nnlayer in self.layers_list[anchor]:
                        with dpg.tree_node(label=nnlayer.nnlayer.__name__, user_data=nnlayer) as layer:
                            dpg.add_text(nnlayer.docs)
                        
                        with dpg.drag_payload(parent=layer, drag_data=layer):
                            dpg.add_text(nnlayer.nnlayer.__name__)

        return list


    def build_node(self, layer: Layer, parent: str | int) -> str | int:
        '''
        Построение dpg.node из класса Node. Используется, для создания новых нодов в редакторе. Ноды берутся из user_data в списке слева.

        Args:
            node: Node - нода из которой создать dpg.node
            parent: str | int - родитель, внутри которого создать ноду. Чаще всего это dpg.node_editor.

        Returns:
            str | int - индетификатор новой dpg.node.
        '''
        node_id = dpg.generate_uuid()
        node = Node(node_id, layer)

        with dpg.node(label=layer.nnlayer.__name__, parent=parent, user_data=node, tag=node_id):
            with dpg.node_attribute(label="INPUT", attribute_type=dpg.mvNode_Attr_Input):
                dpg.add_text("INPUT")
                
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                with dpg.tree_node(label="Docs"):
                    dpg.add_text(layer.docs)

            with dpg.node_attribute(label="Arguments", attribute_type=dpg.mvNode_Attr_Static) as attr:
                with dpg.group():
                    for label, hint in layer.annotations.items():
                        self.factory.build(hint, label=label, parent=attr, width=256)

            with dpg.node_attribute(label="OUTPUT", attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_button(label="Delete", callback=node.delete)
                dpg.add_text("OUTPUT")

        return node_id
    

    def build_layer(self, node: Node) -> layers.Layer:
        '''
        # ! Опасный метод 
        
        Использует dpg.get_item_children. При нарушении иерархии классов внутри ноды, будет ошибка.
        Строит слой Keras.layers из параметров ноды.

        Args:
            node: Node - нода из которой строить слой.

        Returns:
            keras.layers.Layer - слой нейроной сети.
        '''
        attributes = dpg.get_item_children(node.node_tag)
        arguments = dpg.get_item_children(attributes[1][2])[1]

        kwargs = {}
        
        # TODO Будет ошибка если инпут - группа, т.е. в случае tuple. Нужно исправить

        for argument in arguments:
            name = dpg.get_item_label(argument)
            if name in node.layer.annotations:
                kwargs[name] = dpg.get_value(argument)
            
        return node.layer(**kwargs)
    

    def build_input(self, parent: str | int, shape: tuple[int]) -> Node:
        '''
        Особенный метод, реализующий построение слоя входа.

        Args:
            parent: str | int - родительский элемент в котором построить нод. Чаще всего node_editor.
            shape: tuple[int] - форма данных, передаётся в входной слой.

        Returns:
            str | int - индетификатор новой ноды
        '''

        node_id = dpg.generate_uuid()
        layer = Layer(layer=layers.InputLayer, annotations={'shape': str})
        node = Node(node_tag=node_id, layer=layer)

        with dpg.node(label="InputLayer", parent=parent, user_data=node, tag=node_id):
            with dpg.node_attribute(label="INPUT", attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_text("INPUT")
                dpg.add_input_intx(size=len(shape), enabled=False, default_value=list(shape), width=256)

            with dpg.node_attribute(label="OUTPUT", attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_text("OUTPUT")

        return node_id
