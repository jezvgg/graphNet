from Src.Config.Annotations.annotation import Annotation

import dearpygui.dearpygui as dpg



class ANode(Annotation):


    @staticmethod
    def build(parent: int | str, *args, **kwargs):
        kwargs = Annotation.check_kwargs(dpg.add_text, kwargs)

        if (dpg.get_item_type(parent) != 'mvAppItemType::mvNodeAttribute'):
            raise Exception(f"Incompatable parent {dpg.get_item_type(parent)} must be mvAppItemType::mvNodeAttribute")

        new_parent = dpg.get_item_parent(parent)
        dpg.delete_item(parent)
        kwargs = Annotation.check_kwargs(dpg.node_attribute, kwargs)
        kwargs['parent']  = new_parent
        kwargs['user_data'] = []

        with dpg.node_attribute(*args, **kwargs, attribute_type=dpg.mvNode_Attr_Input) as attr:
            dpg.add_text(kwargs.get('label'), label=kwargs.get('label'))
        return attr
    

    @staticmethod
    def get(input_field: int | str):
        from Src.Nodes import AbstractNode

        if (dpg.get_item_type(input_field) != 'mvAppItemType::mvNodeAttribute'):
            raise Exception(f"Incompatable item {dpg.get_item_type(input_field)} must be mvAppItemType::mvNodeAttribute")

        user_data = dpg.get_item_user_data(input_field)

        node_in: list[tuple[str, AbstractNode]] = [(dpg.get_item_label(attribute),
                                                    dpg.get_item_user_data(dpg.get_item_parent(attribute))) 
                                                    for attribute in user_data]

        if len(node_in) == 1: return getattr(node_in[0][1], node_in[0][0])
        return [getattr(node, field) for field, node in node_in]
    

    @staticmethod
    def set(input_id: str| int): pass