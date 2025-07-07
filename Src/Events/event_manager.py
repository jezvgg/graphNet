import dearpygui.dearpygui as dpg


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

    # Карта событий для ItemHandlerRegistry
    _HANDLER_EVENT_MAP = {
        "click": dpg.add_item_clicked_handler,
        "double_click": dpg.add_item_double_clicked_handler,
        "hover": dpg.add_item_hover_handler,
        "focus": dpg.add_item_focus_handler,
        "visible": dpg.add_item_visible_handler,
        "activated": dpg.add_item_activated_handler,
        "deactivated": dpg.add_item_deactivated_handler,
        "edited": dpg.add_item_edited_handler,
    }

    @classmethod
    def add(cls, event_type, item_id, handler, *, user_data=None):
        """
        Регистрирует обработчик на событие для указанного элемента DPG.

        Для 'value_changed' используется основной callback элемента (перезаписывает предыдущий).
        Для остальных событий можно регистрировать несколько обработчиков.

        Args:
            event_type (str): Тип события ('value_changed', 'click', 'hover' и т.д.).
            item_id (int or str): ID элемента DPG.
            handler (callable): Функция-обработчик (sender, app_data, user_data).
            user_data (any, optional): Пользовательские данные для передачи в обработчик.
        """
        if not dpg.does_item_exist(item_id):
            if cls._logger:
                cls._logger.warning(f"Элемент {item_id} не существует. Регистрация '{event_type}' прервана.")
            return

        # 'value_changed' - это особый случай, он использует основной callback
        if event_type == "value_changed":
            dpg.configure_item(item_id, callback=handler, user_data=user_data)
            if cls._logger:
                cls._logger.info(f"Обработчик 'value_changed' установлен для элемента {item_id}.")
            return

        if event_type not in cls._HANDLER_EVENT_MAP:
            if cls._logger:
                cls._logger.error(f"Неизвестный тип события: '{event_type}'. "
                                  f"Поддерживаемые типы: 'value_changed', {', '.join(cls._HANDLER_EVENT_MAP.keys())}.")
            return

        registry_id = dpg.get_item_info(item_id).get("handlers")
        if not registry_id:
            registry_id = dpg.add_item_handler_registry()
            dpg.bind_item_handler_registry(item_id, registry_id)
            if cls._logger:
                cls._logger.debug(f"Создан новый ItemHandlerRegistry ({registry_id}) для элемента {item_id}.")

        add_handler_func = cls._HANDLER_EVENT_MAP[event_type]
        add_handler_func(parent=registry_id, callback=handler, user_data=user_data)

        if cls._logger:
            cls._logger.info(f"Обработчик для '{event_type}' успешно добавлен к элементу {item_id}.")

    @classmethod
    def clear(cls, item_id):
        """
        Удаляет все обработчики, привязанные к элементу,
        включая основной callback и все из ItemHandlerRegistry.

        Args:
            item_id (int or str): ID элемента DPG.
        """
        if not dpg.does_item_exist(item_id):
            if cls._logger:
                cls._logger.warning(f"Попытка очистить обработчики для несуществующего элемента {item_id}.")
            return

        # Сбрасываем основной callback (для 'value_changed')
        dpg.configure_item(item_id, callback=None, user_data=None)

        registry_id = dpg.get_item_info(item_id).get("handlers")
        if registry_id:
            dpg.delete_item(registry_id)

        if cls._logger:
            cls._logger.info(f"Все обработчики для элемента {item_id} были очищены.")