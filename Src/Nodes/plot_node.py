from typing import Any

import matplotlib
import numpy as np

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from Src.Enums import Themes
from Src.Nodes.data_node import DataNode


class PlotNode(DataNode):
    theme_name: Themes = Themes.PLOT


    @staticmethod
    def create_plot(x: Any = None, y: Any = None, title: str = "My Plot") -> plt.Figure:
        '''
        Создаёт график по переданным данным.
        '''
        fig: plt.Figure
        ax: Any
        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)

        if x is not None and y is not None:
            x_len: int = x.shape[0] if hasattr(x, 'shape') else len(x)
            y_len: int = y.shape[0] if hasattr(y, 'shape') else len(y)
            
            if x_len == y_len:
                ax.plot(x, y)
            else:
                ax.plot(x, label='x')
                ax.plot(y, label='y')
                ax.legend()
        elif x is not None:
            ax.plot(x)
        elif y is not None:
            ax.plot(y)
        
        if x is not None or y is not None:
            ax.grid(True)

        ax.set_title(title)
        fig.tight_layout()
        return fig


    def compile(self, kwargs: dict[str, Any] | None = None) -> bool:
        status: bool = super().compile(kwargs)
        if not status:
            return False
            
        self.figure = self.OUTPUT
        return status