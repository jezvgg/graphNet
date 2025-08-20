from itertools import chain

import dearpygui.dearpygui as dpg
import keras

from Src.Nodes import ParameterNode



class CompileNode(ParameterNode):
    logic: keras.models.Model.compile
    data: keras.models.Model


    def compile(self):
        self.logger.debug("Модель начала компиляцию")

        input_nodes = [getattr(dpg.get_item_user_data(dpg.get_item_parent(node)),'inputs') \
                       for node in chain(*self.incoming.values())]
        input_nodes = set().union(*input_nodes)
        inputs = [getattr(node, 'layer') for node in input_nodes]

        outputs = [getattr(dpg.get_item_user_data(dpg.get_item_parent(attribute)), 'layer') for attribute in 
                   dpg.get_item_user_data(dpg.get_item_children(self.node_tag)[1][0])]

        model = keras.models.Model(inputs=inputs, outputs=outputs)

        status = super().compile({"self": model})
        self.logger.info("Модель скомпилирована")

        self.logger.info(f"model: {model}")

        # TODO: Поубирать лишнии параметры
        self.data = model
        self.OUTPUT = self.data
        return status



        

