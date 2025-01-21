import dearpygui.dearpygui as dpg
import keras

from Src.Nodes import ParameterNode, LayerNode, InputLayerNode



class CompileNode(ParameterNode):
    logic: keras.models.Model.compile
    incoming: list[LayerNode]
    # TODO Сделать геттер на модель
    data: keras.models.Model


    def compile(self):
        queue = self.incoming[:]
        input_nodes: list[InputLayerNode] = []

        # * Одностороний обход в ширину, чтоб найти входные слои
        while queue:
            current_node = queue.pop()

            if isinstance(current_node, InputLayerNode):
                input_nodes.append(current_node)
            
            for neightbor in current_node.incoming:
                    if neightbor not in queue:
                        queue = [neightbor] + queue


        inputs = [node.layer for node in input_nodes]
        outputs = [node.layer for node in self.incoming]

        self.data = keras.models.Model(inputs=inputs, outputs=outputs)

        attributes = dpg.get_item_children(self.node_tag)
        arguments = dpg.get_item_children(attributes[1][2])[1]

        kwargs = {}

        kwargs['self'] = self.data

        # ? Вынести вот эту функцию куда-нибудь?
        for argument in arguments:
            name = dpg.get_item_label(argument)
            if name in self.annotations:
                if isinstance(self.annotations[name], tuple):
                    kwargs[name] = tuple(dpg.get_values(dpg.get_item_children(argument)[1])[:len(self.annotations[name])])
                    continue
                elif isinstance(self.annotations[name], self.__class__):
                    kwargs[name] = getattr(argument, 'data')
                    continue
                        
                kwargs[name] = dpg.get_value(argument)
            
        self.logic(**kwargs)

        return self.data



        

