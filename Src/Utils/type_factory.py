from typing import Callable, Hashable
from abc import ABC

from Src.Utils import FactoryMethods



class TypesFactory(ABC):
    __map: dict[type, Callable]


    def __init__(self): self.__map = {}


    def build_type(self, value: Hashable, *args, **kwargs):
        return FactoryMethods.build(self.__map, value, *args, **kwargs)


    def build_by_type(self, value: object, *args, **kwargs):
        return self.build_type(type(value), *args, **kwargs)
    

    def mapping_type(self, value: type, action: Callable):
        return FactoryMethods.mapping(self.__map, value, action)


    def mapping_subclasses(self, value: type, action: Callable):
        for subclass in value.__subclasses__():
            self.mapping_subclasses(subclass, action)
        self.mapping_type(value, action)
    

    @property
    def type_map(self):
        return self.__map
