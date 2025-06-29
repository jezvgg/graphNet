from Src.Config.Annotations.annotation import Annotation

import dearpygui.dearpygui as dpg



class ANode(Annotation):


    @staticmethod
    def build(*args, **kwargs):
        kwargs = Annotation.check_kwargs(dpg.add_text, kwargs)

        parent = dpg.get_item_parent(kwargs['parent'])
        dpg.delete_item(kwargs['parent'])
        kwargs = Annotation.check_kwargs(dpg.node_attribute, kwargs)
        kwargs['tag'] = kwargs['parent']
        kwargs['parent']  = parent
        kwargs['user_data'] = []

        with dpg.node_attribute(*args, **kwargs, attribute_type=dpg.mvNode_Attr_Input) as attr:
            dpg.add_text(kwargs.get('label'), label=kwargs.get('label'))
        return attr
    

    @staticmethod
    def get(input_field: int | str):
        from Src.Nodes import AbstractNode

        parent = dpg.get_item_parent(input_field)
        user_data = dpg.get_item_user_data(parent)

        print(user_data)
        node_in: list[tuple[str, AbstractNode]] = [('data' if dpg.get_item_alias(attribute) == 'OUTPUT' 
                                                    else dpg.get_item_alias(attribute),
                                                    dpg.get_item_user_data(dpg.get_item_parent(attribute))) 
                                                    for attribute in user_data]

        print(node_in)
        if len(node_in) == 1: return getattr(node_in[0][1], node_in[0][0])
        return [getattr(node, field) for field, node in node_in]
    

    @staticmethod
    def set(): pass