from dataclasses import dataclass
from Src.Utils import Backfield

def test_Backfield():
    @dataclass
    class A:
        flag = False
        b = Backfield(0)

    a = A()
    A.b.bind(a, lambda _: setattr(A, 'flag', True))
    a.b = 1
    assert a.flag is True

def test_Backfield_value_stored():
    @dataclass
    class A:
        b = Backfield(0)

    a = A()
    A.b.bind(a, lambda _: None)
    a.b = 99
    assert a.b == 99

def test_Backfield_callback_receives_new_value():
    @dataclass
    class A:
        b = Backfield(0)

    received = []
    a = A()
    A.b.bind(a, lambda val: received.append(val))
    a.b = 1
    a.b = 2
    assert received == [1, 2]
