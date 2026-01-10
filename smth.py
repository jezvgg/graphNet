

class Base:
    flag = False


    def __init__(self, flag = None):
        if flag is not None: Base.flag = flag
        if not Base.flag: print('Flag is down!')
        else: print('Flag is UP!')



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


class A:
    smth = lateinit(Base)


# print(A.smth)
print(Base.flag)
# Base(True)
a = A()
print(a.smth)
print(a.smth)