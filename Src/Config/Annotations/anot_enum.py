import enum

import dearpygui.dearpygui as dpg

from Src.Config.Annotations.annotation import Annotation


class AEnum(Annotation):
    """
    Аннотация для создания выпадающего списка (dpg.add_combo).
    Используется для полей с предопределенным набором строковых значений.
    """

    def __init__(self, source: list[str] | type):
        """
        Args:
            source (list[str] | type): Источник данных. Может быть списком строк
                                        или классом, унаследованным от enum.Enum.
        """
        if isinstance(source, type):
            self.items = [e.value for e in source]
            return

        self.items = source

    def build(self, *args, **kwargs):
        """
        Создает dpg.add_combo с предопределенными элементами.
        """
        kwargs = Annotation.check_kwargs(dpg.add_combo, kwargs)

        kwargs['items'] = self.items
        kwargs['default_value'] = self.items[0]

        return dpg.add_combo(*args, **kwargs)

    @staticmethod
    def get(input_id: int | str):
        """
        Получает текущее выбранное значение из dpg.add_combo.
        """
        return dpg.get_value(input_id)

    @staticmethod
    def set(input_id: str | int, value: str) -> bool:
        """
        Устанавливает значение для dpg.add_combo.
        """
        if not isinstance(value, str):
            return False

        dpg.set_value(input_id, value)
        return True