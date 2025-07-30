from typing import Callable

import dearpygui.dearpygui as dpg

from Src.Enums import EventType




class EventManager:
    """
    Менеджер событий для DearPyGui.
        Использует ItemHandlerRegistry для событий (click, hover и т.д.).
    """
    _logger = None


    @classmethod
    def set_logger(cls, logger):
        """
        Устанавливает экземпляр логгера для класса.
        """
        cls._logger = logger
        if cls._logger:
            cls._logger.info("Logger установлен для EventManager")


    @classmethod
    def add(cls, event_type: EventType, item_id, handler: Callable, *, user_data=None):
        """
        Регистрирует обработчик на событие для указанного элемента DPG.

        Args:
            event_type (EventType): Тип события из перечисления EventType.
            item_id (int or str): ID элемента DPG.
            handler (callable): Функция-обработчик (sender, app_data, user_data).
            user_data (any, optional): Пользовательские данные для передачи в обработчик.
        """
        if not dpg.does_item_exist(item_id):
            cls._log('warning', f"Элемент {item_id} не существует. Регистрация '{event_type}' прервана.")
            return

        registry_id = dpg.get_item_info(item_id).get("handlers")
        if not registry_id:
            registry_id = dpg.add_item_handler_registry()
            dpg.bind_item_handler_registry(item_id, registry_id)
            cls._log('debug', f"Создан новый ItemHandlerRegistry ({registry_id}) для элемента {item_id}.")

        event_type(parent=registry_id, callback=handler, user_data=user_data)
        cls._log('info', f"Обработчик для '{event_type}' успешно добавлен к элементу {item_id}.")


    @classmethod
    def add_value_changed(cls, item_id, handler: Callable, *, user_data=None):
        """
        Регистрирует обработчик на изменение значения элемента.
        """
        if not dpg.does_item_exist(item_id):
            cls._log('warning', f"Элемент {item_id} не существует. Регистрация 'value_changed' прервана.")
            return

        dpg.configure_item(item_id, callback=handler, user_data=user_data)
        cls._log('info', f"Обработчик 'value_changed' установлен для элемента {item_id}.")


    @classmethod
    def clear(cls, item_id):
        """
        Удаляет все обработчики, привязанные к элементу.
        """
        if not dpg.does_item_exist(item_id):
            cls._log('warning', f"Попытка очистить обработчики для несуществующего элемента {item_id}.")
            return

        dpg.configure_item(item_id, callback=None, user_data=None)

        registry_id = dpg.get_item_info(item_id).get("handlers")
        if registry_id:
            dpg.delete_item(registry_id)

        cls._log('info', f"Все обработчики для элемента {item_id} были очищены.")


    @classmethod
    def _log(cls, level: str, message: str):
        if cls._logger and hasattr(cls._logger, level):
            getattr(cls._logger, level)(message)