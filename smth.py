class A:
    _smth: int

    def __init__(self):
        self._smth = 5

    @property
    def smth(self):
        return self._smth
    


print(A.smth)
obj = A()
print(A.smth.__get__(obj))