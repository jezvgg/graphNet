from dataclasses import dataclass
from abc import ABC
from typing import Callable
import inspect

import dearpygui.dearpygui as dpg

from Src.Logging import Logger_factory, Logger
from Src.Config.parameter import Parameter, AttrType


class AbstractNode(ABC):
    '''
    Нода (узел графа), класс который используется для сохранения связей в графе, а также информации о ноде. 

    Attributes:
        node_tag: str | int - индетификатор ноды (dpg.node)
        incoming: list[Node] - связи с нодами, которые подключенны к этой ноде. (Приходящие)
        outgoing: list[Node] - связи с нодами, к которым подключенна эта нода. (Уходящие)
    '''
    __error_message: str = None
    _error_id: int | str = None

    node_tag: str | int
    # Устанавливаем связи не между узлами, а между их аттрибутами
    incoming: dict[str | int, list[str | int]]
    outgoing: dict[str | int, list[str | int]]
    annotations: dict[str, Parameter]
    logic: Callable
    docs: str
    input: bool
    output: bool
    logger: Logger


    def __init__(self, node_tag: int | str, annotations: dict[str: type], \
                 logic: Callable, docs: str = None, input = True, output = True):
        '''
        Нода (узел графа), класс который используется для сохранения связей в графе, а также информации о ноде. 

        Args:
            layer: keras.layers.Layer - слой, логику которого нода хранит.
            annotations: dict[str, type] - аннотации на аргументы, которые нужно вводить, для создания слоя.
            docs: str - документация к слою
            node_tag: str | int = None - индетификатор ноды (dpg.node)
        '''
        self.node_tag = node_tag
        self.annotations = annotations
        self.logic = logic
        self.incoming = {}
        self.outgoing = {}
        self.input = input
        self.output = output
        self.OUTPUT = None

        if not docs: docs = inspect.getdoc(self.logic)
        self.docs = docs

        self.logger = Logger_factory.from_instance()("nodes")

        with dpg.stage():
            self._error_id = dpg.add_text("ОШИБКА!")


    def __repr__(self) -> str:
        return f"{self.node_tag}"


    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.node_tag} {dict(incoming=self.incoming, outgoing=self.outgoing)}"
    

    def __hash__(self):
        return self.node_tag


    def compile(self, kwargs: dict = None) -> bool:
        '''
        Основной метод нодов, содержащий логику их работы. Тут создаются слои нейронной сети, проходит обучение и т.д. В зависимости от ноды, будет разная логика.
        '''
        if not kwargs: kwargs = {}
        arguments = dpg.get_item_children(self.node_tag)[1]

        self.logger.info(f"Компиляция ноды - {self.__class__.__name__}")
        self.logger.debug(f"Аргументы ноды - {arguments}")

        for argument in arguments:
            name = dpg.get_item_label(argument)

            if name not in self.annotations or \
            self.annotations[name].attr_type == AttrType.OUTPUT: continue

            kwargs[name] = self.annotations[name].get_value(argument)

            self.logger.debug(kwargs)

        try: 
            self.OUTPUT = self.logic(**kwargs)
            self.lower_error()

        except AttributeError as ex:
            self.raise_error(ex, "Некорректные данные для узла")
            return False
        
        except Exception as ex:
            self.raise_error(ex)
            return False
            
        return True
    

    def raise_error(self, error_message: str, error_message_type: str = "Неизвестная ошибка"):
        with dpg.theme() as error_theme:
            with dpg.theme_component(dpg.mvNode):
                dpg.add_theme_color(dpg.mvNodeCol_NodeOutline, (175, 0, 0, 255), category=dpg.mvThemeCat_Nodes)

            with dpg.theme_component(dpg.mvTooltip):
                dpg.add_theme_color(dpg.mvThemeCol_Border, (175, 0, 0, 255), category=dpg.mvThemeCat_Core)

        dpg.bind_item_theme(self.node_tag, error_theme)

        dpg.move_item(item=self._error_id, parent=self.node_tag)
            
        with dpg.tooltip(parent=self._error_id):
            dpg.add_text(f"{error_message_type}:")
            dpg.add_text(error_message)

        self.logger.warning(f"Поймана ошибка ({error_message_type}): {error_message}")


    def lower_error(self):
        with dpg.theme() as default_theme:
            with dpg.theme_component(dpg.mvNode):
                dpg.add_theme_color(dpg.mvNodeCol_NodeOutline, (100, 100, 100, 255), category=dpg.mvThemeCat_Nodes)

            with dpg.theme_component(dpg.mvTooltip):
                dpg.add_theme_color(dpg.mvThemeCol_Border, (78, 78, 78, 255), category=dpg.mvThemeCat_Core)
            
        dpg.bind_item_theme(self.node_tag, default_theme)

        if self._error_id and dpg.does_item_exist(self._error_id): 
            dpg.delete_item(self._error_id)
        self.__error_message = None


@dataclass
class node_link:
    '''
    Класс для dpg.add_node_link, указывает какие аттрибуты узлов связываются.
    '''
    outgoing: str | int
    incoming: str | int