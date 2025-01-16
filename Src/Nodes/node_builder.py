import dearpygui.dearpygui as dpg
from keras import layers

from Src.Nodes import Node, InputsFactory


class NodeBuilder:
    factory: InputsFactory
    layers_list: dict[str: Node]


    def __init__(self, layers_list: dict[str: Node]):
        self.factory = InputsFactory()
        self.layers_list = layers_list


    def build_list(self, parent: str | int) -> str | int:
        with dpg.group(parent=parent) as list:
            for anchor in self.layers_list.keys():
                with dpg.tree_node(label=anchor) as tree:
                    for node in self.layers_list[anchor]:
                        with dpg.tree_node(label=node.layer.__name__, user_data=node) as layer:
                            dpg.add_text(node.docs)
                        
                        with dpg.drag_payload(parent=layer, drag_data=layer):
                            dpg.add_text(node.layer.__name__)

        return list


    def build_node(self, node: Node, parent: str | int) -> str | int:

        new_node = node.copy()
        with dpg.node(label=node.layer.__name__, parent=parent, user_data=new_node) as node_id:
            with dpg.node_attribute(label="INPUT", attribute_type=dpg.mvNode_Attr_Input):
                dpg.add_text("INPUT")
                
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                with dpg.tree_node(label="Docs"):
                    dpg.add_text(node.docs)

            with dpg.node_attribute(label="Arguments", attribute_type=dpg.mvNode_Attr_Static) as attr:
                with dpg.group():
                    for label, hint in node.annotations.items():
                        self.factory.build(hint, label=label, parent=attr, width=256)

            with dpg.node_attribute(label="OUTPUT", attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_button(label="Delete", callback=new_node.delete)
                dpg.add_text("OUTPUT")

        new_node.node_tag = node_id
        return node_id
    

    def build_layer(self, node: Node) -> layers.Layer:
        '''
        # ! Опасный метод 
        
        '''
        attributes = dpg.get_item_children(node.node_tag)
        arguments = dpg.get_item_children(attributes[1][2])[1]

        kwargs = {}

        for argument in arguments:
            name = dpg.get_item_label(argument)
            if name in node.annotations:
                kwargs[name] = dpg.get_value(argument)
            
        return node.layer(**kwargs)
    

    def build_input(self, parent: str | int, shape: tuple[int]) -> Node:

        node = Node(layer=layers.InputLayer, annotations={'shape': str})

        with dpg.node(label="InputLayer", parent=parent, user_data=node) as node_id:
            with dpg.node_attribute(label="INPUT", attribute_type=dpg.mvNode_Attr_Input):
                dpg.add_text("INPUT")
                dpg.add_input_intx(size=len(shape), enabled=False, default_value=list(shape), width=256)

            with dpg.node_attribute(label="OUTPUT", attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_text("OUTPUT")

        node.node_tag = node_id
        return node


if __name__ == "__main__":
    dpg.create_context()
    dpg.create_viewport(title='Custom Title')

    builder = NodeBuilder()
    layers_list = {"Full": [
        Node(0, layers.Dense, annotations={
            "units": int,
            "activation": str,
            "use_bias": bool
        })
    ]}

    print(layers_list["Full"][0])

    with dpg.window(tag="Prime"):
        with dpg.node_editor(tag="Editor"):
            builder.build_node(layers_list["Full"][0], "Editor")

        dpg.add_button(callback=lambda: print(builder.build_layer(layers_list["Full"][0])))

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Prime", True)
    dpg.set_global_font_scale(2)
    dpg.start_dearpygui()
    dpg.destroy_context()