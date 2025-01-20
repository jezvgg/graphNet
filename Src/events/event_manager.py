from typing import Callable, Optional




class Event_manager:
    """
    Менеджер кастомных событий (Синглтон).
    
    Attributes:
        events: dict[str, list[Callable]] - словарь событий и их обработчиков
    """
    
    _instance = None
    

    def __new__(cls):
        """Создание единственного экземпляра класса"""
        if cls._instance is None:
            cls._instance = super(Event_manager, cls).__new__(cls)
            cls._instance._events = {}
        return cls._instance


    def add_event(self, event_name: str, handler: list[Callable]) -> None:
        """
        Подписка на событие.
        
        Args:
            event_name: str - название события
            handler: list[Callable] - функции-обработчики события
        """
        if event_name not in self.events:
            self.events[event_name] = []
        
        for event in handler:
            self.events[event_name].append(event)


    def remove(self, event_name: Optional[str] = None, handler: Optional[Callable] = None) -> None:
        """
        Отписка от события, или очистка обработчика события или всех событий.
        
        Args:
            event_name: str - название события, None - очистка всех событий
            handler: Callable - функция-обработчик для удаления
        """

        if event_name in self.events and handler in self.events[event_name]:
            self.events[event_name].remove(handler)
        elif event_name and handler is None:
            self.events[event_name].clear()
            del self.events[event_name]
        else:
            self.events.clear()
        
            
    def call_event(self, event_name: str, *args, **kwargs) -> None:
        """
        Вызов события.
        
        Args:
            event_name: str - название события
            *args, **kwargs - аргументы передаваемые обработчикам
        """
        if event_name not in self.events:
            raise ValueError(f"Event '{event_name}' is not defined")
            
        for handler in self.events[event_name]:
            handler(*args, **kwargs)


    @property        
    def events(self) -> dict[str, list[Callable]]:
        """
        Свойство для доступа к словарю событий.
        
        Returns:
            dict[str, list[Callable]] - словарь событий и их обработчиков
        """
        return self._events
