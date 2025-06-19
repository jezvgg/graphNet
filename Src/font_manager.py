import dearpygui.dearpygui as dpg


class FontManager:
    """Менеджер шрифтов для Dear PyGui приложения"""


    def __init__(self):
        """Инициализация менеджера шрифтов"""
        
        self.app_fonts_config: dict[str, dict[str, any]] = {}  # Конфигурация шрифтов приложения
        self.node_config: dict[str, any] | None = None  # конфигурация шрифтов нодов
        self.loaded_fonts: dict[str, int] = {}  # все загруженные шрифты
        self.default_font: int | None = None  # тег дефолтного шрифта


    def configure_app_font(self, user_tag: str, font_path: str, size: int, make_default: bool = False) -> None:
        """
        Добавляет конфигурацию шрифта приложения

        Args:
            user_tag: пользовательский тег для идентификации шрифта
            font_path: путь к файлу шрифта
            size: размер шрифта
            make_default: сделать ли этот шрифт дефолтным
        """

        self.app_fonts_config[user_tag] = {
            "path": font_path,
            "size": size,
            "make_default": make_default
        }


    def configure_node_fonts(self, font_path: str, base_size: int, sizes: list[int],
                             tag_prefix: str = "NodeFont") -> None:
        """
        Настраивает серию шрифтов для узлов редактора

        Args:
            font_path: путь к файлу шрифта
            base_size: базовый размер шрифта
            sizes: список размеров для загрузки
            tag_prefix: префикс для тегов шрифтов узлов
        """

        valid_sizes = sorted(set(sizes))
        if not valid_sizes:
            self.node_config = None
            return

        self.node_config = {
            "path": font_path,
            "base_size": base_size,
            "sizes": valid_sizes,
            "prefix": tag_prefix
        }


    def load_fonts(self) -> None:
        """
        Загружает все настроенные шрифты в Dear PyGui

        Функция должна вызываться после загрузки всех конфигов в конструкции dearpygui.font_registry()
        """

        for user_tag, config in self.app_fonts_config.items():
            with dpg.font(config["path"], config["size"], tag=user_tag) as font_tag:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic, parent=font_tag)

            self.loaded_fonts[user_tag] = font_tag
            if config["make_default"]:
                self.default_font = font_tag
                dpg.bind_font(self.default_font)

        if self.node_config:
            for size in self.node_config["sizes"]:
                tag = f"{self.node_config['prefix']}_{size}"
                with dpg.font(self.node_config["path"], size, tag=tag) as font_tag:
                    dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic, parent=font_tag)
                self.loaded_fonts[f"node_{size}"] = font_tag


    def get_font_by_tag(self, user_tag: str) -> int | None:
        """
        Возвращает тег шрифта приложения по пользовательскому тегу

        Args:
            user_tag: пользовательский тег шрифта

        Returns:
            тег шрифта DPG или None
        """

        font = self.loaded_fonts.get(user_tag)

        if dpg.does_item_exist(font):
            return font

        return self.default_font


    def get_node_font_by_size(self, size: int) -> int | None:
        """
        Возвращает тег шрифта узла по размеру

        Args:
            size: размер шрифта

        Returns:
            тег шрифта DPG или None
        """

        font = self.loaded_fonts.get(f"node_{size}")

        if dpg.does_item_exist(font):
            return font

        return self.default_font


    def clear(self) -> None:
        """Очищает все шрифты и конфигурации"""

        for font_tag in self.loaded_fonts.values():
            if font_tag and dpg.does_item_exist(font_tag):
                dpg.delete_item(font_tag)

        self.loaded_fonts.clear()
        self.app_fonts_config.clear()
        self.node_config = None
        self.default_font = None