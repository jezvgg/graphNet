from Src.Config.Annotations.annotation import Annotation

import dearpygui.dearpygui as dpg

from Src.Logging.logger_factory import Logger_factory




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
            input_id = dpg.add_text(kwargs.get('label'), label=kwargs.get('label'))

        return input_id
    

    @staticmethod
    def get(input_id: int | str):
        from Src.Nodes import AbstractNode

        parent = dpg.get_item_parent(input_id)

        if dpg.get_item_type(parent) != 'mvAppItemType::mvNodeAttribute':
            raise Exception(f"Incompatable parent of item {dpg.get_item_type(parent)} must be mvAppItemType::mvNodeAttribute")

        user_data = dpg.get_item_user_data(parent)

        node_in: list[tuple[str, AbstractNode]] = [(dpg.get_item_label(attribute),
                                                    dpg.get_item_user_data(dpg.get_item_parent(attribute)))
                                                    for attribute in user_data]

        results = []
        for field, node in node_in:
            if not hasattr(node, field):
                raise Exception(f"Атрибут '{field}' не найден в объекте узла типа '{node.__class__.__name__}'.")

            results.append(getattr(node, field))

        if len(results) == 1: return results[0]
        return results
    

    @staticmethod
    def set(input_id: str| int, value) -> bool:
        return False 
