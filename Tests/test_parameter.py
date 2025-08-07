import dearpygui.dearpygui as dpg

from Src.Config.Annotations import AInteger
from Src.Config.parameter import Parameter
from Src.Enums.attr_type import AttrType
from Tests.DPG_test import DPGUnitTest


class test_annotations(DPGUnitTest):

    def test_Parameter(self):
        param = Parameter(AttrType.INPUT, AInteger, default=5)

        with dpg.node_editor(parent = self.parent):
            with dpg.node() as node_id:
                attr_id = param.build(parent = node_id)

        assert isinstance(attr_id, int | str) 
        assert attr_id in dpg.get_all_items()

        value = param.get_value(attr_id)

        assert value == 5

        result = param.set_value(attr_id, 1)

        assert param.get_value(attr_id) == 1
        assert result == True
            