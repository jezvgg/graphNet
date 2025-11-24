# state.py
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class FileDialogState:
    current_path: str = ""
    selected_files: List[str] = field(default_factory=list)
    last_click_time: float = 0.0
    last_clicked_element: str = ""
    search_query: str = ""
    filter_selected: str = ".*"
    
    last_selected_index: Optional[int] = None  # индекс последнего кликнутого элемента
    anchor_index: Optional[int] = None        # индекс "якоря" для Shift
    file_list_cache: List[dict] = field(default_factory=list) 
    
    on_close: bool = False
