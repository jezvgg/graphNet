from pathlib import Path
from typing import Any

from Src.Config.Annotations import AFile, AEnum, ASequence


class ProjectDecoder:
    """
    Класс, инкапсулирующий логику десериализации сохраненного состояния проекта
    обратно в объекты Python. Симметричен ProjectEncoder.
    """

    DESERIALIZERS: dict = {
        AFile:     lambda hint, val: [Path(p) for p in val],
        AEnum:     lambda hint, val: next((m for m in hint.source if m.value == val), None),
        ASequence: lambda hint, val: tuple(val),
    }

    @classmethod
    def deserialize_value(cls, hint: Any, value: Any) -> Any:
        """
        Преобразует JSON-совместимое значение обратно в исходный тип Python
        на основе словаря-диспетчера DESERIALIZERS.
        """
        if value is None:
            return None

        hint_cls = hint if isinstance(hint, type) else type(hint)

        if handler := cls.DESERIALIZERS.get(hint_cls):
            return handler(hint, value)

        return value
