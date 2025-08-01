import dearpygui.dearpygui as dpg
from keras import layers

from Src.Enums.attr_type import AttrType
from Src.Logging import Logger_factory, Logger
from Src.Nodes import AbstractNode, InputLayerNode, DataNode
from Src.Config.node_list import NodeAnnotation, Parameter, ANode



class NodeBuilder:
    '''
    Класс реализующий логику связывания Keras и Нодов.

    Attributes:
        factory: InputsFactory - фабрика конвертации аннотаций в инпуты
        layers_list: dict[str: AbstractNode] - список слоёв с параметрами, которые использовать в конструкторе
    '''
    node_list: dict[str, dict[str, list[NodeAnnotation]]]
    logger: Logger


    def __init__(self, node_list: dict[str: AbstractNode]):
        '''
        Args:
            layers_list: dict[str: AbstractNode] - список слоёв с параметрами, которые использовать в конструкторе
        '''
        self.logger = Logger_factory.from_instance()("nodes")
        self.node_list = node_list


    def build_list(self, parent: str | int) -> str | int:
        '''
        Построить список (tree_node) из списка слоёв. Используется для панели слева в конструкторе.

        Args:
            parent: str | int - родительский элемент в котором создать список.

        Returns:
            str | int - индетификатор списка
        '''
        with dpg.group(parent=parent) as list:
            for anchor in self.node_list.keys():
                with dpg.tree_node(label=anchor) as tree_anchor:

                    for subanchor in self.node_list[anchor].keys():
                        with dpg.tree_node(label=subanchor) as tree_subanchor:

                            for node in self.node_list[anchor][subanchor]:
                                btn = dpg.add_button(label=node.label, user_data=node)
                                
                                with dpg.drag_payload(parent=btn, drag_data=btn):
                                    dpg.add_text(node.label)

        return list


    def build_node(self, node_data: NodeAnnotation, parent: str | int) -> str | int:
        '''
        Построение dpg.node из класса AbstractNode. Используется, для создания новых нодов в редакторе. Ноды берутся из user_data в списке слева.

        Args:
            node: AbstractNode - нода из которой создать dpg.node
            parent: str | int - родитель, внутри которого создать ноду. Чаще всего это dpg.node_editor.

        Returns:
            str | int - индетификатор новой dpg.node.
        '''
        node_id = dpg.generate_uuid()
        node: AbstractNode = node_data.node_type(node_id, **node_data.kwargs)

        with dpg.node(label=node_data.label, parent=parent, user_data=node, tag=node_id):
            if node.input:
                with dpg.node_attribute(label="INPUT", attribute_type=dpg.mvNode_Attr_Input):
                    dpg.add_text("INPUT")
                
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                with dpg.tree_node(label="Docs"):
                    dpg.add_text(node.docs)

            for label, attribute in node.annotations.items():
                width = self.calculate_width(attribute.hint)
                self.logger.info(f"Attribute label: {label}")
                attribute.build(label=label, parent=node_id, width=width)

            with dpg.node_attribute(label="Delete", attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_button(label="Delete", callback=node.delete)

            if node.output:
                with dpg.node_attribute(label="OUTPUT", attribute_type=dpg.mvNode_Attr_Output):
                    dpg.add_text("OUTPUT")

        return node_id
    

    def build_input(self, parent: str | int, shape: tuple[int]) -> AbstractNode:
        '''
        Особенный метод, реализующий построение слоя входа.

        Args:
            parent: str | int - родительский элемент в котором построить нод. Чаще всего node_editor.
            shape: tuple[int] - форма данных, передаётся в входной слой.

        Returns:
            str | int - индетификатор новой ноды
        '''
        layer = NodeAnnotation(
            label="Input",
            node_type=InputLayerNode, 
            logic = layers.Input,
            annotations = {
                    "shape": Parameter(AttrType.INPUT, ANode),
                }
            )

        node_id = self.build_node(layer, parent=parent)

        attributes = dpg.get_item_children(node_id)[1]

        arguments = [dpg.get_item_children(argument)[1][0] for argument in attributes]

        input_argument = [arg for arg in arguments if dpg.get_item_label(arg) == "shape"][0]
        
        for value, input in zip(shape, dpg.get_item_children(input_argument)[1]):
            dpg.set_value(input, value)

        return node_id
    

    def compile_graph(self):
        '''
        Компиляция графа, от его концов. Работает через обход в ширину. Вызывает метод compile у нода, если все ноды, пришедшие к нему уже скомпилированы. Начинает с нодов, у которых нет входов.
        '''

        ref_node: AbstractNode = dpg.get_item_user_data(dpg.get_item_children("node_editor", slot=1)[-1])
        queue: list[AbstractNode] = [ref_node]
        visited = set()
        starting_nodes: list[AbstractNode] = []

        # * Двустороний обход в ширину, чтоб найти стартовые ноды
        while queue:
            current_node = queue.pop()

            if current_node in visited: continue

            if len(current_node.incoming) == 0: starting_nodes.append(current_node)
            
            for neightbor in current_node.incoming + current_node.outcoming:
                    if neightbor not in queue:
                        queue = [neightbor] + queue

            visited.add(current_node)

        visited = set()
        queue = starting_nodes[:]
        self.logger.info("Началась сборка графа.")

        while queue:
            current_node = queue.pop()
            self.logger.debug(f"Текущая очередь - {queue}")
            self.logger.debug(f"Текущая нода - {current_node}")

            if set(current_node.incoming) | visited == visited:
                self.logger.debug("Нода подошла.")

                layer = current_node.compile()
                print(layer)

                for neightbor in current_node.outcoming:
                    if neightbor not in queue:
                        queue = [neightbor] + queue

                visited.add(current_node)


    def calculate_width(self, annotation_type) -> int:
        '''
        Вычисляет ширину нода в зависимости от типа аннотации.

        Args:
            annotation_type: тип аннотации для определения количества инпутов

        Returns:
            int: рекомендуемая ширина для каждого инпута
        '''

        base_width = 256
        min_width = 48

        if not isinstance(annotation_type, tuple) or len(annotation_type) <= 1: return base_width

        width = int(base_width * 1 / len(annotation_type))

        return max(width, min_width)

