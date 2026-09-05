from collections import deque

import dearpygui.dearpygui as dpg


def get_children(item: str | int, depth: int = None, slot: int = 1) -> set[int | str]:

    children = dpg.get_item_children(item, slot=slot)
    result = set()
    if not children: return result

    queue = deque((child, 1) for child in children)

    while queue:
        current_item, current_depth = queue.popleft()
        if depth and current_depth > depth: break

        result.add(current_item)

        queue.extend(
            (child, current_depth + 1) for child in
            dpg.get_item_children(current_item, slot=slot) or []
            if child not in result
        )

    return result
