class A:
    pass

class B(A):
    pass

class C(B):
    pass

print(A.__subclasses__())