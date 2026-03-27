from typing import Callable
from itertools import chain
import traceback

import dearpygui.dearpygui as dpg
from keras import layers

from Src.Enums.attr_type import AttrType
from Src.Logging import logging, Logger
from Src.Nodes import AbstractNode, InputLayerNode, LayerNode
from Src.Config.node_list import NodeAnnotation, Parameter, ANode, Single
from Src.Managers import ThemeManager

BUTTON_HEIGHT: int = 32
LINE_HEIGHT: int = 30
PADDING: int = 8
LIST_HEADER_WIDTH: int = 210
LIST_FIELD_WIDTH: int = 120

class NodeBuilder:
    '''
    Класс реализующий логику связывания Keras и Нодов.

    Attributes:
        factory: InputsFactory - фабрика конвертации аннотаций в инпуты
        layers_list: dict[str: AbstractNode] - список слоёв с параметрами, которые использовать в конструкторе
    '''
    node_list: dict[str, dict[str, list[NodeAnnotation]]]
    delete_callback: Callable
    logger: Logger


    def __init__(self, 
                 node_list: dict[str: AbstractNode],
                 delete_callback: Callable):
        '''
        Args:
            layers_list: dict[str: AbstractNode] - список слоёв с параметрами, которые использовать в конструкторе
        '''
        self.logger = logging()("nodes")
        self.delete_callback = delete_callback
        self.node_list = node_list


    def build_list(self, parent: str | int) -> str | int:
        '''
        Построить список (tree_node) из списка слоёв. Используется для панели слева в конструкторе.

        Args:
            parent: str | int - родительский элемент в котором создать список.

        Returns:
            str | int - индетификатор списка
        '''
        with dpg.group(parent=parent) as list:
            for anchor in self.node_list.keys():
                with dpg.tree_node(label=anchor) as tree_anchor:

                    for subanchor in self.node_list[anchor].keys():
                        with dpg.tree_node(label=subanchor) as tree_subanchor:

                            for node in self.node_list[anchor][subanchor]:
                              self._build_list_node(node_data=node, parent=tree_subanchor)

        return list

    def _build_list_node(self, node_data: NodeAnnotation, parent: int | str) -> int | str:
      '''
      Построение элемента списка нод, визуально имитирующего ноду в редакторе.

      Args:
          node_data: NodeAnnotation - аннотация ноды из node_list
          parent:    int | str      - родительский элемент (tree_node подкатегории)

      Returns:
          int | str - идентификатор созданной группы
      '''
      
      visible_params: list[tuple[str, Parameter]] = [
          (label, param) for label, param in node_data.annotations.items()
          if label != 'INPUT' and not isinstance(param.hint, ANode)
      ]

      with dpg.group(horizontal=False, parent=parent, user_data=node_data) as group:
      
        with dpg.drag_payload(parent=group, drag_data=group):
            dpg.add_text(node_data.label)

        header_button: int | str = dpg.add_button(
            label=node_data.label,
            width=LIST_HEADER_WIDTH
        )

        layer_theme = ThemeManager._themes_config[node_data.node_type.theme_name]
        title_color = layer_theme["mvNode"]["mvNodeCol_TitleBar"]
        with dpg.theme() as btn_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, title_color)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, title_color)
        dpg.bind_item_theme(header_button, btn_theme)

        if node_data.input:
            dpg.add_text("INPUT", indent=4)
        
        with dpg.tree_node(label="Docs", indent=4) as docs_node:
          dpg.add_text(node_data.docs, wrap=LIST_HEADER_WIDTH - 20)
        
        for label, param in visible_params:
              with dpg.group(horizontal=True) as param_group:
                param.hint.build(label=label,
                                parent=group,
                                width=LIST_FIELD_WIDTH,
                                enabled=False)

        if node_data.output:
          dpg.add_text("OUTPUT", indent=4)
        
        dpg.add_spacer(height=2)
        dpg.add_separator()
        dpg.add_spacer(height=10)

      return group

    def build_node(self, node_data: NodeAnnotation, parent: str | int) -> str | int:
        '''
        Построение dpg.node из класса AbstractNode. Используется, для создания новых нодов в редакторе. Ноды берутся из user_data в списке слева.

        Args:
            node: AbstractNode - нода из которой создать dpg.node
            parent: str | int - родитель, внутри которого создать ноду. Чаще всего это dpg.node_editor.

        Returns:
            str | int - индетификатор новой dpg.node.
        '''
        node_id = dpg.generate_uuid()
        node: AbstractNode = node_data.node_type(node_id, **node_data.kwargs)

        with dpg.node(label=node_data.label, parent=parent, user_data=node, tag=node_id):
            if node_data.input:
                node_data.input.build(label="INPUT", parent=node_id)
                
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                with dpg.tree_node(label="Docs"):
                    dpg.add_text(node.docs)

            for label, attribute in node.annotations.items():
                if label == 'INPUT': continue
                self.logger.debug(f"Attribute label: {label}")
                attr = attribute.build(label=label, parent=node_id)

            with dpg.node_attribute(label="Delete", attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_button(label="Delete", callback=lambda: self.delete_callback(node_id))

            if node_data.output:
                node_data.output.build(label="OUTPUT", parent=node_id)

        node.default_theme()

        return node_id
    

    def build_input(self, parent: str | int) -> str | int:
        '''
        Особенный метод, реализующий построение слоя входа.

        Args:
            parent: str | int - родительский элемент в котором построить нод. Чаще всего node_editor.
            shape: tuple[int] - форма данных, передаётся в входной слой.

        Returns:
            str | int - индетификатор новой ноды
        '''
        # TODO: Сделать типизированную передачу у shape TableDataNode
        layer = NodeAnnotation(
            label="Input",
            node_type=InputLayerNode, 
            logic = InputLayerNode.create_input,
            annotations = {
                    "shape": Parameter(AttrType.INPUT, ANode[Single[object]]),
                },
            input=False,
            output=LayerNode
            )

        node_id = self.build_node(layer, parent=parent)

        return node_id
    

    def compile_graph(self, start_nodes: list[AbstractNode]) -> set[AbstractNode]:
        '''
        Компиляция графа, от его концов. Работает через обход в ширину. Вызывает метод compile у нода, если все ноды, пришедшие к нему уже скомпилированы. Начинает с нодов, у которых нет входов.
        '''

        visited = set()
        queue = start_nodes[:]
        self.logger.info("Началась сборка графа.")
        status = True

        while queue:
            self.logger.debug(f"Текущая очередь - {queue}")
            current_node = queue.pop(0)
            self.logger.debug(f"Текущая нода - {current_node}")

            if all([dpg.get_item_user_data(dpg.get_item_parent(value)) in visited \
                for value in chain(*current_node.incoming.values())]):
                self.logger.debug("Нода подошла.")

                try:
                    status = current_node.compile()

                except Exception as ex:
                    self.raise_error(ex)
                    status = False

                if not status: break
                
                self.logger.debug(f"resulted OUTPUT - {current_node.OUTPUT}")

                for attr_id in chain(*current_node.outgoing.values()):
                    neightbor: AbstractNode = dpg.get_item_user_data(dpg.get_item_parent(attr_id))
                    if neightbor not in queue:
                        queue.append(neightbor)

                visited.add(current_node)

        return visited
    

    def raise_error(self, error_message: str, error_message_type: str = "Неизвестная ошибка"):
        with dpg.window(label="Непревиденная ошибка", modal=True, no_title_bar=True, \
                        no_resize=True, no_move=True) as error_window:
            dpg.add_text("Произошла непредвиденная ошибка, сообщите пожалуйста разработчикам.")
            dpg.add_text(f"{error_message_type}:")
            dpg.add_text(error_message)
            dpg.add_text(traceback.format_exc())
            dpg.add_button(label="Close", callback=lambda: dpg.configure_item(error_window, show=False))

        # TODO: Прикрепить модальное окно на середину при изменении размера
        dpg.set_item_pos(error_window, [
            (dpg.get_viewport_width() - dpg.get_item_width(error_window)) // 4,
            (dpg.get_viewport_height() - dpg.get_item_height(error_window)) // 3
        ])

        self.logger.warning(f"Поймана ошибка ({error_message_type}): {error_message}")
        
