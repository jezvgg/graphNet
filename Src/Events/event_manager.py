from typing import Callable

import dearpygui.dearpygui as dpg

from Src.Enums import EventType




class EventManager:
    """
    Менеджер событий для DearPyGui.
    Использует ItemHandlerRegistry для событий (click, hover и т.д.).
    """
    _logger = None
    _global_handler_registry = None


    @classmethod
    def set_logger(cls, logger):
        """Устанавливает экземпляр логгера для класса."""
        cls._logger = logger
        cls._logger and cls._logger.info("Logger установлен для EventManager")


    @classmethod
    def add(cls, event_type: EventType, item_id: str | int = None,
            handler: Callable = None, *, user_data=None):
        """
        Регистрирует обработчик на событие.
        Обрабатывает item-specific, global и viewport события.

        Args:
            event_type (EventType): Тип события из перечисления EventType.
            item_id (str | int, optional): ID элемента DPG. Для глобальных событий должен быть None.
            handler (Callable, optional): Функция-обработчик (sender, app_data, user_data).
            user_data (any, optional): Пользовательские данные для передачи в обработчик.
        """

        # Обработчики специфичные для объектов
        if item_id and dpg.does_item_exist(item_id):
            registry_id = cls._get_or_create_item_registry(item_id)
            event_type(parent=registry_id, callback=handler, user_data=user_data)
            cls._logger and cls._logger.info(f"Обработчик '{event_type}' добавлен к элементу {item_id}")
            return

        # Обработчик для viewport'а
        if event_type == EventType.VIEWPORT_RESIZE:
            event_type(handler)
            cls._logger and cls._logger.info(f"Обработчик '{event_type}' установлен для viewport")
            return

        # Глобальные обработчики
        global_registry = cls._get_or_create_global_registry()
        event_type(parent=global_registry, callback=handler, user_data=user_data)
        cls._logger and cls._logger.info(f"Глобальный обработчик '{event_type}' добавлен")


    @classmethod
    def add_value_changed(cls, item_id: str | int, handler: Callable, *, user_data=None):
        """Регистрирует обработчик на изменение значения элемента."""
        if dpg.does_item_exist(item_id):
            dpg.configure_item(item_id, callback=handler, user_data=user_data)
            cls._logger and cls._logger.info(f"Обработчик 'value_changed' установлен для {item_id}")


    @classmethod
    def clear(cls, item_id: str | int):
        """Удаляет все обработчики, привязанные к элементу."""
        if not dpg.does_item_exist(item_id):
            return

        dpg.configure_item(item_id, callback=None, user_data=None)

        registry_id = dpg.get_item_info(item_id).get("handlers")
        if registry_id:
            dpg.delete_item(registry_id)

        cls._logger and cls._logger.info(f"Обработчики для {item_id} очищены")


    @classmethod
    def _get_or_create_item_registry(cls, item_id: str | int) -> int:
        """Получает или создает ItemHandlerRegistry для элемента."""
        registry_id = dpg.get_item_info(item_id).get("handlers")
        if not registry_id:
            registry_id = dpg.add_item_handler_registry()
            dpg.bind_item_handler_registry(item_id, registry_id)
            cls._logger and cls._logger.debug(f"Создан ItemHandlerRegistry ({registry_id}) для {item_id}")
        return registry_id


    @classmethod
    def _get_or_create_global_registry(cls):
        """Создает глобальный registry для обработчиков, если его нет."""
        if cls._global_handler_registry is None:
            cls._global_handler_registry = dpg.add_handler_registry()
        return cls._global_handler_registry