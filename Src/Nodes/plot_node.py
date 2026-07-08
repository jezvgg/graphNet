from typing import Any

import matplotlib
import numpy as np

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from Src.Enums import Themes
from Src.Nodes.data_node import DataNode


from Src.Utils import Backfield

class PlotNode(DataNode):
    theme_name: Themes = Themes.PLOT
    figure: Backfield = Backfield()

    @staticmethod
    def wrapper(func):
        def wrapped_logic(x=None, y=None, title="My Plot", **kwargs):
            fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
            
            raw = [a for a in [x, y] if a is not None]
            
            data_to_plot = (
                [np.squeeze(raw[0])[:, 0], np.squeeze(raw[0])[:, 1]]
                if len(raw) >= 1 and np.squeeze(raw[0]).ndim > 1 and np.squeeze(raw[0]).shape[1] >= 2
                else [np.squeeze(a) for a in raw]
            )

            func(*data_to_plot, **kwargs)

            ax.set_title(title)
            ax.grid(True)
            fig.tight_layout()
            return fig
        return wrapped_logic
    
    def compile(self, kwargs=None):
        status = super().compile(kwargs)
        status = status and setattr(self, 'figure', self.OUTPUT)
        return status
    
