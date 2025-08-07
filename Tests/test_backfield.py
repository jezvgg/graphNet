import unittest
from dataclasses import dataclass

from Src.Utils import Backfield



class test_backfield(unittest.TestCase):

    def test_Backfield(self):
        
        @dataclass
        class A:
            flag = False
            b = Backfield(0, callback=lambda _: setattr(A, 'flag', True))


        a = A()
        a.b = 1

        assert a.flag == True