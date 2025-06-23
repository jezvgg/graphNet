from typing import Callable
from functools import singledispatch
from enum import Enum

import dearpygui.dearpygui as dpg

from Src.Models import File
from Src.Utils import factorymethod
from Src.Nodes import ParameterNode, DataNode
from Src.Enums import Activations,Losses,Metrics


class AttributesFactory:
    '''
    Фабрика, реализующая создание аттрибутов нода в зависимости от переданных параметров.
    '''

    @staticmethod
    def check_kwargs(func: Callable, kwargs: dict):
        annotations = func.__annotations__ | getattr(getattr(func, '__wrapped__', None), '__annotations__', {})
        union_annotations = dict([(key, kwargs[key]) for key in kwargs if key in annotations])
        return union_annotations

    @singledispatch
    @staticmethod
    def build(value, *args, **kwargs):
        raise Exception("Не получилась диспатчеризация для построения узла")

    @build.register(tuple)
    @staticmethod
    def build_tuple(shape: tuple, *args, **kwargs):
        '''
        Если передан tuple, то создаётся группа инпутов.
        '''
        with dpg.node_attribute(parent=kwargs.get('parent') or 0, attribute_type=dpg.mvNode_Attr_Static) as attr:
            kwargs = AttributesFactory.check_kwargs(dpg.group, kwargs)
            kwargs["parent"] = attr
            with dpg.group(horizontal=True, *args, **kwargs) as item:
                for hint in shape:
                    AttributesFactory.build_input(hint, parent=item)

                # Если отсутсвует label, то создаст пустой текст
                dpg.add_text(kwargs.get('label') or '')
            return item

    @build.register(type)
    @factorymethod
    def build_attribute(value: type, *args, **kwargs):
        raise Exception(f"Не получилось диспатчеризация типа {value}")

    @build_attribute.register(
        ParameterNode.__subclasses__() + \
        DataNode.__subclasses__()
    )
    def build_object(value: ParameterNode, *args, **kwargs):
        kwargs = AttributesFactory.check_kwargs(dpg.node_attribute, kwargs)
        with dpg.node_attribute(*args, **kwargs, attribute_type=dpg.mvNode_Attr_Input, user_data=[]) as attr:
            dpg.add_text(kwargs.get('label'), label=kwargs.get('label'))
        return attr

    @build_attribute.register((int, float, str, bool, File, Activations, Losses, Metrics))
    def build_type(value: type, *args, **kwargs):
        with dpg.node_attribute(parent=kwargs.get('parent') or 0, attribute_type=dpg.mvNode_Attr_Static) as attr:
            kwargs['parent'] = attr
            AttributesFactory.build_input(value, *args, **kwargs)
        return attr


    @factorymethod
    def build_input(value: type, parent: str | int, *args, **kwargs):
        raise Exception("Не получилось диспатчеризация для построения инпута")

    build_input.register(int)(
        lambda value, parent, *a, **k: dpg.add_input_int(**AttributesFactory.check_kwargs(dpg.add_input_int, k)))
    build_input.register(str)(
        lambda value, parent, *a, **k: dpg.add_input_text(**AttributesFactory.check_kwargs(dpg.add_input_text, k)))
    build_input.register(float)(
        lambda value, parent, *a, **k: dpg.add_input_float(**AttributesFactory.check_kwargs(dpg.add_input_float, k)))
    build_input.register(bool)(
        lambda value, parent, *a, **k: dpg.add_checkbox(**AttributesFactory.check_kwargs(dpg.add_checkbox, k)))

    @build_input.register(File)
    def build_file(value: File, *args, **kwargs):
        '''
        Если передан File, то создаётся группа из файлового выбора и их просмотра.
        '''
        kwargs = AttributesFactory.check_kwargs(dpg.node_attribute, kwargs)
        browser_id = dpg.generate_uuid()
        group_id = dpg.generate_uuid()

        with dpg.file_dialog(directory_selector=False, show=False, modal=True, \
                             width=1400, height=800, tag=browser_id,
                             callback=lambda _, appdata: dpg.set_item_user_data(group_id, appdata)):
            dpg.add_file_extension(".*")

        with dpg.group(*args, **kwargs, tag=group_id) as item:
            dpg.add_button(label="Choose file...", callback=lambda: dpg.show_item(browser_id))

        return item

    @build_input.register((Activations,Losses,Metrics))
    def build_enums(value: Enum, *args, **kwargs):
        kwargs['items'] = [item.name for item in value]
        dpg.add_combo(**kwargs)
