import enum
from pathlib import Path
import pytest
import dearpygui.dearpygui as dpg

from Src.Config.Annotations import *

class DummyEnum(enum.Enum):
    FIRST = 'first'
    SECOND = 'second'

def test_Annotation_check_kwargs():
    def func(x: int, y: int, z: int): pass
    kwargs = Annotation.check_kwargs(func, {'x':5, 'y':2, 'z':3, 'k':5})
    assert 'x' in kwargs
    assert 'y' in kwargs
    assert 'z' in kwargs
    assert 'k' not in kwargs
    assert len(kwargs.keys()) == 3

def test_ABoolean(env):
    checkbox_id = ABoolean.build(parent=env)
    assert isinstance(checkbox_id, int | str) 
    assert checkbox_id in dpg.get_all_items()
    assert ABoolean.get(checkbox_id) is False
    assert ABoolean.set(checkbox_id, True) is True
    assert ABoolean.get(checkbox_id) is True
    assert ABoolean.set(checkbox_id, 1) is False

def test_AFloat(env):
    input_id = AFloat.build(parent=env)
    assert isinstance(input_id, int | str) 
    assert input_id in dpg.get_all_items()
    assert AFloat.get(input_id) == 0.0
    assert AFloat.set(input_id, 1.5) is True
    assert AFloat.get(input_id) == 1.5
    assert AFloat.set(input_id, "Example") is False

def test_AInteger(env):
    input_id = AInteger.build(parent=env)
    assert isinstance(input_id, int | str) 
    assert input_id in dpg.get_all_items()
    assert AInteger.get(input_id) == 0
    assert AInteger.set(input_id, 1) is True
    assert AInteger.get(input_id) == 1
    assert AInteger.set(input_id, 1.5) is False

def test_AString(env):
    input_id = AString.build(parent=env)
    assert isinstance(input_id, int | str) 
    assert input_id in dpg.get_all_items()
    assert AString.get(input_id) == ''
    example = "Example"
    assert AString.set(input_id, example) is True
    assert AString.get(input_id) == example
    assert AString.set(input_id, 1.5) is False

def test_AFile(env):
    input_id = AFile.build(parent=env)
    assert isinstance(input_id, int | str) 
    assert input_id in dpg.get_all_items()
    assert AFile.get(input_id) is None
    assert AFile.set(input_id, [Path.cwd()]) is True 
    assert AFile.get(input_id) == [Path.cwd()]
    assert AFile.set(input_id, 'Example path') is False
    assert AFile.set(input_id, [Path.cwd(), 'Example path']) is False

def test_ANode(env):
    with dpg.node_editor(parent=env):
        with dpg.node():
            with dpg.node_attribute() as attribute:
                input_id = ANode[object].build(parent=attribute)
    assert isinstance(input_id, int | str) 
    assert input_id in dpg.get_all_items()
    assert ANode[object].get(input_id) == []
    assert ANode[object].set(input_id, None) is False

def test_ASequence(env):
    input_id = ASequence[AInteger, AInteger].build(parent=env)
    assert isinstance(input_id, int | str) 
    assert input_id in dpg.get_all_items()
    assert ASequence[AInteger, AInteger].get(input_id) == [0, 0]
    assert ASequence[AInteger, AInteger].set(input_id, (1, 1)) is True
    assert ASequence[AInteger, AInteger].get(input_id) == [1, 1]
    assert ASequence[AInteger, AInteger].set(input_id, 1) is False
    assert ASequence[AInteger, AInteger].set(input_id, (1, 1, 1)) is False

def test_AEnum(env):
    annotation = AEnum[DummyEnum]
    combo_id = annotation.build(parent=env)
    assert isinstance(combo_id, int | str)
    assert combo_id in dpg.get_all_items()
    assert DummyEnum(annotation.get(combo_id)) == DummyEnum.FIRST
    assert annotation.set(combo_id, DummyEnum.SECOND) is True
    assert DummyEnum(annotation.get(combo_id)) == DummyEnum.SECOND
    assert annotation.set(combo_id, "Invalid value") is False
    assert annotation.set(combo_id, 123) is False
    assert DummyEnum(annotation.get(combo_id)) == DummyEnum.SECOND

def test_check_kwargs_empty_input():
    def func(x: int, y: int): pass
    assert Annotation.check_kwargs(func, {}) == {}

def test_check_kwargs_no_matching_keys():
    def func(x: int): pass
    assert Annotation.check_kwargs(func, {'a': 1, 'b': 2}) == {}

def test_AString_empty_string_is_valid(env):
    input_id = AString.build(parent=env)
    assert AString.set(input_id, "") is True
    assert AString.get(input_id) == ""

def test_AInteger_negative_value(env):
    input_id = AInteger.build(parent=env)
    assert AInteger.set(input_id, -10) is True
    assert AInteger.get(input_id) == -10
