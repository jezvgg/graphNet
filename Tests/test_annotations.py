import dearpygui.dearpygui as dpg

from Src.Config.Annotations import *
from Tests.DPG_test import DPGUnitTest


class test_annotations(DPGUnitTest):
    '''
    Проверка объектов аннотации и их работоспособности
    '''
    def test_Annotation_check_kwargs(self):
        def func(x: int, y: int, z: int): pass

        kwargs = Annotation.check_kwargs(func, {'x':5, 'y':2, 'z':3, 'k':5})

        assert 'x' in kwargs
        assert 'y' in kwargs
        assert 'z' in kwargs
        assert 'k' not in kwargs
        assert len(kwargs.keys()) == 3


    def test_ABoolean(self):
        checkbox_id = ABoolean.build(parent = self.parent)

        assert isinstance(checkbox_id, int | str) 
        assert checkbox_id in dpg.get_all_items()

        assert ABoolean.get(checkbox_id) == False


    

    