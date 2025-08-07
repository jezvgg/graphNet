import dearpygui.dearpygui as dpg




class SizeManager:
    """
    Универсальный менеджер размеров и шрифтов для Dear PyGui.
    Управляет глобальным масштабом приложения и размерами шрифтов для объектов.
    """


    def __init__(self,
                 font_limits: list[int],
                 initial_object_font_size: int,
                 initial_global_scale: float = 1.0,
                 global_scale_limits: list[float] = [0.5, 2.0],
                 scale_step: float = 0.1):
        """
        Инициализация менеджера размеров и шрифтов.

        Args:
            font_limits (list[int]): Границы [min, max] для размеров шрифтов объектов.
            initial_object_font_size (int): Начальный размер шрифта для объектов.
            initial_global_scale (float): Начальный глобальный масштаб приложения.
            global_scale_limits (list[float], optional): Границы [min, max] для глобального масштаба.
            scale_step (float): Шаг изменения масштаба.
        """
        self.default_font: str | int = None
        self.font_limits = font_limits
        self.global_scale_limits = global_scale_limits
        self.scale_step = scale_step

        self.current_object_font_size = self._clamp_value(initial_object_font_size, self.font_limits)
        self.current_global_scale = self._clamp_value(initial_global_scale, self.global_scale_limits)


    def resize_scale(self, size_delta: float, target: str | int = None):
        """
        Универсальный метод изменения масштаба.

        Args:
            size_delta (float): Дельта изменения размера (положительная/отрицательная).
            target (str | int, optional): ID контейнера для изменения шрифтов объектов.
                                        Если None - изменяется глобальный масштаб.
        """
        if target is None:
            self._resize_global_scale(size_delta)
        else:
            self._resize_objects_font(target, size_delta)


    def load_fonts(self, font_configs: list[dict]) -> None:
        """
        Загружает шрифты в Dear PyGui на основе конфигураций.
        Должен вызываться внутри контекста dpg.font_registry().

        Args:
            font_configs (list[dict]): Список конфигураций шрифтов.
                Каждая конфигурация содержит:
                - "path": str (путь к файлу шрифта)
                - "size": int (размер шрифта)
                - "dpg_tag": str (уникальный тег для DearPyGui)
                - "make_default": bool (optional, сделать шрифтом по умолчанию)
        """

        for config in font_configs:
            font_id = self._load_single_font(config)

            if config.get("make_default") and self.default_font is None:
                self.default_font = font_id
                if dpg.does_item_exist(self.default_font):
                    dpg.bind_font(self.default_font)


    def _clamp_value(self, value: float, limits: list[float]) -> float:
        """Ограничивает значение в заданных пределах."""
        return max(limits[0], min(limits[1], value))


    def _load_single_font(self, config: dict) -> int:
        """Загружает один шрифт и возвращает его ID."""
        with dpg.font(config["path"], config["size"], tag=config["dpg_tag"]) as font_id:
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic, parent=font_id)
        return font_id


    def _resize_global_scale(self, size_delta: float):
        """Изменяет глобальный масштаб приложения."""
        self.current_global_scale += size_delta * self.scale_step
        self.current_global_scale = self._clamp_value(self.current_global_scale, self.global_scale_limits)
        dpg.set_global_font_scale(self.current_global_scale)


    def _resize_objects_font(self, container_id: str | int, size_delta: float):
        """Изменяет размер шрифта всех объектов в контейнере."""
        self.current_object_font_size += int(size_delta)
        self.current_object_font_size = self._clamp_value(self.current_object_font_size, self.font_limits)

        font_tag = f'font_{int(self.current_object_font_size)}'
        for item in dpg.get_item_children(container_id, 1):
            dpg.bind_item_font(item, font_tag)


    @property
    def object_font(self) -> str:
        """Возвращает тег текущего шрифта для объектов."""
        return f'font_{self.current_object_font_size}'