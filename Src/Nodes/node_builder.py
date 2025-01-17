import dearpygui.dearpygui as dpg
from keras import layers
from keras import models
from keras import utils

from Src.Logging import Logger_factory, Logger
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
    __inputs_kwargs: dict
    logger: Logger


    def __init__(self, layers_list: dict[str: Node]):
        '''
        Args:
            layers_list: dict[str: Node] - список слоёв с параметрами, которые использовать в конструкторе
        '''
        self.logger = Logger_factory.from_instance()("nodes")
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


    def build_node(self, layer: Layer, parent: str | int, input: bool = False) -> str | int:
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
            with dpg.node_attribute(label="INPUT", attribute_type=dpg.mvNode_Attr_Static if input else dpg.mvNode_Attr_Input):
                dpg.add_text("INPUT")
                
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                with dpg.tree_node(label="Docs"):
                    dpg.add_text(layer.docs)

            with dpg.node_attribute(label="Arguments", attribute_type=dpg.mvNode_Attr_Static) as attr:
                with dpg.group():
                    for label, hint in layer.annotations.items():
                        kwargs = dict(label=label, parent=attr, width=256)
                        if input: kwargs |= self.__inputs_kwargs
                        self.factory.build(hint, **kwargs)

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

        for argument in arguments:
            name = dpg.get_item_label(argument)
            if name in node.layer.annotations:
                if isinstance(node.layer.annotations[name], tuple):
                    kwargs[name] = tuple(dpg.get_values(dpg.get_item_children(argument)[1])[:len(node.layer.annotations[name])])
                    continue
                        
                kwargs[name] = dpg.get_value(argument)
            
        return node.layer.nnlayer(**kwargs)
    

    def build_input(self, parent: str | int, shape: tuple[int]) -> Node:
        '''
        Особенный метод, реализующий построение слоя входа.

        Args:
            parent: str | int - родительский элемент в котором построить нод. Чаще всего node_editor.
            shape: tuple[int] - форма данных, передаётся в входной слой.

        Returns:
            str | int - индетификатор новой ноды
        '''
        layer = Layer(layer=layers.Input, annotations={'shape': (int,)*len(shape)})

        self.__inputs_kwargs = {
            "enabled": False
        }

        node_id = self.build_node(layer, parent=parent, input=True)

        attributes = dpg.get_item_children(node_id)
        argument = dpg.get_item_children(attributes[1][2])[1][1]
        
        for value, input in zip(shape, dpg.get_item_children(argument)[1]):
            dpg.set_value(input, value)

        return node_id
    

    def build_model(self, node: Node):
        visited = set()
        queue = [node]
        layer = 0
        last_layer = None
        self.logger.info("Началась сборка модели.")

        while queue:
            current_node = queue.pop()
            self.logger.debug(f"Текущая очередь - {queue}")
            self.logger.debug(f"Текущая нода - {current_node}")

            if set(current_node.incoming) | visited == visited:
                self.logger.debug("Нода подошла.")

                nnlayer = self.build_layer(current_node)
                match len(current_node.incoming):
                    case 0: nnlayer = nnlayer
                    case 1: 
                        nnlayer = nnlayer(dpg.get_item_user_data(current_node.incoming[0].node_tag))
                    case _:
                        layers = [dpg.get_item_user_data(node.node_tag) for node in current_node.incoming]
                        nnlayer = nnlayer(layers)

                last_layer = nnlayer
                dpg.set_item_user_data(current_node.node_tag, nnlayer)

                for neightbor in current_node.outcoming:
                    if neightbor not in queue:
                        queue = [neightbor] + queue

                visited.add(current_node)

                layer+=1

        model = models.Model(inputs=[dpg.get_item_user_data(node.node_tag)], outputs=[last_layer])

        # * Для супер жёсткого дебага
        # utils.plot_model(model)
        # print(model.summary())

        


