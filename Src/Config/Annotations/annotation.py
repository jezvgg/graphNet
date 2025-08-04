from abc import ABC, abstractmethod
from typing import Callable



class Annotation(ABC):
    BASE_WIDTH = 256
    field_id: str | int


    @classmethod
    def check_kwargs(cls, func: Callable, kwargs: dict):
        annotations = func.__annotations__ | getattr(getattr(func, '__wrapped__', None), '__annotations__', {})
        union_annotations = dict([(key, kwargs[key]) for key in kwargs if key in annotations])
        return union_annotations
    

    @staticmethod
    @abstractmethod
    def build(*args, **kwargs) -> str | int: pass


    @staticmethod
    @abstractmethod
    def get(input_id: str| int): pass


    @staticmethod
    @abstractmethod
    def set(input_id: str| int, value) -> bool: pass
    