import json

import dearpygui.dearpygui as dpg

from Src.node_editor import NodeEditor
from Src.Config import NodeAnnotation, Parameter
from Src.Config.Annotations import AInteger
from Src.Nodes import AbstractNode
from Src.Enums.attr_type import AttrType
from Src.Logging.logger_factory import Logger_factory
from Tests.DPG_test import DPGUnitTest




class test_NodeEditor(DPGUnitTest):
    '''
    Проверка объектов аннотации и их работоспособности
    '''
    node_editor: NodeEditor


    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        dpg.create_viewport(title='Custom Title')
        with open("Tests/logger_config.json") as f:
            config = json.load(f)

        log_factory = Logger_factory(config)
        cls.node_editor = NodeEditor()


    def test_initialize(self):
        assert isinstance(self.node_editor, NodeEditor)


    def test_drop_callback(self):
        node = NodeAnnotation(
                    label="Example",
                    node_type=AbstractNode,
                    logic = lambda x:x,
                    annotations={}
                    )

        with dpg.window():
            btn = dpg.add_button(label=node.label, user_data=node)

        nodes_count = len(dpg.get_item_children("node_editor", slot=1))

        self.node_editor.drop_callback("node_editor", btn)
        assert dpg.get_item_pos(self.node_editor._NodeEditor__start_nodes[-1].node_tag) == [8,8]
        assert len(dpg.get_item_children("node_editor", slot=1)) == nodes_count + 1
        assert dpg.get_item_label(dpg.get_item_children("node_editor", slot=1)[-1]) == "Example"


    def test_link_callback(self):
        anode1 = NodeAnnotation(
                    label="Example",
                    node_type=AbstractNode,
                    logic = lambda x:x,
                    annotations={
                        "x": Parameter(AttrType.OUTPUT, AInteger)
                        }
                    )
        anode2 = NodeAnnotation(
                    label="Example",
                    node_type=AbstractNode,
                    logic = lambda x:x,
                    annotations={
                        "x": Parameter(AttrType.INPUT, AInteger)
                        }
                    )
        
        node_id1 = self.node_editor.builder.build_node(anode1, "node_editor")
        node_id2 = self.node_editor.builder.build_node(anode2, "node_editor")
        node1: AbstractNode = dpg.get_item_user_data(node_id1)
        node2: AbstractNode = dpg.get_item_user_data(node_id2)
        self.node_editor._NodeEditor__start_nodes += [node1, node2]
        node_attr1 = None
        node_attr2 = None

        for attribute in dpg.get_item_children(node_id1, slot=1):
            for field in dpg.get_item_children(attribute, slot=1):
                if dpg.get_item_label(field) == "x":
                    node_attr1 = attribute
                    break

        for attribute in dpg.get_item_children(node_id2, slot=1):
            for field in dpg.get_item_children(attribute, slot=1):
                if dpg.get_item_label(field) == "x":
                    node_attr2 = attribute
                    break

        self.node_editor.link_callback("node_editor", (node_attr1, node_attr2))


        assert isinstance(node1.outgoing[node_attr1], list)
        assert len(node1.outgoing[node_attr1]) == 1
        assert node_attr2 in node1.outgoing[node_attr1]
        assert node_attr1 == node2.incoming[node_attr2]


    def test_delink_callback(self):
        anode1 = NodeAnnotation(
                    label="Example",
                    node_type=AbstractNode,
                    logic = lambda x:x,
                    annotations={
                        "x": Parameter(AttrType.OUTPUT, AInteger)
                        }
                    )
        anode2 = NodeAnnotation(
                    label="Example",
                    node_type=AbstractNode,
                    logic = lambda x:x,
                    annotations={
                        "x": Parameter(AttrType.INPUT, AInteger)
                        }
                    )
        
        node_id1 = self.node_editor.builder.build_node(anode1, "node_editor")
        node_id2 = self.node_editor.builder.build_node(anode2, "node_editor")
        node1: AbstractNode = dpg.get_item_user_data(node_id1)
        node2: AbstractNode = dpg.get_item_user_data(node_id2)
        self.node_editor._NodeEditor__start_nodes += [node1, node2]
        node_attr1 = None
        node_attr2 = None

        for attribute in dpg.get_item_children(node_id1, slot=1):
            for field in dpg.get_item_children(attribute, slot=1):
                if dpg.get_item_label(field) == "x":
                    node_attr1 = attribute
                    break

        for attribute in dpg.get_item_children(node_id2, slot=1):
            for field in dpg.get_item_children(attribute, slot=1):
                if dpg.get_item_label(field) == "x":
                    node_attr2 = attribute
                    break

        self.node_editor.link_callback("node_editor", (node_attr1, node_attr2))

        assert dpg.get_item_user_data(node_attr1) == [node_attr2]
        assert dpg.get_item_user_data(node_attr2) == [node_attr1]

        link_id = dpg.get_item_children("node_editor", slot=0)[-1]

        self.node_editor.delink_callback("node_editor", link_id)

        assert node_attr1 not in node1.outgoing
        assert node_attr2 not in node2.incoming

        assert dpg.get_item_user_data(node_attr1) == []
        assert dpg.get_item_user_data(node_attr2) == []


    def test_delete_node(self):
        anode1 = NodeAnnotation(
                    label="Example",
                    node_type=AbstractNode,
                    logic = lambda x:x,
                    annotations={
                        "x": Parameter(AttrType.OUTPUT, AInteger)
                        }
                    )
        anode2 = NodeAnnotation(
                    label="Example",
                    node_type=AbstractNode,
                    logic = lambda x:x,
                    annotations={
                        "x": Parameter(AttrType.INPUT, AInteger)
                        }
                    )
        
        node_id1 = self.node_editor.builder.build_node(anode1, "node_editor")
        node_id2 = self.node_editor.builder.build_node(anode2, "node_editor")
        node1: AbstractNode = dpg.get_item_user_data(node_id1)
        node2: AbstractNode = dpg.get_item_user_data(node_id2)
        self.node_editor._NodeEditor__start_nodes += [node1, node2]
        node_attr1 = None
        node_attr2 = None

        for attribute in dpg.get_item_children(node_id1, slot=1):
            for field in dpg.get_item_children(attribute, slot=1):
                if dpg.get_item_label(field) == "x":
                    node_attr1 = attribute
                    break

        for attribute in dpg.get_item_children(node_id2, slot=1):
            for field in dpg.get_item_children(attribute, slot=1):
                if dpg.get_item_label(field) == "x":
                    node_attr2 = attribute
                    break

        self.node_editor.link_callback("node_editor", (node_attr1, node_attr2))

        links_count = len(dpg.get_item_children("node_editor", slot=0))
        nodes_count = len(dpg.get_item_children("node_editor", slot=1))

        self.node_editor.delete_node(node_id1)

        assert len(dpg.get_item_children("node_editor", slot=0)) == links_count - 1
        assert len(dpg.get_item_children("node_editor", slot=1)) == nodes_count - 1
        assert node_attr2 not in node2.incoming
        assert node2 in self.node_editor._NodeEditor__start_nodes

