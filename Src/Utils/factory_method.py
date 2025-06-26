from functools import wraps, update_wrapper
from typing import Callable, Hashable, Iterable
from collections import defaultdict



# TODO: Сделать более стабильно работащим
class factorymethod:
    '''
    Декоратор - диспатчеризатор для реализации фабрик
    '''
    default_func: Callable
    registry: dict[Hashable, Callable]


    def __init__(self, default_func: Callable):
        self.default_func = staticmethod(default_func)
        self.registry = defaultdict(lambda: self.default_func)
        update_wrapper(self, self.default_func)


    def __call__(self, *args, **kwargs):
        return self.registry[args[0]](*args, **kwargs)


    def register(self, arguments: Iterable[Hashable] | Hashable):
        if not isinstance(arguments, Iterable): arguments = [arguments]
        
        def decorator(func: Callable):

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            for argument in arguments:
                self.registry[argument] = func

            return wrapper
        return decorator