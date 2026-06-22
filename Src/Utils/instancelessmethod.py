from functools import wraps


class instancelessmethod:
    """
    Декоратор для вызова методов класса, который передаёт в self значения в зависимости от типа вызова.
    Он делает метод способным к вызову как из класса, так и из объекта.
    Если вызывают из класса, то self является самим классом, а если из объекта, то self является объектом.
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        @wraps(self.func)
        def wrapper(*args, **kwargs):
            return self.func(instance or owner, *args, **kwargs)

        return wrapper
