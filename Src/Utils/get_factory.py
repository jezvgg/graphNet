from functools import singledispatch

import dearpygui.dearpygui as dpg

from Src.Models import File
from Src.Nodes import ParameterNode, DataNode, AbstractNode
from Src.Utils.factory_method import factorymethod



class GetterFactory:


    @singledispatch
    @staticmethod
    def get_value(hint: type |  tuple, argument: int): raise Exception(f"Не получилось получить значения для {hint}")
    

    @get_value.register(tuple)
    def get_values(hint: tuple, argument: int): return tuple(dpg.get_values(dpg.get_item_children(argument)[1])[:len(hint)])
    

    @get_value.register(type)
    @factorymethod
    def get_input_value(hint: type, argument: int): raise Exception(f"Не получилось получить значения для элемента ввода типа {hint}")
    

    @get_input_value.register((int, float, str, bool))
    def get_input_state(hint: type, argument: int): return dpg.get_value(argument)
    

    @get_input_value.register(File)
    def get_files_state(hint: File, argument: int): return dpg.get_item_user_data(argument)
    

    @get_input_value.register(
        ParameterNode.__subclasses__() + \
        DataNode.__subclasses__()
    )
    def get_node_state(hint: ParameterNode, argument: int):
        parent = dpg.get_item_parent(argument)
        user_data = dpg.get_item_user_data(parent)

        node_in: list[tuple[str, AbstractNode]] = [('data' if dpg.get_item_alias(attribute) == 'OUTPUT' 
                                                    else dpg.get_item_alias(attribute),
                                                    dpg.get_item_user_data(dpg.get_item_parent(attribute))) 
                                                    for attribute in user_data]

        if len(node_in) == 1: return getattr(node_in[0][1], node_in[0][0])
        return [getattr(node, field) for field, node in node_in]