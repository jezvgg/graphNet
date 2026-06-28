import pytest
import dearpygui.dearpygui as dpg

from Src.Config.Annotations import AInteger, AFloat, ABoolean, AString
from Src.Config.parameter import Parameter
from Src.Enums.attr_type import AttrType

def _make_attr(env, param: Parameter) -> int | str:
    # Минимальный контекст node_editor → node для построения одного параметра
    with dpg.node_editor(parent=env):
        with dpg.node() as node_id:
            return param.build(parent=node_id)

def test_Parameter(env):
    # Базовая проверка: параметр строится, попадает в реестр DPG, default применяется
    param = Parameter(AttrType.INPUT, AInteger, default=5)

    with dpg.node_editor(parent=env):
        with dpg.node() as node_id:
            attr_id = param.build(parent=node_id)

    assert isinstance(attr_id, int | str)
    assert attr_id in dpg.get_all_items()

    assert param.get_value(attr_id) == 5

    result = param.set_value(attr_id, 1)
    assert result is True
    assert param.get_value(attr_id) == 1

def test_Parameter_float(env):
    # AFloat: дефолт применяется, get/set работают с float-значением
    # Используем 1.5 — точно представимо в float32, избегаем ошибки округления
    param = Parameter(AttrType.INPUT, AFloat, default=1.5)
    attr_id = _make_attr(env, param)

    assert attr_id in dpg.get_all_items()
    assert param.get_value(attr_id) == pytest.approx(1.5, abs=1e-4)

    result = param.set_value(attr_id, 2.0)
    assert result is True
    assert param.get_value(attr_id) == pytest.approx(2.0, abs=1e-4)

def test_Parameter_bool(env):
    # ABoolean: дефолт True считывается, set_value переключает на False
    param = Parameter(AttrType.INPUT, ABoolean, default=True)
    attr_id = _make_attr(env, param)

    assert param.get_value(attr_id) is True

    result = param.set_value(attr_id, False)
    assert result is True
    assert param.get_value(attr_id) is False

def test_Parameter_string(env):
    # AString: дефолтная строка считывается, set_value обновляет текст
    param = Parameter(AttrType.INPUT, AString, default="hello")
    attr_id = _make_attr(env, param)

    assert param.get_value(attr_id) == "hello"

    result = param.set_value(attr_id, "world")
    assert result is True
    assert param.get_value(attr_id) == "world"

def test_Parameter_output_type(env):
    # AttrType.OUTPUT: параметр строится без ошибок, значение читается корректно
    param = Parameter(AttrType.OUTPUT, AInteger, default=42)
    attr_id = _make_attr(env, param)

    assert attr_id in dpg.get_all_items()
    assert param.get_value(attr_id) == 42

def test_Parameter_static_type(env):
    # AttrType.STATIC: виджет внутри атрибута должен быть отключён (enabled=False)
    param = Parameter(AttrType.STATIC, AInteger, default=7)
    attr_id = _make_attr(env, param)

    assert attr_id in dpg.get_all_items()
    field_id = dpg.get_item_children(attr_id, slot=1)[0]
    assert not dpg.is_item_enabled(field_id)

def test_Parameter_set_wrong_type_returns_false(env):
    # set_value с несовместимым типом возвращает False и не меняет значение
    param = Parameter(AttrType.INPUT, AInteger, default=10)
    attr_id = _make_attr(env, param)

    result = param.set_value(attr_id, "not_an_int")
    assert result is False
    assert param.get_value(attr_id) == 10

def test_Parameter_no_default(env):
    # Без default get_value возвращает нулевое значение DPG-виджета (0 для AInteger)
    param = Parameter(AttrType.INPUT, AInteger)
    attr_id = _make_attr(env, param)

    assert attr_id in dpg.get_all_items()
    assert param.get_value(attr_id) == 0

def test_Parameter_incompatible_parent_raises(env):
    # build должен поднять Exception, если родитель — не mvNode
    param = Parameter(AttrType.INPUT, AInteger)

    with dpg.window() as window_id:
        with pytest.raises(Exception):
            param.build(parent=window_id)
