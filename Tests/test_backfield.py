import unittest
from dataclasses import dataclass

from Src.Utils import Backfield



class test_backfield(unittest.TestCase):

    def test_Backfield(self):

        @dataclass
        class A:
            flag = False
            b = Backfield(0)

        a = A()
        A.b.bind(a, lambda _: setattr(A, 'flag', True))
        a.b = 1

        assert a.flag == True


    def test_Backfield_value_stored(self):
        # После присвоения значение должно сохраниться и читаться обратно

        @dataclass
        class A:
            b = Backfield(0)

        a = A()
        A.b.bind(a, lambda _: None)
        a.b = 99

        assert a.b == 99


    def test_Backfield_callback_receives_new_value(self):
        # Callback должен получать именно то значение, которое было присвоено

        @dataclass
        class A:
            b = Backfield(0)

        received = []
        a = A()
        A.b.bind(a, lambda val: received.append(val))

        a.b = 1
        a.b = 2

        assert received == [1, 2]