from Src.Config.Annotations.annotation import Annotation

import dearpygui.dearpygui as dpg

from Src.Logging.logger_factory import Logger_factory




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

        logger = Logger_factory.from_instance()("ANode")

        parent = dpg.get_item_parent(input_field)
        user_data = dpg.get_item_user_data(parent)

        node_in: list[tuple[str, AbstractNode]] = [(dpg.get_item_label(attribute),
                                                    dpg.get_item_user_data(dpg.get_item_parent(attribute)))
                                                    for attribute in user_data]

        if len(node_in) == 1:

            field, node = node_in[0]

            if hasattr(node, field):
                return getattr(node, field)

            logger.error(f"Атрибут '{field}' не найден в объекте узла типа '{node.__class__.__name__}'.")
            return None

        results = []
        for field, node in node_in:

            if hasattr(node, field):
                results.append(getattr(node, field))
            else:
                logger.error(f"Атрибут '{field}' не найден в объекте узла типа '{node.__class__.__name__}'.")
                
        return results
    

    @staticmethod
    def set(): pass
