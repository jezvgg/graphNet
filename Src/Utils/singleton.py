from functools import wraps


def singleton(cls):
    
    @wraps(cls)
    def wrapper(*args, **kwargs):
        if not hasattr(cls, '__instance'):
            setattr(cls, '__instance', cls(*args, **kwargs))
        return getattr(cls, '__instance')

    return wrapper