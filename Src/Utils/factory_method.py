from functools import wraps, update_wrapper, partial
from typing import Callable, Hashable, Iterable
from collections import defaultdict



class factorymethod:
    '''
    Декоратор - диспатчеризатор по значению первого аргумента метода
    '''
    default_func: Callable
    registry: dict[Hashable, Callable]


    def __init__(self, default_func: Callable):
        self.default_func = default_func
        self.registry = defaultdict(lambda: self.default_func)
        update_wrapper(self, self.default_func)


    def __call__(self, *args, **kwargs):
        return self.registry[args[1]](*args, **kwargs)


    def __get__(self, instance, owner):
        if instance is None: return self

        bound_call = partial(self.__call__, instance)
        update_wrapper(bound_call, self.default_func)
        bound_call.register = self.register
        return bound_call


    def register(self, arguments: Iterable[Hashable] | Hashable):
        if not isinstance(arguments, Iterable): arguments = [arguments]

        def decorator(func: Callable):

            for argument in arguments:
                self.registry[argument] = func

            return func
        return decorator
