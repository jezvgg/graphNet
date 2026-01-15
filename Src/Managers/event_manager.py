from typing import Callable

import dearpygui.dearpygui as dpg

from Src.Logging import logging
from Src.Enums.eventtypes import EventType, ITEM_EVENTS, GLOBAL_EVENTS
from Src.Utils import singleton, factorymethod, lateinit




@singleton
class EventManager:
    """
    Менеджер событий для DearPyGui.
    Использует ItemHandlerRegistry для событий (click, hover и т.д.).
    """
    __logger = lateinit(logging(), 'events')
    __global_handler_registry: str | int = None

    _events: dict[str, list[Callable]] = {}


    @factorymethod
    def add(self, event_type: EventType, *args, **kwargs):
        self.__logger.error(f"Нет обработчика для события: {event_type}")


    @add.register(ITEM_EVENTS)
    def add_item_handler(self, event_type: EventType, 
            item_id: str | int = None,
            handler: Callable = None, 
            user_data = None):
        '''Регестрирует обработчик события объекта.'''
        if not (item_id and dpg.does_item_exist(item_id)):
            self.__logger.error(f"Неккоректный индитификатор ({item_id}) для наложения события.")
        
        registry_id = self.__get_item_registry(item_id)
        event_type(parent=registry_id, callback=handler, user_data=user_data)
        self.__logger.info(f"Обработчик '{event_type}' добавлен к элементу {item_id}")


    @add.register(EventType.VIEWPORT_RESIZE)
    def add_viewport_handler(self, event_type: EventType, handler: Callable = None):
        '''Регестрирует обработчики связанные с экраном вывода.'''
        event_type(callback=handler)
        self.__logger.info(f"Обработчик '{event_type}' установлен для viewport")


    @add.register(GLOBAL_EVENTS)
    def add_global_event(self, event_type: EventType,
            handler: Callable = None, 
            user_data = None):
        '''Регестрирует глобальные обработчики.'''
        global_registry = self.__get_global_registry()
        event_type(parent=global_registry, callback=handler, user_data=user_data)
        self.__logger.info(f"Глобальный обработчик '{event_type}' добавлен")


    def clear(self, item_id: str | int):
        """Удаляет все обработчики, привязанные к элементу."""
        if not dpg.does_item_exist(item_id):
            self.__logger.warn(f"Попытка удаления обработчиков с ({item_id}), которого не существует")
            return

        dpg.configure_item(item_id, callback=None, user_data=None)

        registry_id = dpg.get_item_info(item_id).get("handlers")
        if registry_id:
            dpg.delete_item(registry_id)

        self.__logger.info(f"Обработчики для {item_id} очищены")


    def __get_item_registry(self, item_id: str | int) -> int:
        """Получает или создает ItemHandlerRegistry для элемента."""
        registry_id = dpg.get_item_info(item_id).get("handlers")
        if not registry_id:
            registry_id = dpg.add_item_handler_registry()
            dpg.bind_item_handler_registry(item_id, registry_id)
            self.__logger.info(f"Создан ItemHandlerRegistry ({registry_id}) для {item_id}")

        return registry_id


    def __get_global_registry(self):
        """Создает глобальный registry для обработчиков, если его нет."""
        if self.__global_handler_registry is None:
            self.__global_handler_registry = dpg.add_handler_registry()
            self.__logger.info(f"Создан GlobalHandlerRegistry ({self.__global_handler_registry})")

        return self.__global_handler_registry