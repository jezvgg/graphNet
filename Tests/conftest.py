import pytest
import json
import dearpygui.dearpygui as dpg

from Src.Managers.theme_manager import ThemeManager
from Src.Logging.logger_factory import Logger_factory
from Src.node_editor import NodeEditor


@pytest.fixture(scope="session", autouse=True)
def dpg_session():
    '''
    Фикстура для создания сессии DearPyGui.
    '''
    dpg.create_context()
    dpg.create_viewport(title='Test Session')
    dpg.setup_dearpygui()
    yield


@pytest.fixture(scope="session")
def setup_logger():
    """
    Настройка логгера один раз на сессию.
    """
    with open("Tests/logger_config.json") as f: config = json.load(f)
    Logger_factory(config)


@pytest.fixture()
def env(dpg_session):
    '''
    Настройка и очистка окружения
    '''
    window = dpg.add_window(tag="Tests")
    ThemeManager.load_themes("Tests/themes.json")

    yield window

    for item in list(dpg.get_all_items()):
        if dpg.get_item_parent(item) == 0:
                dpg.delete_item(item)

    for alias in list(dpg.get_aliases()):
        dpg.remove_alias(alias)

    ThemeManager._created_themes = {}
    ThemeManager._item_themes = {}


@pytest.fixture()
def node_editor(env, setup_logger):
    return NodeEditor()
