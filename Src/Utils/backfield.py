from typing import Callable, Any



class Backfield:
    owner: str
    name: str
    callback: Callable


    def __init__(self, value = None, callback: Callable = lambda x:x):
        self.callback = callback
        self = value


    def __set_name__(self, owner, name):
        self.owner = owner
        self.name = f"_{name}"

    
    def __get__(self, instance, owner: type = None) -> Any:
        if not instance: return self
        return getattr(instance, self.name)
    

    def __set__(self, instance, value) -> None:
        self.callback(value)
        setattr(instance, self.name, value)