from random import randint

import dearpygui.dearpygui as dpg



class NodeEditor:


    def __init__(self):
        pass


    def __call__(self, *args, **kwargs):

        with dpg.group(horizontal=True, tag="NodeEditor_group"):


            with dpg.group(tag="nodes_group"):
                with dpg.tree_node(label="Convoluion Layers", tag="tree_node_conv"):
                    dpg.add_button(label="Layer1", tag="Layer1", user_data="Some Data")
                    dpg.add_button(label="Layer2", tag="Layer2")

                    with dpg.drag_payload(parent="Layer1", drag_data="Layer1"):
                        dpg.add_text("popup drag")

            with dpg.group(tag="editor_group", drop_callback=self.drop_callback):
                with dpg.node_editor(tag="node_editor", callback=self.link_callback, \
                                    delink_callback=self.delink_callback, *args, **kwargs):

                    with dpg.node(label="Input Layer", pos=(0, 0)):
                        with dpg.node_attribute(label="INPUT_DUMMY"):
                            dpg.add_text("INPUT")


    def drop_callback(self, sender, app_data):
        print(sender, app_data)

        pos = dpg.get_mouse_pos(local=False)
        ref_node = dpg.get_item_children("node_editor", slot=1)[0]
        ref_screen_pos = dpg.get_item_rect_min(ref_node)
        ref_grid_pos = dpg.get_item_pos(ref_node)

        NODE_PADDING = (8, 8)

        pos[0] = pos[0] - (ref_screen_pos[0] - NODE_PADDING[0]) + ref_grid_pos[0]
        pos[1] = pos[1] - (ref_screen_pos[1] - NODE_PADDING[1]) + ref_grid_pos[1]

        print(pos)
        
        with dpg.node(label=app_data, pos=pos, parent="node_editor"):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_text("Hello World!")


    def link_callback(self, sender, app_data):
        print(app_data)
        dpg.add_node_link(app_data[0], app_data[1], parent=sender)
        print(dpg.get_item_label(app_data[0]), "=>", dpg.get_item_label(app_data[1]))
        print(dpg.get_item_label(dpg.get_item_parent(app_data[0])), '->', \
              dpg.get_item_label(dpg.get_item_parent(app_data[1])))
        print(dpg.get_item_label(sender))


    def delink_callback(self, sender, app_data):
        dpg.delete_item(app_data)



node_editor = NodeEditor()

if __name__ == "__main__":
    dpg.create_context()

    with dpg.window(tag="Prime"):
        node_editor(minimap=True, minimap_location=dpg.mvNodeMiniMap_Location_TopRight)

    dpg.create_viewport(title='Custom Title')
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Prime", True)
    dpg.set_global_font_scale(2)
    dpg.start_dearpygui()
    dpg.destroy_context()