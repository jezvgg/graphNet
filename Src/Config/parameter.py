from dataclasses import dataclass
from typing import Union

from Src.Enums.attr_type import AttrType


AUTODEFAULT = 0


@dataclass
class Parameter:
    attr_type: AttrType
    hint: Union['type',tuple['type']]
    default: object = None


    def build(self, *args, **kwargs):
        # ! Ебучие циклически импорты, питон заебал с ними
        from Src.Utils import AttributesFactory
        return AttributesFactory.build(self.attr_type, self.hint, *args, **kwargs)
    

    def get_value(self, argument: int):
        # ! Ебучие циклически импорты, питон заебал с ними
        from Src.Utils import GetterFactory
        value = GetterFactory.get_value(self.hint, argument)
        print(value)
        return value

