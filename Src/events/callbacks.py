
from typing import Any, Callable
from enum import Enum
from dataclasses import dataclass

import dearpygui.dearpygui as dpg

from event_manager import Event_manager
from Src.Logging import Logger_factory, Logger




class CallbackType(Enum):
    """Типы отслеживаемых изменений элементов интерфейса."""
    VALUE = "value"
    STATE = "state"




@dataclass
class CallbackInfo:
    """Информация о callback-функции и условии её вызова."""
    callbacks: list[Callable]
    trigger_value: Any = None




class DPGCallback:
    """
    Обработчик callbacks для элементов DearPyGui с использованием Event_manager.

    Класс предоставляет механизм отслеживания изменений значений и состояний
    элементов интерфейса DearPyGui с возможностью привязки пользовательских callback-функций.
    """

    item_id: str|int
    logger: Logger
    _prev_values: dict[CallbackType, Any]
    _callbacks: dict[str, CallbackInfo]


    def __init__(self, item_id: str|int) -> None:
        """
        Инициализация обработчика callback.

        Args:
            item_id: Идентификатор элемента DearPyGui
        """
        self.item_id: str|int = item_id
        self.logger: Logger = Logger_factory.from_instance()('events')
        
        self._prev_values: dict[CallbackType, Any] = {
            CallbackType.VALUE: {},
            CallbackType.STATE: {}
        }
        self._callbacks: dict[str, CallbackInfo] = {}
        
        if not self._item_exists():
            self.logger.warning(f"Item {item_id} does not exist. Skipping event registration.")
            return

        self.logger.info(f"DPGCallback initialized for item {item_id}")


    def _create_event_name(self, callback_type: CallbackType, state: str = "") -> str:
        """
        Создает уникальное имя события для callback.

        Args:
            callback_type: Тип callback (VALUE или STATE)
            state: Название состояния (для STATE callbacks)

        Returns:
            Уникальное имя события
        """
        base_name = f"{self.item_id}_{callback_type.value}"
        return f"{base_name}_{state}_change" if state else f"{base_name}_change"


    def _register_callback(self, 
                         event_name: str, 
                         callback: Callable, 
                         trigger_value: Any = None) -> bool:
        """
        Регистрирует новый callback.

        Args:
            event_name: Имя события
            callback: Функция обратного вызова
            trigger_value: Значение-триггер для вызова callback

        Returns:
            True если регистрация успешна, иначе False
        """
        if not callable(callback):
            self.logger.warning(f"Invalid callback for event {event_name}")
            return

        if event_name not in self._callbacks:
            self._callbacks[event_name] = CallbackInfo(callbacks=[], trigger_value=trigger_value)
        
        if callback not in self._callbacks[event_name].callbacks:
            self._callbacks[event_name].callbacks.append(callback)
            
            Event_manager.add_custom_event(event_name, [callback])
            
            self.logger.debug(f"Callback registered for event {event_name}")
            return True
        
        return


    def add_value_callback(self, callback: Callable, trigger_value: Any = None) -> None:
        """
        Добавляет callback на изменение значения элемента.

        Args:
            callback: Функция обратного вызова
            trigger_value: Значение-триггер для вызова callback
        """
        if not self._item_exists():
            self.logger.warning(f"Cannot add value callback. Item {self.item_id} does not exist.")
            return

        event_name = self._create_event_name(CallbackType.VALUE)
        if self._register_callback(event_name, callback, trigger_value):
            self._update_previous_value(CallbackType.VALUE)
            self.logger.info(f"Value callback added for item {self.item_id}")


    def add_state_callback(self, 
                         state: str, 
                         callback: Callable, 
                         trigger_value: Any = None) -> None:
        """
        Добавляет callback на изменение состояния элемента.

        Args:
            state: Название отслеживаемого состояния
            callback: Функция обратного вызова
            trigger_value: Значение-триггер для вызова callback
        """
        if not self._item_exists():
            self.logger.warning(f"Cannot add state callback. Item {self.item_id} does not exist.")
            return
        
        if not state:
            self.logger.warning("State cannot be empty")
            return

        event_name = self._create_event_name(CallbackType.STATE, state)
        if self._register_callback(event_name, callback, trigger_value):
            self._update_previous_value(CallbackType.STATE, state)
            self.logger.info(f"State callback added for item {self.item_id}, state {state}")


    def _get_current_value(self, 
                         callback_type: CallbackType, 
                         state: str = "") -> Any:
        """
        Получает текущее значение или состояние элемента.

        Args:
            callback_type: Тип получаемого значения
            state: Название состояния

        Returns:
            Текущее значение или состояние элемента
        """
        if not self._item_exists():
            self.logger.warning(f"Item {self.item_id} does not exist")
            return

        if callback_type == CallbackType.VALUE:
            return dpg.get_value(self.item_id)
        
        if callback_type == CallbackType.STATE:
            item_state = dpg.get_item_state(self.item_id)
            return item_state.get(state)
        
        return None


    def _should_trigger_callback(self, 
                               current_value: Any, 
                               prev_value: Any, 
                               callback_info: CallbackInfo) -> bool:
        """
        Проверяет, должен ли быть вызван callback.

        Args:
            current_value: Текущее значение
            prev_value: Предыдущее значение
            callback_info: Информация о callback

        Returns:
            True если callback должен быть вызван, False иначе
        """
        if callback_info.trigger_value is not None:
            return current_value == callback_info.trigger_value
        return current_value != prev_value


    def _update_previous_value(self, 
                             callback_type: CallbackType, 
                             state: str = "") -> None:
        """
        Обновляет сохраненное значение или состояние элемента.

        Args:
            callback_type: Тип обновляемого значения
            state: Название состояния
        """
        current_value = self._get_current_value(callback_type, state)
        
        if current_value is None:
            self.logger.warning(f"Failed to get current value for item {self.item_id}")
            return

        if callback_type == CallbackType.VALUE:
            self._prev_values[callback_type] = current_value
        else:
            self._prev_values[callback_type][state] = current_value


    def _item_exists(self) -> bool:
        """
        Проверяет существование элемента в DearPyGui.

        Returns:
            True если элемент существует, False в противном случае
        """
        return dpg.does_item_exist(self.item_id)


    def check(self) -> None:
        """
        Проверяет изменения значений и состояний элемента и вызывает
        соответствующие callbacks при обнаружении изменений.
        """
        if not self._item_exists():
            self.logger.warning(f"Item {self.item_id} does not exist during check")
            return

        self._check_value_changes()
        self._check_state_changes()


    def _check_value_changes(self) -> None:
        """Проверяет изменения значения элемента."""
        event_name = self._create_event_name(CallbackType.VALUE)
    
        if event_name not in self._callbacks:
            self.logger.warning(f"No callbacks registered for {event_name}")
            return

        current_value = self._get_current_value(CallbackType.VALUE)
        callback_info = self._callbacks[event_name]
        
        if current_value is None:
            self.logger.warning(f"Failed to get current value for {self.item_id}")
            return

        if self._should_trigger_callback(
            current_value, 
            self._prev_values[CallbackType.VALUE], 
            callback_info
        ):
            Event_manager.trigger_custom_event(
                f"{self.item_id}_value_change",
                current_value
            )
            
            self._prev_values[CallbackType.VALUE] = current_value


    def _check_state_changes(self) -> None:
        """Проверяет изменения состояний элемента."""
        for state in list(self._prev_values[CallbackType.STATE].keys()):
            event_name = self._create_event_name(CallbackType.STATE, state)
            
            if event_name not in self._callbacks:
                self.logger.warning(f"No callbacks registered for {event_name}")
                return

            current_state = self._get_current_value(CallbackType.STATE, state)
            
            if current_state is None:
                self.logger.warning(f"Failed to get current state for {self.item_id}")
                return

            callback_info = self._callbacks[event_name]
            
            if self._should_trigger_callback(
                current_state, 
                self._prev_values[CallbackType.STATE][state], 
                callback_info
            ):            
                for state in list(self._prev_values[CallbackType.STATE].keys()):
                    Event_manager.trigger_custom_event(
                    f"{self.item_id}_state_{state}_change",
                    state,
                    current_state
                    )
                
                self._prev_values[CallbackType.STATE][state] = current_state