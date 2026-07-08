
class lateinit:

    def __init__(self, method, *args, **kwargs):
        self.__value = method
        self.__args = args
        self.__kwargs = kwargs


    def __set_name__(self, owner, name):
        self.owner = owner
        self.name = name


    def __get__(self, instance, owner: type = None):
        value = self.__value(*self.__args, **self.__kwargs)
        setattr(instance, self.name, value)
        return value
