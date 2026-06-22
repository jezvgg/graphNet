import pytest
import dearpygui.dearpygui as dpg


@pytest.fixture(scope="session", autouse=True)
def dpg_session():
    dpg.create_context()
    dpg.create_viewport(title='Test Session')
    dpg.setup_dearpygui()
    yield
