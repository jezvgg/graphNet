import json

import dearpygui.dearpygui as dpg

from Src.Logging import Logger_factory, Logger
from Src.page import Page
from Src.Nodes import NodeEditor


class PageController:
    page_graph: dict[Page, tuple[Page]]
    start_page: Page
    __logger: Logger


    def __init__(self):
        '''
        Здесь задаётся граф связей страниц.
        '''
        with open("Src/Logging/logger_config_debug.json") as f:
            config = json.load(f)

        self.__logger = Logger_factory.from_instance()('pages', config)

        nodeEditor_page = NodeEditor(minimap=True, minimap_location=dpg.mvNodeMiniMap_Location_TopRight)

        self.page_graph = {nodeEditor_page: ()}

        self.start_page = nodeEditor_page


    def start_polling(self, parent: str | int):
        self.__logger.info("Первая страница.")
        self.start_page.show(parent=parent)

        with dpg.item_handler_registry() as handler:
            dpg.add_item_visible_handler(callback=lambda :self.poll(self.start_page, parent))
        dpg.bind_item_handler_registry(self.start_page.page_tag, handler)

    
    def poll(self, last_page: Page, parent: str | int):
        self.__logger.info(f"Страница {last_page.__class__.__name__} скрыта.")
        next_page = self.page_graph[last_page][last_page.state]
        next_page.show(parent, next_page.user_data)
        self.__logger.info(f"Страница {next_page.__class__.__name__} отображена.")

        with dpg.item_handler_registry() as handler:
            dpg.add_item_visible_handler(callback=lambda :self.poll(self.start_page, parent))
        dpg.bind_item_handler_registry(next_page.page_tag, handler)

        