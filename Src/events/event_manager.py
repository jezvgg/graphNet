from typing import Callable

from Src.Logging import Logger_factory,Logger




class Event_manager:
    """
    Класс-наблюдатель для управления пользовательскими событиями.

    Class Attributes:
        _events: dict[str, list[Callable]] - словарь событий и их обработчиков
        logger: Logger - экземпляр логгера
    """

    _events: dict[str, list[Callable]] = {}
    logger: Logger = Logger_factory.from_instance()('events')


    @classmethod
    def add_custom_event(cls, event_name: str, handlers: list[Callable]) -> None:
        """
        Добавление пользовательского события и его обработчиков.

        Args:
            event_name: str - название события
            handlers: list[Callable] - список функций-обработчиков события
        """
        if event_name not in cls._events:
            cls._events[event_name] = []

        cls._events[event_name]+=handlers


    @classmethod
    def remove_custom_event(cls, event_name: str = None, handler: Callable = None) -> None:
        """
        Отписка от события, или очистка обработчика события или всех событий.
        
        Args:
            event_name: str, optional - название события. Если None, очищаются все события
            handler: Callable, optional - функция-обработчик для удаления
        """
        # Если не указано имя события, очищаем все события
        if not event_name:
            cls._events.clear()
            return
        # Если указан конкретный обработчик, удаляем только его
        if handler and handler in cls._events[event_name]:
            cls._events[event_name].remove(handler)
        else:
            # Иначе удаляем все обработчики события
            del cls._events[event_name]


    @classmethod
    def trigger_custom_event(cls, event_name: str) -> None:
        """
        Вызов пользовательского события.

        Args:
            event_name: str - название события
            *args, **kwargs - аргументы, передаваемые обработчикам
        """
        if event_name not in cls._events:
            cls.logger.error(f"Событие '{event_name}' не определено")
            return

        for handler in cls._events[event_name]:
            handler()



    @classmethod
    def get_events(cls) -> dict[str, list[Callable]]:
        """
        Метод для доступа к словарю событий.

        Returns:
            dict[str, list[Callable]] - словарь событий и их обработчиков
        """
        return cls._events