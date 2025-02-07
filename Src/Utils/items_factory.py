from abc import ABC
from typing import Hashable, Callable, Sequence

# from Src.Logging import Logger_factory
from Src.Utils import FactoryMethods

# TODO Добавить логгирование когда его починю

class ItemsFactory(ABC):
    __map: dict[Hashable, Callable]


    def __init__(self): self.__map = {}


    def build(self, value: Hashable, *args, **kwargs):
        return FactoryMethods.build(self.__map, value, *args, **kwargs)

    
    def mapping(self, value: Hashable | Sequence[Hashable], action: Callable):
        return FactoryMethods.mapping(self.__map, value, action)


    @property
    def map(self):
        return self.__map
