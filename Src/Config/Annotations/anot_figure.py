from dataclasses import dataclass, field
from gettext import install
from typing import Any

import dearpygui.dearpygui as dpg
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from Src.Config.Annotations import AParam
from Src.Enums import DPGType
from Src.Utils.instancelessmethod import instancelessmethod


@dataclass
class AFigure(AParam):
    display: bool = True
    single: bool = field(default=True, init=False)
    node_type: type = field(default=object, init=False)

    def _build(self, *args: Any, **kwargs: Any) -> int | str:
        if not dpg.does_alias_exist("figure_texture_registry"):
            dpg.add_texture_registry(tag="figure_texture_registry")

        tex_id: int | str = dpg.generate_uuid()
        dpg.add_dynamic_texture(
            width=400,
            height=300,
            default_value=np.full((300, 400, 4), 0.5, dtype=np.float32).flatten(),
            tag=tex_id,
            parent="figure_texture_registry",
        )

        dpg.add_text(kwargs.get("label") or "Figure", show=not self.display)
        return dpg.add_image(tex_id, user_data=tex_id, show=self.display)


    @staticmethod
    def get(input_id: int | str) -> Any:
        parent: int | str = dpg.get_item_parent(input_id)
        user_data: list[int | str] | None = dpg.get_item_user_data(parent)

        if not user_data:
            return None

        results: list[Any] = []
        for attribute in user_data:
            label: str = dpg.get_item_label(attribute)
            node: Any = dpg.get_item_user_data(dpg.get_item_parent(attribute))
            results.append(getattr(node, label))

        return results[0] if results else None


    @instancelessmethod
    def set(self, input_id: int | str, fig: plt.Figure) -> bool:
        if not self.display:
            return True

        canvas: FigureCanvas = FigureCanvas(fig)
        canvas.draw()

        w, h = canvas.get_width_height()
        tex_data = (
            np.frombuffer(canvas.buffer_rgba(), dtype=np.uint8).astype(np.float32)
            / 255.0
        )

        tex_id: int | str = dpg.get_item_user_data(input_id)

        dpg.configure_item(tex_id, width=w, height=h)
        dpg.set_value(tex_id, tex_data)

        plt.close(fig)
        return True
