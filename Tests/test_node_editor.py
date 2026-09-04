import dearpygui.dearpygui as dpg

from Src.node_editor import NodeEditor
from Src.Config import NodeAnnotation, Parameter
from Src.Config.Annotations import ANode
from Src.Nodes import AbstractNode
from Src.Enums.attr_type import AttrType
from Src.Utils import get_userdata, set_userdata


def test_initialize(node_editor):
    assert isinstance(node_editor, NodeEditor)


def test_drop_callback(node_editor):
    node = NodeAnnotation(
                label="Example",
                node_type=AbstractNode,
                logic = lambda x:x,
                annotations={}
                )

    with dpg.window():
        btn = dpg.add_button(label=node.label)
        set_userdata(btn, value=node)

    nodes_count = len(dpg.get_item_children("node_editor", slot=1))

    node_editor.drop_callback("node_editor", btn)
    assert dpg.get_item_pos(node_editor._NodeEditor__start_nodes[-1].node_tag) == [8,8]
    assert len(dpg.get_item_children("node_editor", slot=1)) == nodes_count + 1
    assert dpg.get_item_label(dpg.get_item_children("node_editor", slot=1)[-1]) == "Example"


def test_link_callback(node_editor):
    anode1 = NodeAnnotation(
                label="Example",
                node_type=AbstractNode,
                logic = lambda x:x,
                annotations={
                    "x": Parameter(AttrType.OUTPUT, ANode[object])
                    }
                )
    anode2 = NodeAnnotation(
                label="Example In 1",
                node_type=AbstractNode,
                logic = lambda x: x,
                annotations={
                    "x": Parameter(AttrType.INPUT, ANode[object])
                }
    )
    anode3 = NodeAnnotation(
                label="Example In 2",
                node_type=AbstractNode,
                logic = lambda x: x,
                annotations={
                    "x": Parameter(AttrType.INPUT, ANode[object])
                }
    )

    node_id1 = node_editor.builder.build_node(anode1, "node_editor")
    node_id2 = node_editor.builder.build_node(anode2, "node_editor")
    node_id3 = node_editor.builder.build_node(anode3, "node_editor")

    node1: AbstractNode = get_userdata(node_id1)
    node2: AbstractNode = get_userdata(node_id2)
    node3: AbstractNode = get_userdata(node_id3)
    node_editor._NodeEditor__start_nodes += [node1, node2, node3]

    node_attr1 = None
    node_attr2 = None
    node_attr3 = None

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

    for attribute in dpg.get_item_children(node_id3, slot=1):
        for field in dpg.get_item_children(attribute, slot=1):
            if dpg.get_item_label(field) == "x":
                node_attr3 = attribute
                break

    node_editor.link_callback("node_editor", (node_attr1, node_attr2))
    node_editor.link_callback("node_editor", (node_attr1, node_attr3))

    assert node2 not in node_editor._NodeEditor__start_nodes
    assert node3 not in node_editor._NodeEditor__start_nodes

    assert isinstance(node1.outgoing[node_attr1], list)

    assert len(node1.outgoing[node_attr1]) == 2

    assert node_attr2 in node1.outgoing[node_attr1]
    assert node_attr3 in node1.outgoing[node_attr1]

    assert node_attr1 in node2.incoming[node_attr2]
    assert node_attr1 in node3.incoming[node_attr3]


def test_delink_callback(node_editor):
    anode1 = NodeAnnotation(
                label="Example",
                node_type=AbstractNode,
                logic = lambda x:x,
                annotations={
                    "x": Parameter(AttrType.OUTPUT, ANode[object])
                    }
                )
    anode2 = NodeAnnotation(
                label="Example",
                node_type=AbstractNode,
                logic = lambda x:x,
                annotations={
                    "x": Parameter(AttrType.INPUT, ANode[object])
                    }
                )

    node_id1 = node_editor.builder.build_node(anode1, "node_editor")
    node_id2 = node_editor.builder.build_node(anode2, "node_editor")
    node1: AbstractNode = get_userdata(node_id1)
    node2: AbstractNode = get_userdata(node_id2)
    node_editor._NodeEditor__start_nodes += [node1, node2]
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

    node_editor.link_callback("node_editor", (node_attr1, node_attr2))

    assert get_userdata(node_attr1) == [node_attr2]
    assert get_userdata(node_attr2) == [node_attr1]

    link_id = dpg.get_item_children("node_editor", slot=0)[-1]

    node_editor.delink_callback("node_editor", link_id)

    assert node_attr1 not in node1.outgoing
    assert node_attr2 not in node2.incoming

    assert get_userdata(node_attr1) == []
    assert get_userdata(node_attr2) == []


def test_delete_node(node_editor):
    anode1 = NodeAnnotation(
                label="Example",
                node_type=AbstractNode,
                logic = lambda x:x,
                annotations={
                    "x": Parameter(AttrType.OUTPUT, ANode[object])
                    }
                )
    anode2 = NodeAnnotation(
                label="Example",
                node_type=AbstractNode,
                logic = lambda x:x,
                annotations={
                    "x": Parameter(AttrType.INPUT, ANode[object])
                    }
                )

    node_id1 = node_editor.builder.build_node(anode1, "node_editor")
    node_id2 = node_editor.builder.build_node(anode2, "node_editor")
    node1: AbstractNode = get_userdata(node_id1)
    node2: AbstractNode = get_userdata(node_id2)
    node_editor._NodeEditor__start_nodes += [node1, node2]
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

    node_editor.link_callback("node_editor", (node_attr1, node_attr2))

    links_count = len(dpg.get_item_children("node_editor", slot=0))
    nodes_count = len(dpg.get_item_children("node_editor", slot=1))

    node_editor.delete_node(node_id1)

    assert len(dpg.get_item_children("node_editor", slot=0)) == links_count - 1
    assert len(dpg.get_item_children("node_editor", slot=1)) == nodes_count - 1
    assert node_attr2 not in node2.incoming
    assert node2 in node_editor._NodeEditor__start_nodes


def test_node_editor_tag_in_dpg(node_editor):
    assert dpg.does_item_exist("node_editor")


def test_drop_callback_returns_node_id(node_editor):
    node = NodeAnnotation(
        label="Example",
        node_type=AbstractNode,
        logic=lambda x: x,
        annotations={}
    )

    with dpg.window():
        btn = dpg.add_button(label=node.label)
        set_userdata(btn, value=node)

    node_id = node_editor.drop_callback("node_editor", btn)

    assert node_id in dpg.get_all_items()
