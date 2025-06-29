class Smth:
    def __class_getitem__(cls, items):
        if not isinstance(items, tuple):
            items = (items,)
        cls.items = items
        return cls
    
    @classmethod
    def smth(cls):
        print(cls.items)


Smth[int, str].smth()
Smth[bool].smth()
