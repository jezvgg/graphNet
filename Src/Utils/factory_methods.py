from typing import Hashable, Callable, Sequence



class FactoryMethods:

    @staticmethod
    def build(map: dict[Hashable, Callable], value: Hashable, *args, **kwargs):
        if value not in map:
            return print("BIG BIG BIG BIG ERROR")
        
        func = map[value]
        annotations = func.__annotations__ | getattr(getattr(func, '__wrapped__', None), '__annotations__', {})
        union_annotations = dict([(key, kwargs[key]) for key in kwargs if key in annotations])

        if union_annotations.keys() != kwargs.keys():
            print("INFO")

        return func(*args, **union_annotations)
    

    @staticmethod
    def mapping(map: dict[Hashable, Callable], value: Hashable | Sequence[Hashable], action: Callable):
        if not isinstance(value, Sequence): value = [value]

        for hint in value:
            map[hint] = action