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

    def compile(self, kwargs: dict[str, Any] | None = None) -> bool:
        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
        
        original_logic = self.logic
        
        def wrapped_logic(*args: Any, **kw: Any) -> Any:
            title = kw.pop("title", "My Plot")
            
            args = [np.squeeze(a) if isinstance(a, np.ndarray) else a for a in args]
            if len(args) == 1 and isinstance(args[0], np.ndarray) and original_logic.__name__ != 'hist':
                data = args[0]
                args = [data[:, 0], data[:, 1]] if data.ndim > 1 and data.shape[1] >= 2 else [np.arange(len(data)), data]
                
            res = original_logic(*args, **kw)
            ax.set_title(title)
            ax.grid(True)
            fig.tight_layout()
            return res
            
        self.logic = wrapped_logic
        status: bool = super().compile(kwargs)
        self.logic = original_logic
        
        if not status:
            plt.close(fig)
            return False
            
        self.figure = fig
        return status