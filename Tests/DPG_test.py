import unittest

import dearpygui.dearpygui as dpg

from Src.Managers.theme_manager import ThemeManager


class DPGUnitTest(unittest.TestCase):
    '''
    Базовый класс для тестов с DPG-контекстом.
    Контекст создаётся один раз на всю сессию через conftest.py.
    '''

    @classmethod
    def setUpClass(cls):
        cls.parent = "Tests"
        cls.window = dpg.add_window(tag=cls.parent)
        ThemeManager.load_themes("Tests/themes.json")
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        for item in list(dpg.get_all_items()):
            try:
                dpg.delete_item(item)
            except Exception:
                pass
        return super().tearDownClass()
