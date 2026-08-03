import pytest
from pathlib import Path
import enum
import json
import dearpygui.dearpygui as dpg

from Src.Utils.serialization.serializers import ProjectEncoder
from Src.Utils.serialization.deserializers import deserialize_parameter_value, deserialize_node
from Src.Utils.serialization.project_manager import ProjectManager
from Src.Nodes.abstract_node import AbstractNode
from Src.Config.parameter import Parameter, AttrType
from Src.Config.Annotations import AFile, AEnum, ASequence
from Src.node_builder import NodeBuilder


class DummyEnum(enum.Enum):
    A = "A"
    B = "B"

def test_project_encoder_basic():
    encoder = ProjectEncoder()
    assert encoder.serialize(123) == 123
    assert encoder.serialize("str") == "str"
    assert encoder.serialize([1, 2]) == [1, 2]

def test_project_encoder_serialize_path():
    encoder = ProjectEncoder()
    path = Path("/dummy/path")
    assert encoder.serialize(path) == str(path)

def test_project_encoder_serialize_enum():
    encoder = ProjectEncoder()
    assert encoder.serialize(DummyEnum.A) == "A"

def test_project_encoder_serialize_tuple():
    encoder = ProjectEncoder()
    assert encoder.serialize((1, "2", DummyEnum.B)) == [1, "2", "B"]


def test_deserialize_value_afile():
    val = ["/path1", "/path2"]
    res = deserialize_parameter_value(AFile, val)
    assert isinstance(res, list)
    assert res[0] == Path("/path1")
    assert res[1] == Path("/path2")

def test_deserialize_value_aenum():
    val = "A"
    res = deserialize_parameter_value(AEnum[DummyEnum], val)
    assert res == DummyEnum.A

def test_deserialize_value_asequence():
    val = [1, 2, 3]
    res = deserialize_parameter_value(ASequence, val)
    assert res == (1, 2, 3)

def test_deserialize_parameter_value():
    assert deserialize_parameter_value(ASequence, [1, 2, 3]) == (1, 2, 3)
    assert deserialize_parameter_value(None, None) is None
    assert deserialize_parameter_value(int, 42) == 42 # Fallback
