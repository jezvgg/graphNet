# from functools import update_wrapper, wraps


# def his_func(a1: str, b2: int, c3: list):
#     pass


# @wraps(his_func, assigned=())
# def my_func(hint: tuple, *args, **kwargs):
#     print(args, kwargs, hint)


# print(my_func.__name__)
# print(my_func.__annotations__)
# print(my_func.__wrapped__.__annotations__)

# my_func(a1='1',b2=3, c3=[], hint=(1,2,3))

# dict1 = {'a': 1, 'b': 2}
# dict2 = {'a': 3, 'b': 4}

# print(dict1.keys() == dict2.keys())


class A:
    def __init__(self):
        self.__a = 1


    def func_a(self, A):
        print(self.__a)


class B:
    def __init__(self):
        self.__a = 1

    
    def func_B(self, a):
        A.func_a(self, a)


class C(A,B):
    def __init__(self):
        A.__init__(self)
        B.__init__(self)


c = C()
print(c.__dict__)