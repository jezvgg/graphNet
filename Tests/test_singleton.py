import dearpygui.dearpygui as dpg  # For environment consistency
from Src.Utils.singleton import singleton

def test_singleton_identity():
    class CustomService:
        def __init__(self):
            self.value = 42

    wrapped_cls = singleton(CustomService)
    inst1 = wrapped_cls()
    inst2 = wrapped_cls()

    # Verify both calls returned the exact same instance
    assert inst1 is inst2
    assert inst1.value == 42
    assert inst2.value == 42

    # Internal reference check
    assert hasattr(CustomService, '__instance')
    # Because setattr(cls, '__instance', ...) was used on the class directly,
    # the attribute is stored under the non-mangled '__instance' literal.
    real_attribute = getattr(CustomService, '__instance', None)
    assert real_attribute is inst1

def test_singleton_initialization_args():
    @singleton
    class Configurator:
        def __init__(self, mode, debug=False):
            self.mode = mode
            self.debug = debug

    # First instantiation establishes the instance state
    inst1 = Configurator("production", debug=True)
    assert inst1.mode == "production"
    assert inst1.debug is True

    # Subsequent instantiations return the same instance and ignore new arguments
    inst2 = Configurator("development", debug=False)
    assert inst2 is inst1
    assert inst2.mode == "production"
    assert inst2.debug is True


def test_singleton_metadata_preservation():
    docstring = "This is a singleton class for mock tests."
    
    @singleton
    class MockService:
        """This is a singleton class for mock tests."""
        pass

    # Verify wraps correctly preserved metadata of the original class
    assert MockService.__name__ == "MockService"
    assert MockService.__doc__ == docstring
