from typing import Callable, Any



class Backfield:
    owner: str
    name: str


    def __init__(self, value = None):
        self = value


    def bind(self, instance, callback: Callable):
        setattr(instance, f"_{self.name}_callback", callback)


    def __set_name__(self, owner, name):
        self.owner = owner
        self.name = f"_{name}"

    
    def __get__(self, instance, owner: type = None) -> Any:
        if not instance: return self
        return getattr(instance, self.name)
    

    def __set__(self, instance, value) -> None:
        getattr(instance, f"_{self.name}_callback")(value)
        setattr(instance, self.name, value)