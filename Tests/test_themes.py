import dearpygui.dearpygui as dpg

from Src.Managers.theme_manager import ThemeManager
from Src.Enums import Themes

def test_load_themes(env):
    """
    Проверяет, что конфигурация тем успешно загружена.
    """
    manager = ThemeManager()
    assert manager.config != {}


def test_apply_theme(env):
    """
    Проверяет применение одной темы к элементу.
    """
    with dpg.window():
        button_id = dpg.add_button(label="Test Button")

    manager = ThemeManager()
    manager.apply(button_id, Themes.ERROR)

    theme_key = (Themes.ERROR,)
    assert theme_key in manager._ThemeManager__created_themes

    theme_id = manager._ThemeManager__created_themes[theme_key]
    assert dpg.get_item_theme(button_id) == dpg.get_alias_id(theme_id)


def test_add_theme(env):
    """
    Проверяет добавление темы к уже существующим темам элемента.
    """
    with dpg.window():
        button_id = dpg.add_button(label="Test Button")

    manager = ThemeManager()
    manager.apply(button_id, Themes.DEFAULT)
    manager.add(button_id, Themes.ERROR)

    assert Themes.DEFAULT in manager._ThemeManager__item_themes[button_id]
    assert Themes.ERROR in manager._ThemeManager__item_themes[button_id]
    assert len(manager._ThemeManager__item_themes[button_id]) == 2


def test_remove_theme(env):
    """
    Проверяет удаление темы у элемента.
    """
    with dpg.window():
        button_id = dpg.add_button(label="Test Button")

    manager = ThemeManager()
    manager.apply(button_id, Themes.DEFAULT, Themes.ERROR, Themes.COMPILE)
    manager.remove(button_id, Themes.ERROR)

    item_themes = manager._ThemeManager__item_themes.get(button_id, [])
    assert Themes.DEFAULT in item_themes
    assert Themes.ERROR not in item_themes
    assert Themes.COMPILE in item_themes
    assert len(item_themes) == 2

    manager.remove(button_id, Themes.DEFAULT, Themes.COMPILE)
    assert dpg.get_item_theme(button_id) is None


def test_get_theme(env):
    """
    Проверяет получение (и кэширование) тем.
    """
    manager = ThemeManager()
    theme_id_1 = manager.get(Themes.COMPILE)
    assert (Themes.COMPILE,) in manager._ThemeManager__created_themes

    theme_id_2 = manager.get(Themes.COMPILE)
    assert theme_id_1 == theme_id_2


def test_theme_combination_override(env):
    """
    Проверяет, что стили тем правильно переопределяются при их комбинации.
    """
    with dpg.window():
        with dpg.node_editor():
            node_id = dpg.add_node(label="Test Node")

    manager = ThemeManager()
    manager.apply(node_id, Themes.DEFAULT, Themes.ERROR)

    theme_key = (Themes.DEFAULT, Themes.ERROR)
    assert theme_key in manager._ThemeManager__created_themes

    combined_theme_id = manager._ThemeManager__created_themes[theme_key]
    assert dpg.get_item_theme(node_id) == dpg.get_alias_id(combined_theme_id)


def test_apply_theme_replaces_previous(env):
    """
    Проверяет, что повторный вызов apply_theme заменяет темы, а не добавляет к ним.
    """
    with dpg.window():
        button_id = dpg.add_button(label="Test Button")

    manager = ThemeManager()
    manager.apply(button_id, Themes.DEFAULT)
    manager.apply(button_id, Themes.ERROR)

    item_themes = manager._ThemeManager__item_themes[button_id]
    assert Themes.ERROR in item_themes
    assert Themes.DEFAULT not in item_themes
    assert len(item_themes) == 1


def test_get_theme_returns_valid_dpg_item(env):
    """
    Проверяет, что get_theme возвращает существующий DPG-элемент.
    """
    manager = ThemeManager()
    theme_id = manager.get(Themes.DEFAULT)

    assert dpg.does_item_exist(theme_id)
