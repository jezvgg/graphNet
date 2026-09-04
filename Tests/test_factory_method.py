import dearpygui.dearpygui as dpg  # Environment consistency
from Src.Utils.factory_method import factorymethod

def test_factory_method_basic_dispatch():
    class Actions:
        @factorymethod
        def do_action(self, action_type, *args, **kwargs):
            return f"default:{action_type}"

        # Registering using an iterable of keys
        @do_action.register(["run", "walk"])
        def _move_action(self, action_type, speed=10):
            return f"moving:{action_type}:{speed}"

    actions_inst = Actions()

    # Test registered methods
    assert actions_inst.do_action("run", speed=20) == "moving:run:20"
    assert actions_inst.do_action("walk") == "moving:walk:10"

    # Test default fallback path
    assert actions_inst.do_action("jump") == "default:jump"


def test_factory_method_non_iterable_keys():
    # Enums or custom hashable non-iterable objects
    class CustomKey:
        def __init__(self, val):
            self.val = val
        def __hash__(self):
            return hash(self.val)
        def __eq__(self, other):
            return isinstance(other, CustomKey) and self.val == other.val

    key_a = CustomKey("A")
    key_b = CustomKey("B")

    class Service:
        @factorymethod
        def process(self, key, data):
            return f"fallback:{data}"

        @process.register(key_a)
        def _prod_a(self, key, data):
            return f"A:{data}"

    inst = Service()

    # Test registered non-iterable key
    assert inst.process(key_a, "hello") == "A:hello"

    # Test fallback path
    assert inst.process(key_b, "world") == "fallback:world"


def test_factory_method_metadata():
    docstring = "Process files based on type."

    @factorymethod
    def process_file(instance, file_type):
        """Process files based on type."""
        return "default"

    # Check update_wrapper preserves doc and name
    assert process_file.__name__ == "process_file"
    assert process_file.__doc__ == docstring


def test_factory_method_class_lookup():
    class Worker:
        @factorymethod
        def work(self, task):
            return "default"

    # Accessing descriptor via the class directly (instance=None)
    descriptor = Worker.work
    assert isinstance(descriptor, factorymethod)
    assert descriptor.default_func.__name__ == "work"
