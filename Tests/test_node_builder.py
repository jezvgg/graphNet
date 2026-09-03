import dearpygui.dearpygui as dpg

from Src.node_builder import NodeBuilder
from Src.Config.node_annotation import NodeAnnotation
from Src.Nodes import AbstractNode, InputLayerNode
from Src.Utils import get_userdata

def test_build_list(env, setup_logger):

    builder = NodeBuilder(
        {
            "Example": {
                "Example": [
                    NodeAnnotation(
                        label="Example",
                        node_type=AbstractNode,
                        logic = lambda x:x,
                        annotations={}
                    )
                ]
            }
        },
        lambda x:x
    )

    with dpg.window() as id:
        list_id = builder.build_list(id)

    assert len(dpg.get_item_children(list_id)[1]) == 1


def test_build_node(env, setup_logger):
    builder = NodeBuilder({}, lambda x:x)

    with dpg.window() as id:
        with dpg.node_editor(tag="node_editor") as editor_id:
            node_id = builder.build_node(
                NodeAnnotation(
                            label="Example",
                            node_type=AbstractNode,
                            logic = lambda x:x,
                            annotations={}
                        ),
                        editor_id
                        )

    assert isinstance(get_userdata(node_id), AbstractNode)
    assert dpg.get_item_type(node_id) == "mvAppItemType::mvNode"
    assert getattr(get_userdata(node_id), 'node_tag') == node_id


def test_build_input(env, setup_logger):
    node_list_mock = {
        "Data & Preprocessing": {
            "Input": [
                NodeAnnotation(
                    label="Input",
                    node_type=InputLayerNode,
                    logic=lambda x: x,
                    annotations={}
                )
            ]
        }
    }
    builder = NodeBuilder(node_list_mock, lambda x:x)
    with dpg.window() as id:
        with dpg.node_editor(tag="node_editor") as editor_id:
            node_id = builder.build_input(editor_id)

    node = get_userdata(node_id)

    assert isinstance(node, InputLayerNode)
    assert dpg.get_item_label(node_id) == "Input"


def test_build_node_correct_label(env, setup_logger):
    builder = NodeBuilder({}, lambda x: x)

    with dpg.window() as id:
        with dpg.node_editor(tag="node_editor") as editor_id:
            node_id = builder.build_node(
                NodeAnnotation(
                    label="MyTestLabel",
                    node_type=AbstractNode,
                    logic=lambda x: x,
                    annotations={}
                ),
                editor_id
            )

    assert dpg.get_item_label(node_id) == "MyTestLabel"
