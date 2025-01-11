import dearpygui.dearpygui as dpg

dpg.create_context()
dpg.create_viewport(title=f"Test - {dpg.get_dearpygui_version()}", width=500, height=400)

dpg.setup_dearpygui()

with dpg.window(pos=(0, 30), width=500, height=350):
    b1 = dpg.add_button(label="Drag me!")
    with dpg.drag_payload(parent=b1):
        dpg.add_text("A new node")

    node_editor = dpg.generate_uuid()

    def on_drop(sender, app_data):
        pos = dpg.get_mouse_pos(local=True)
        print(pos)
        print(sender)
        ref_node = dpg.get_item_children(node_editor, slot=1)[0]
        print(ref_node)
        print(dpg.get_item_label(ref_node))
        ref_grid_pos = dpg.get_item_pos(ref_node)

        NODE_PADDING = (8, 8)

        pos[0] = pos[0] - 8
        pos[1] = pos[1] - 8

        with dpg.node(label="New", pos=pos, parent=node_editor):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_text(f"I'm a new node")
                dpg.add_text(f"at {pos}!")

    with dpg.group(drop_callback=on_drop):
        with dpg.node_editor(tag=node_editor,
                             minimap=True,
                             minimap_location=dpg.mvNodeMiniMap_Location_BottomRight):
            print(node_editor)

            with dpg.node(label="A real node", pos=[50, 30], tag="REALNODE"):
                with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                    pass


dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()