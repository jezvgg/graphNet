from typing import Callable
from collections import defaultdict

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

    __viewport_calls: list[Callable] = []
    __global_calls: dict[GLOBAL_EVENTS, list[Callable]] = defaultdict(list)
    __items_calls: dict[int | str, dict[ITEM_EVENTS, list[Callable]]] = defaultdict(lambda: defaultdict(list))


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


    def __raise_calls(self, calls: list[Callable], *args, **kwargs):
        print(args, kwargs)
        for call in calls: call(*args, **kwargs)


    def __get_callback(self, calls: list[Callable]):
        return lambda sender, app_data: self.__raise_calls(calls, sender, app_data)


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
        self.__items_calls[item_id][event_type].append(handler)
        callback = self.__get_callback(self.__items_calls[item_id][event_type])
        event_type(parent=registry_id, callback=callback, user_data=user_data)

        self.__logger.info(f"Обработчик '{event_type}' добавлен к элементу {item_id}")
        self.__logger.debug(f"Нынешние обработчики: {self.__items_calls[item_id][event_type]}")


    @add.register(EventType.VIEWPORT_RESIZE)
    def add_viewport_handler(self, event_type: EventType, handler: Callable = None):
        '''Регестрирует обработчики связанные с экраном вывода.'''
        self.__viewport_calls.append(handler)
        event_type(callback=self.__get_callback(self.__viewport_calls))

        self.__logger.info(f"Обработчик '{event_type}' установлен для viewport")
        self.__logger.debug(f"Нынешние обработчики: {self.__viewport_calls}")


    @add.register(GLOBAL_EVENTS)
    def add_global_event(self, event_type: EventType,
            handler: Callable = None, 
            user_data = None):
        '''Регестрирует глобальные обработчики.'''
        global_registry = self.__get_global_registry()
        self.__global_calls[event_type].append(handler)
        callback = self.__get_callback(self.__global_calls[event_type])
        event_type(parent=global_registry, callback=callback, user_data=user_data)

        self.__logger.info(f"Глобальный обработчик '{event_type}' добавлен")
        self.__logger.debug(f"Нынешние обработчики: {self.__global_calls[event_type]}")


    def clear(self, item_id: str | int):
        """Удаляет все обработчики, привязанные к элементу."""
        if not dpg.does_item_exist(item_id):
            self.__logger.warn(f"Попытка удаления обработчиков с ({item_id}), которого не существует")
            return

        dpg.configure_item(item_id, callback=None, user_data=None)
        self.__items_calls[item_id] = defaultdict(list)

        registry_id = dpg.get_item_info(item_id).get("handlers")
        if registry_id:
            dpg.delete_item(registry_id)

        self.__logger.info(f"Обработчики для {item_id} очищены")
