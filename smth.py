class Smth:
    def __class_getitem__(cls, items):
        if not isinstance(items, tuple):
            items = (items,)
        return Smth(shape = items)
    
    def __init__(self, shape: tuple):
        self.shape = shape

    def smth(self):
        print(self.shape)


Smth[int, str].smth()
Smth[bool].smth()
