import dearpygui.dearpygui as dpg


def get_children(item: str | int, depth: int = None, slot: int = 1) -> set[int | str]:

    children = dpg.get_item_children(item, slot=slot)
    iterator = iter(children)
    child = None

    while child != children[-1]:
        child = next(iterator)
        children += dpg.get_item_children(child, slot=slot)

    return set(children)


