from dataclasses import dataclass, field
from typing import Any

import dearpygui.dearpygui as dpg
import matplotlib
import numpy as np

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from Src.Config.Annotations.annotation import Annotation


@dataclass
class AFigure(Annotation):
    display: bool = True
    single: bool = field(default=True, init=False)
    node_type: type = field(default=object, init=False)

    @staticmethod
    def static_build(parent: int | str, display: bool = True, *args: Any, **kwargs: Any) -> int | str: 
        new_parent: int | str = dpg.get_item_parent(parent)
        attr_config: dict[str, Any] = dpg.get_item_configuration(parent)
        dpg.delete_item(parent)

        kwargs = Annotation.check_kwargs(dpg.node_attribute, kwargs)
        kwargs['parent'] = new_parent
        kwargs['user_data'] = []
        attr_type: int = attr_config.get('attribute_type', dpg.mvNode_Attr_Input)
        kwargs['attribute_type'] = dpg.mvNode_Attr_Input if attr_type == dpg.mvNode_Attr_Static else attr_type
        
        with dpg.node_attribute(*args, **kwargs):
            if not dpg.does_alias_exist("figure_texture_registry"):
                dpg.add_texture_registry(tag="figure_texture_registry")

            tex_id: int | str = dpg.generate_uuid()
            dpg.add_dynamic_texture(
                width=400, height=300, 
                default_value=np.full((300, 400, 4), 0.5, dtype=np.float32).flatten(), 
                tag=tex_id, parent="figure_texture_registry"
            )
            
            dpg.add_text(kwargs.get('label') or "Figure", show=not display)
            return dpg.add_image(tex_id, user_data=tex_id, show=display)

    def build(self, parent: int | str, *args: Any, **kwargs: Any) -> int | str:
        return self.static_build(parent, self.display, *args, **kwargs)

    @staticmethod
    def static_get(input_id: int | str) -> Any:
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

    def get(self, input_id: int | str) -> Any:
        return self.static_get(input_id)

    @staticmethod 
    def static_set(input_id: int | str, fig: plt.Figure, display: bool = True) -> bool:
        if not display:
            return True

        canvas: FigureCanvas = FigureCanvas(fig)
        canvas.draw()
        
        w, h = canvas.get_width_height()
        tex_data = np.frombuffer(canvas.buffer_rgba(), dtype=np.uint8).astype(np.float32) / 255.0

        tex_id: int | str = dpg.get_item_user_data(input_id)
        
        dpg.configure_item(tex_id, width=w, height=h)
        dpg.set_value(tex_id, tex_data)
        
        plt.close(fig) 
        return True

    def set(self, input_id: int | str, fig: plt.Figure) -> bool:
        return self.static_set(input_id, fig, self.display)
    

    def serialize(self, input_id: int | str):
        return None 
    

    def deserialize(self, input_id: int | str, value) -> bool:
        return True
