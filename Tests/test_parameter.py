import dearpygui.dearpygui as dpg

from Src.Config.Annotations import AInteger, AFloat, ABoolean, AString
from Src.Config.parameter import Parameter
from Src.Enums.attr_type import AttrType
from Tests.DPG_test_with_reset import DPGUnitTestWithReset


class test_parameter(DPGUnitTestWithReset):

    def _make_attr(self, param: Parameter) -> int | str:
        # Минимальный контекст node_editor → node для построения одного параметра
        with dpg.node_editor(parent=self.parent):
            with dpg.node() as node_id:
                return param.build(parent=node_id)

    def test_Parameter(self):
        # Базовая проверка: параметр строится, попадает в реестр DPG, default применяется
        param = Parameter(AttrType.INPUT, AInteger, default=5)

        with dpg.node_editor(parent=self.parent):
            with dpg.node() as node_id:
                attr_id = param.build(parent=node_id)

        assert isinstance(attr_id, int | str)
        assert attr_id in dpg.get_all_items()

        assert param.get_value(attr_id) == 5

        result = param.set_value(attr_id, 1)
        assert result == True
        assert param.get_value(attr_id) == 1

    def test_Parameter_float(self):
        # AFloat: дефолт применяется, get/set работают с float-значением
        # Используем 1.5 — точно представимо в float32, избегаем ошибки округления
        param = Parameter(AttrType.INPUT, AFloat, default=1.5)
        attr_id = self._make_attr(param)

        assert attr_id in dpg.get_all_items()
        self.assertAlmostEqual(param.get_value(attr_id), 1.5, places=4)

        result = param.set_value(attr_id, 2.0)
        assert result == True
        self.assertAlmostEqual(param.get_value(attr_id), 2.0, places=4)

    def test_Parameter_bool(self):
        # ABoolean: дефолт True считывается, set_value переключает на False
        param = Parameter(AttrType.INPUT, ABoolean, default=True)
        attr_id = self._make_attr(param)

        assert param.get_value(attr_id) == True

        result = param.set_value(attr_id, False)
        assert result == True
        assert param.get_value(attr_id) == False

    def test_Parameter_string(self):
        # AString: дефолтная строка считывается, set_value обновляет текст
        param = Parameter(AttrType.INPUT, AString, default="hello")
        attr_id = self._make_attr(param)

        assert param.get_value(attr_id) == "hello"

        result = param.set_value(attr_id, "world")
        assert result == True
        assert param.get_value(attr_id) == "world"

    def test_Parameter_output_type(self):
        # AttrType.OUTPUT: параметр строится без ошибок, значение читается корректно
        param = Parameter(AttrType.OUTPUT, AInteger, default=42)
        attr_id = self._make_attr(param)

        assert attr_id in dpg.get_all_items()
        assert param.get_value(attr_id) == 42

    def test_Parameter_static_type(self):
        # AttrType.STATIC: виджет внутри атрибута должен быть отключён (enabled=False)
        param = Parameter(AttrType.STATIC, AInteger, default=7)
        attr_id = self._make_attr(param)

        assert attr_id in dpg.get_all_items()
        field_id = dpg.get_item_children(attr_id, slot=1)[0]
        assert not dpg.is_item_enabled(field_id)

    def test_Parameter_set_wrong_type_returns_false(self):
        # set_value с несовместимым типом возвращает False и не меняет значение
        param = Parameter(AttrType.INPUT, AInteger, default=10)
        attr_id = self._make_attr(param)

        result = param.set_value(attr_id, "not_an_int")
        assert result == False
        assert param.get_value(attr_id) == 10

    def test_Parameter_no_default(self):
        # Без default get_value возвращает нулевое значение DPG-виджета (0 для AInteger)
        param = Parameter(AttrType.INPUT, AInteger)
        attr_id = self._make_attr(param)

        assert attr_id in dpg.get_all_items()
        assert param.get_value(attr_id) == 0

    def test_Parameter_incompatible_parent_raises(self):
        # build должен поднять Exception, если родитель — не mvNode
        param = Parameter(AttrType.INPUT, AInteger)

        with dpg.window() as window_id:
            with self.assertRaises(Exception):
                param.build(parent=window_id)
