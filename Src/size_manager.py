import dearpygui.dearpygui as dpg




class SizeManager:
    """
    Универсальный менеджер размеров и шрифтов для Dear PyGui.
    Управляет глобальным масштабом приложения и размерами шрифтов для узлов.
    """

    default_font: str | int | None = None  # DPG шрифт по умолчанию для приложения
    font_limits: list[int]  # [min_size, max_size] для шрифтов узлов
    current_objects_font_size: int  # Текущий размер шрифта для новых узлов

    current_global_scale: float  # Текущий глобальный масштаб приложения
    global_scale_limits: list[float]  # [min_scale, max_scale] для глобального масштаба
    global_scale_step: float = 0.1  # Шаг изменения глобального масштаба


    def __init__(self,
                 font_limits: list[int],
                 initial_node_font_size: int,
                 initial_global_scale: float = 1.0,
                 global_scale_limits: list[float] = None):
        """
        Инициализация менеджера размеров и шрифтов.

        Args:
            font_limits (list[int]): Границы [min, max] для размеров шрифтов узлов.
            initial_node_font_size (int): Начальный размер шрифта для узлов.
            initial_global_scale (float, optional): Начальный глобальный масштаб приложения. По умолчанию 1.0.
            global_scale_limits (list[float], optional): Границы [min, max] для глобального масштаба.
        """
        self.font_limits = font_limits
        self.global_scale_limits = global_scale_limits

        self.current_objects_font_size = self._clamp_value(
            initial_node_font_size, self.font_limits
        )
        self.current_global_scale = self._clamp_value(
            initial_global_scale, self.global_scale_limits
        )


    def _clamp_value(self, value: float, limits: list[float]) -> float:
        """Ограничивает значение в заданных пределах"""
        return max(limits[0], min(limits[1], value))


    def resize_global(self, size_delta: float):
        """Изменение глобального масштаба приложения"""
        self.current_global_scale += size_delta * self.global_scale_step
        self.current_global_scale = self._clamp_value(self.current_global_scale, self.global_scale_limits)
        dpg.set_global_font_scale(self.current_global_scale)


    def resize_node_editor(self, node_editor: int | str, size_delta: float):
        """Изменение размера всех нодов в редакторе"""
        self.current_objects_font_size += size_delta
        self.current_objects_font_size = self._clamp_value(self.current_objects_font_size, self.font_limits)
        for item in dpg.get_item_children(node_editor, 1):
            dpg.bind_item_font(item, f'font_{int(self.current_objects_font_size)}')


    def load_fonts(self, font_configs: list[dict[str, any]]) -> None:
        """
        Загружает шрифты в Dear PyGui на основе предоставленного списка конфигураций.
        Этот метод должен вызываться внутри контекста dpg.font_registry().

        Args:
            font_configs: Список конфигураций шрифтов.
                          Каждая конфигурация - это словарь с ключами:
                          - "path": str (путь к файлу шрифта)
                          - "size": int (размер шрифта)
                          - "dpg_tag": str (уникальный тег, который будет использоваться в DearPyGui.
                                          Вызывающий код отвечает за его уникальность.)
                          - "make_default": bool (необязательно, сделать ли этот шрифт шрифтом по умолчанию)
        """

        for config in font_configs:
            font_path = config["path"]
            size = config["size"]
            dpg_tag = config["dpg_tag"]
            make_default = config.get("make_default", False)

            with dpg.font(font_path, size, tag=dpg_tag) as font_registry_id:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic, parent=font_registry_id)
            if make_default and self.default_font is None:
                self.default_font = font_registry_id
                if dpg.does_item_exist(self.default_font):
                    dpg.bind_font(self.default_font)


    @property
    def object_font(self):
        return f'font_{self.current_objects_font_size}'