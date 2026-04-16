from dataclasses import dataclass
from typing import Any

import dearpygui.dearpygui as dpg
import matplotlib
import numpy as np

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from Src.Config.Annotations.annotation import Annotation
from Src.Config.Annotations.single import Single
from Src.Enums import DPGType




@dataclass
class AFigure(Annotation):
    node_type: type = object
    single: bool = True
    display: bool = True


    @classmethod
    def __class_getitem__(cls: type, item: Any) -> type:
        display: bool = True
        node_type: type = object
        single: bool = True

        if isinstance(item, tuple):
            i: Any
            for i in item:
                if isinstance(i, bool):
                    display = i
                elif isinstance(i, Single):
                    single = True
                    node_type = i.node_type
                elif isinstance(i, type):
                    single = False
                    node_type = i
        else:
            if isinstance(item, bool):
                display = item
            elif isinstance(item, Single):
                single = True
                node_type = item.node_type
            elif isinstance(item, type):
                single = False
                node_type = item

        return type(f"{cls.__name__}Custom", (cls,), {
            'node_type': node_type,
            'single': single,
            'display': display
        })


    @classmethod
    def build(cls: type, parent: int | str, *args: Any, **kwargs: Any) -> int | str: 
        new_parent: int | str = dpg.get_item_parent(parent)
        attr_config: dict[str, Any] = dpg.get_item_configuration(parent)
        dpg.delete_item(parent)

        kwargs = Annotation.check_kwargs(dpg.node_attribute, kwargs)
        kwargs['parent'] = new_parent
        kwargs['user_data'] = []
        attr_type: int = attr_config.get('attribute_type', dpg.mvNode_Attr_Input)
        
        if attr_type == dpg.mvNode_Attr_Static:
            attr_type = dpg.mvNode_Attr_Input
            
        kwargs['attribute_type'] = attr_type
        
        with dpg.node_attribute(*args, **kwargs):
            if cls.display:
                if not dpg.does_alias_exist("figure_texture_registry"):
                    dpg.add_texture_registry(tag="figure_texture_registry")

                tex_id: int | str = dpg.generate_uuid()
                dpg.add_dynamic_texture(
                    width=400, 
                    height=300, 
                    default_value=np.full((300, 400, 4), 0.5, dtype=np.float32).flatten(), 
                    tag=tex_id, 
                    parent="figure_texture_registry"
                )
                return dpg.add_image(tex_id, user_data=tex_id)
            else:
                label_text: str = kwargs.get('label') or "Figure"
                return dpg.add_text(label_text, user_data="hidden_figure")


    @classmethod
    def get(cls: type, input_id: int | str) -> list[Any] | Any:
        parent: int | str = dpg.get_item_parent(input_id)
        user_data: list[int | str] | None = dpg.get_item_user_data(parent)
        
        results: list[Any] = []
        if user_data:
            attribute: int | str
            for attribute in user_data:
                label: str = dpg.get_item_label(attribute)
                node: Any = dpg.get_item_user_data(dpg.get_item_parent(attribute))
                results.append(getattr(node, label))

        return results[0] if cls.single and results else results


    @classmethod 
    def set(cls: type, input_id: int | str, fig: plt.Figure) -> bool:
        if not cls.display:
            return True

        canvas: FigureCanvas = FigureCanvas(fig)
        canvas.draw()
        
        w: int
        h: int
        w, h = canvas.get_width_height()
        tex_data: np.ndarray = np.frombuffer(canvas.buffer_rgba(), dtype=np.uint8).astype(np.float32) / 255.0

        tex_id: int | str = dpg.get_item_user_data(input_id)
        
        dpg.configure_item(tex_id, width=w, height=h)
        dpg.set_value(tex_id, tex_data)
        
        plt.close(fig) 
        return True