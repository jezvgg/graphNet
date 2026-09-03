import dearpygui.dearpygui as dpg  # To be consistent with environment
from Src.Utils.lateinit import lateinit

def test_lateinit_basic_evaluation():
    call_count = 0
    def init_value():
        nonlocal call_count
        call_count += 1
        return "evaluated_value"

    class Demo:
        x = lateinit(init_value)

    # Before evaluation
    demo_inst = Demo()
    assert call_count == 0
    assert "x" not in demo_inst.__dict__

    # First access should evaluate the descriptor
    value = demo_inst.x
    assert value == "evaluated_value"
    assert call_count == 1
    assert "x" in demo_inst.__dict__
    assert demo_inst.__dict__["x"] == "evaluated_value"

    # Second access should return cached value and NOT invoke init_value again
    assert demo_inst.x == "evaluated_value"
    assert call_count == 1


def test_lateinit_independent_per_instance():
    call_count = 0
    def init_value():
        nonlocal call_count
        call_count += 1
        return f"val_{call_count}"

    class Demo:
        x = lateinit(init_value)

    inst1 = Demo()
    inst2 = Demo()

    # Accessing inst1 evaluates it
    val1 = inst1.x
    assert val1 == "val_1"
    assert call_count == 1

    # Accessing inst2 evaluates separately, calling method again
    val2 = inst2.x
    assert val2 == "val_2"
    assert call_count == 2

    # Cached values remain separate
    assert inst1.x == "val_1"
    assert inst2.x == "val_2"
    assert call_count == 2


def test_lateinit_args_and_kwargs():
    def init_with_args(*args, **kwargs):
        return {
            "args": args,
            "kwargs": kwargs
        }

    class Demo:
        data = lateinit(init_with_args, 1, "test", key="value", count=42)

    inst = Demo()
    result = inst.data

    assert result["args"] == (1, "test")
    assert result["kwargs"] == {"key": "value", "count": 42}
