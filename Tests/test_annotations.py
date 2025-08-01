import json

import dearpygui.dearpygui as dpg

from Src.Config.Annotations import *
from Src.Logging.logger_factory import Logger_factory
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

        # False - значение чекбокса
        assert ABoolean.get(checkbox_id) == False

        assert ABoolean.set(checkbox_id) == None


    def test_AFloat(self):
        input_id = AFloat.build(parent = self.parent)

        assert isinstance(input_id, int | str) 
        assert input_id in dpg.get_all_items()

        assert AFloat.get(input_id) == 0.0

        assert AFloat.set(input_id) == None


    def test_AInteger(self):
        input_id = AInteger.build(parent = self.parent)

        assert isinstance(input_id, int | str) 
        assert input_id in dpg.get_all_items()

        assert AInteger.get(input_id) == 0

        assert AInteger.set(input_id) == None


    def test_AString(self):
        input_id = AString.build(parent = self.parent)

        assert isinstance(input_id, int | str) 
        assert input_id in dpg.get_all_items()

        assert AString.get(input_id) == ''

        assert AString.set(input_id) == None


    def test_AFile(self):
        input_id = AFile.build(parent = self.parent)

        assert isinstance(input_id, int | str) 
        assert input_id in dpg.get_all_items()

        assert AFile.get(input_id) == None

        assert AFile.set(input_id) == None


    def test_ANode(self):
        with dpg.node_editor(parent = self.parent):
            with dpg.node():
                with dpg.node_attribute() as attribute:
                    input_id = ANode.build(parent = attribute)

        assert isinstance(input_id, int | str) 
        assert input_id in dpg.get_all_items()

        assert ANode.get(input_id) == []

        assert ANode.set(input_id) == None


    def test_ASequence(self):
        input_id = ASequence[AInteger, AInteger].build(parent = self.parent)

        assert isinstance(input_id, int | str) 
        assert input_id in dpg.get_all_items()

        assert ASequence[AInteger, AInteger].get(input_id) == [0, 0]

        assert ASequence[AInteger, AInteger].set(input_id) == None

    

    