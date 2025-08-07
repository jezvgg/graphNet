import unittest

import dearpygui.dearpygui as dpg



class DPGUnitTest(unittest.TestCase):
    '''
    Класс реализующий создание контекста и его разрушение, для тестирование элементов DPG
    '''

    @classmethod
    def setUpClass(cls):
        cls.context = dpg.create_context()
        cls.parent = "Tests"
        cls.window = dpg.add_window(tag=cls.parent)
        return super().setUpClass()
    

    @classmethod
    def tearDownClass(cls):
        dpg.destroy_context()
        return super().tearDownClass()