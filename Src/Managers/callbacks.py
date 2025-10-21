from typing import Any, Callable
from dataclasses import dataclass

import dearpygui.dearpygui as dpg

from Src.Managers.event_manager import Event_manager
from Src.Enums.callbacktype import CallbackType
from Src.Logging import Logger_factory,Logger



@dataclass
class CallbackInfo:
    """Информация о callback-функции и условии её вызова."""
    callbacks: list[Callable]
    trigger_value: Any = None




class DPGCallback:
    """
    Обработчик callbacks для элементов DearPyGui с использованием Event_manager.
    """


    def __init__(self, item_id: str|int) -> None:
        """
        Инициализация обработчика callback.

        Args:
            item_id: Идентификатор элемента DearPyGui
        """
        self.__item_id = item_id
        self.logger: Logger = Logger_factory.from_instance()('events')
        
        self.__prev_values = {
            CallbackType.VALUE: None,
            CallbackType.STATE: {}
        }
        self.__callbacks = {}
        
        if not dpg.does_item_exist(self.__item_id):
            self.logger.warning(f"Элемент {item_id} не существует. Регистрация события прервана.")
            return

        self.logger.info(f"DPGCallback инициализирован для элемента {item_id}")


    def __check_value_changes(self) -> None:
        """Проверяет изменения значения элемента с учетом trigger_value."""
        event_name = self._create_event_name(CallbackType.VALUE)
        
        if event_name not in self.__callbacks:
            return

        current_value = self._get_current_value(CallbackType.VALUE)
        
        if current_value is None:
            return

        callback_info = self.__callbacks[event_name]
        
        if callback_info.trigger_value is not None:
                if current_value == callback_info.trigger_value:
                    Event_manager.trigger_custom_event(
                        f"{self.__item_id}_value_change"
                    )
            
        else:
            if current_value != self.__prev_values[CallbackType.VALUE]:
                Event_manager.trigger_custom_event(
                    f"{self.__item_id}_value_change"
                )
        self.__prev_values[CallbackType.VALUE] = current_value


    def __check_state_changes(self) -> None:
        """Проверяет изменения состояний элемента с учетом trigger_value."""
        for state, prev_state_value in list(self.__prev_values[CallbackType.STATE].items()):
            event_name = self._create_event_name(CallbackType.STATE, state)
            
            if event_name not in self.__callbacks:
                continue

            current_state = self._get_current_value(CallbackType.STATE, state)
            
            if current_state is None:
                continue

            callback_info = self.__callbacks[event_name]

            if callback_info.trigger_value is not None:
                if current_state == callback_info.trigger_value:
                    Event_manager.trigger_custom_event(
                        f"{self.__item_id}_state_{state}_change"
                    )
            
            else:
                if current_state != prev_state_value:
                    Event_manager.trigger_custom_event(
                        f"{self.__item_id}_state_{state}_change"
                    )
            self.__prev_values[CallbackType.STATE][state] = current_state


    def _create_event_name(self, callback_type: CallbackType, state: str = "") -> str:
        """Создает уникальное имя события для callback."""
        base_name = f"{self.__item_id}_{callback_type.value}"
        return f"{base_name}_{state}_change" if state else f"{base_name}_change"


    def _register_callback(
        self, 
        event_name: str, 
        callback: Callable, 
        trigger_value: Any = None
    ) -> bool:
        """Регистрирует новый callback."""
        if not callable(callback):
            self.logger.warning(f"Некорректный callback для события {event_name}")
            return False

        if event_name not in self.__callbacks:
            self.__callbacks[event_name] = CallbackInfo(
                callbacks=[], 
                trigger_value=trigger_value
            )
        
        if callback not in self.__callbacks[event_name].callbacks:
            self.__callbacks[event_name].callbacks.append(callback)
            Event_manager.add_custom_event(event_name, [callback])
            self.logger.debug(f"Callback зарегистрирован для события {event_name}")
            return True
        
        return False


    def _add_generic_callback(
        self, 
        callback_type: CallbackType, 
        callback: Callable, 
        trigger_value: Any = None, 
        state: str = None
    ) -> None:
        """Универсальный метод добавления callback."""
        if not dpg.does_item_exist(self.__item_id):
            self.logger.warning(f"Невозможно добавить callback. Элемент {self.__item_id} не существует.")
            return

        if callback_type == CallbackType.STATE and not state:
            self.logger.warning("Состояние не может быть пустым")
            return

        event_name = self._create_event_name(
            callback_type, 
            state if callback_type == CallbackType.STATE else ""
        )
        
        if self._register_callback(event_name, callback, trigger_value):
            self._update_previous_value(callback_type, state)
            log_msg = (
                f"Callback состояния добавлен для элемента {self.__item_id}, состояние {state}"
                if callback_type == CallbackType.STATE 
                else f"Callback значения добавлен для элемента {self.__item_id}"
            )
            self.logger.info(log_msg)


    def _get_current_value(
        self, 
        callback_type: CallbackType, 
        state: str = ""
    ) -> Any:
        """Получает текущее значение или состояние элемента."""
        if not dpg.does_item_exist(self.__item_id):
            self.logger.warning(f"Элемент {self.__item_id} не существует")
            return None

        if callback_type == CallbackType.VALUE:
            return dpg.get_value(self.__item_id)
        
        if callback_type == CallbackType.STATE:
            item_state = dpg.get_item_state(self.__item_id)
            return item_state.get(state)
        
        return None


    def _update_previous_value(
        self, 
        callback_type: CallbackType, 
        state: str = None
    ) -> None:
        """Обновляет сохраненное значение или состояние элемента."""
        current_value = self._get_current_value(callback_type, state)
        
        if current_value is None:
            self.logger.warning(f"Не удалось получить текущее значение для элемента {self.__item_id}")
            return

        if callback_type == CallbackType.VALUE:
            self.__prev_values[callback_type] = current_value
        else:
            self.__prev_values[callback_type][state] = current_value

        
    def _check_changes(self, callback_type: CallbackType) -> None:
        """Универсальный метод проверки изменений."""
        if callback_type == CallbackType.VALUE:
            self.__check_value_changes()
        else:
            self.__check_state_changes()


    def add_value_callback(self, callback: Callable, trigger_value: Any = None) -> None:
        """
        Добавляет callback на изменение значения элемента.

        Args:
           callback (Callable): Функция, которая будет вызвана при изменении значения.
           trigger_value (Any, optional): Значение, при котором будет вызван callback.
              Если None, то callback будет вызван при любом изменении значения.
        """
        self._add_generic_callback(CallbackType.VALUE, callback, trigger_value)


    def add_state_callback(
        self, 
        state: str, 
        callback: Callable, 
        trigger_value: Any = None
    ) -> None:
        """
        Добавляет callback на изменение состояния элемента.
        
        Args:
            state (str): Состояние, которое будет отслеживаться.
            callback (Callable): Функция, которая будет вызвана при изменении значения.
            trigger_value (Any, optional): Значение, при котором будет вызван callback.
              Если None, то callback будет вызван при любом изменении значения.
        """
        self._add_generic_callback(
            CallbackType.STATE, 
            callback, 
            trigger_value, 
            state
        )


    def check(self) -> None:
        """
        Проверяет изменения значений и состояний элемента и вызывает
        соответствующие callbacks при обнаружении изменений.
        """
        if not dpg.does_item_exist(self.__item_id):
            self.logger.warning(f"Элемент {self.__item_id} не существует во время проверки")
            return

        self._check_changes(CallbackType.VALUE)
        self._check_changes(CallbackType.STATE)
