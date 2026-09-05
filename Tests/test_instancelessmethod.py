from dataclasses import dataclass

from Src.Utils.instancelessmethod import instancelessmethod


@dataclass
class DummyInstancelessMethod:
    some_field: int = 5

    @instancelessmethod
    def some_method(self):
        return self.some_field


def test_some_method_with_instance():
    inst = DummyInstancelessMethod(some_field=10)
    result = inst.some_method()
    assert result == 10


def test_some_method_without_instance():
    result = DummyInstancelessMethod.some_method()
    assert result == 5
