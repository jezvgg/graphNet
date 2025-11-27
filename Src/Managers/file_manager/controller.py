import time

from typing import List, Set, Optional, Dict, Any, Callable

from pathlib import Path

from .scanner import FileScanner, FileItem




class FileDialogController:
    """Core business logic controller for the file dialog.
    
    Manages navigation, file selection, filtering, and dialog state without any
    Dear PyGui dependencies. Implements multi-selection patterns (Ctrl/Shift) and
    handles double-click actions on files and directories.
    
    Attributes:
        current_path: Current directory path being displayed.
        selected_files: Set of selected file/directory paths.
        search_query: Current search query for filtering files by name.
        filter_selected: Currently selected file extension filter (e.g., ".py").
        file_list_cache: Cached list of files in current directory for index lookup.
        anchor_index: Starting index for Shift-based range selection.
        last_selected_index: Index of last clicked item for selection continuity.
        last_click_time: Timestamp of last click for double-click detection.
        last_clicked_path: Path of last clicked item for double-click detection.
        closed: Flag indicating if dialog has been closed.
        scanner: File system scanner for directory contents.
        callback: Callback function triggered on dialog confirmation.
        dirs_only: If True, only directories can be selected.
        _result: Final result paths to return to callback.
    """
    
    def __init__(
        self,
        scanner: FileScanner,
        callback: Optional[Callable[[List[str]], None]] = None,
        dirs_only: bool = False
    ):
        """Initializes the controller with dependencies and default state.
        
        Args:
            scanner: File system scanner instance for directory operations.
            callback: Optional callback to invoke on confirmation. Receives list of paths.
            dirs_only: If True, restricts selection to directories only.
        """
        self.current_path: str = str(Path.home())
        self.selected_files: Set[str] = set()
        self.search_query: str = ""
        self.filter_selected: str = ".*"
        self.file_list_cache: List[Dict[str, Any]] = []
        self.anchor_index: Optional[int] = None
        self.last_selected_index: Optional[int] = None
        self.last_click_time: float = 0.0
        self.last_clicked_path: Optional[str] = None
        self.closed: bool = False
        self._result: List[str] = []
        
        self.scanner = scanner
        self.callback = callback
        self.dirs_only = dirs_only

    
    def refresh_directory(self) -> List[FileItem]:
        """Scans and returns items in the current directory with active filters.
        
        Applies search query and file extension filters. Updates the file list cache
        for selection operations. Automatically triggers UI refresh in the view layer.
        
        Returns:
            List of FileItem objects representing directory contents.
        """
        items = self.scanner.scan_directory(
            Path(self.current_path),
            search_query=self.search_query,
            file_filter=self.filter_selected
        )
        self.file_list_cache = [{
            "path": item.path,
            "is_dir": item.is_dir,
            "name": item.name
        } for item in items]
        return items

    def navigate_to(self, path: str):
        """Navigates to the specified directory path.
        
        Updates current_path and triggers directory refresh. Path is normalized
        to absolute form before navigation.
        
        Args:
            path: Target directory path to navigate to.
        """
        self.current_path = str(Path(path).resolve())
    
    def go_back(self):
        """Navigates to the parent directory of current path.
        
        Does nothing if already at filesystem root. Updates current_path and
        triggers directory refresh.
        """
        current = Path(self.current_path)
        parent = current.parent
        if parent != current: 
            self.current_path = str(parent)
    
    def set_search_query(self, query: str):
        """Sets the search query for filtering files by name.
        
        Query is case-insensitive. Empty query clears the filter. Automatically
        triggers directory refresh.
        
        Args:
            query: Substring to match in file/directory names.
        """
        self.search_query = query
    
    def set_file_filter(self, filter_ext: str):
        """Sets the file extension filter for displayed items.
        
        Special value ".*" shows all files. Automatically triggers directory refresh.
        
        Args:
            filter_ext: File extension filter (e.g., ".py", ".txt", ".*").
        """
        self.filter_selected = filter_ext
    
    def select_file(
        self,
        path: str,
        *,
        ctrl_pressed: bool = False,
        shift_pressed: bool = False
    ):
        """Handles file selection with keyboard modifier support.
        
        Implements standard multi-selection patterns:
        - No modifiers: Select only this item
        - Ctrl pressed: Toggle item in selection
        - Shift pressed: Select range from anchor to current item
        
        Also handles double-click detection for confirmation actions.
        
        Args:
            path: Path of the clicked file/directory.
            ctrl_pressed: Whether Ctrl key was pressed during click.
            shift_pressed: Whether Shift key was pressed during click.
        """
        now = time.time()
        
        if now - self.last_click_time < 0.5 and self.last_clicked_path == path:
            self.handle_double_click(path)
            self.last_click_time = 0.0
            self.last_clicked_path = None
            return
        
        self.last_click_time = now
        self.last_clicked_path = path
        
        clicked_index = next(
            (i for i, item in enumerate(self.file_list_cache) if item["path"] == path),
            None
        )
        
        if not ctrl_pressed and not shift_pressed:
            self.selected_files = {path}
            self.anchor_index = clicked_index
            self.last_selected_index = clicked_index
            return
        
        if ctrl_pressed:
            new_selection = set(self.selected_files)
            if path in new_selection:
                new_selection.remove(path)
                if self.last_selected_index == clicked_index:
                    self.last_selected_index = None
                if self.anchor_index == clicked_index:
                    self.anchor_index = None
            else:
                new_selection.add(path)
                self.last_selected_index = clicked_index
                if self.anchor_index is None:
                    self.anchor_index = clicked_index
            self.selected_files = new_selection
            return
        
        if shift_pressed and self.anchor_index is not None and clicked_index is not None:
            start = min(self.anchor_index, clicked_index)
            end = max(self.anchor_index, clicked_index)
            new_selection = [
                self.file_list_cache[i]["path"]
                for i in range(start, end + 1)
                if i < len(self.file_list_cache)
            ]
            self.selected_files = set(new_selection)
            self.last_selected_index = clicked_index

    def handle_double_click(self, path: str):
        """Processes double-click action on file or directory.
        
        For directories: Navigates into the directory.
        For files: Confirms selection if in file mode, or ignores if in directory-only mode.
        
        Args:
            path: Path of the double-clicked item.
        """
        item_path = Path(path)
        if item_path.is_dir():
            self.navigate_to(str(item_path))
        elif not self.dirs_only:
            self.confirm_selection([path])

    def confirm_selection(self, paths: Optional[List[str]] = None):
        """Confirms the current selection and closes the dialog.
        
        Filters results based on dirs_only mode. Invokes callback with final paths.
        Sets closed flag to prevent further interactions.
        
        Args:
            paths: Optional override for selected paths. If None, uses current selection.
        """
        selected = paths or list(self.selected_files)
        
        if self.dirs_only:
            self._result = [p for p in selected if Path(p).is_dir()]
        else:
            self._result = [p for p in selected if not Path(p).is_dir()]
        
        self.closed = True
        if self.callback:
            self.callback(self._result)
    
    def cancel_selection(self):
        """Cancels selection and closes dialog with empty result.
        
        Clears all selected files and invokes callback with empty list.
        """
        self.selected_files.clear()
        self._result = []
        self.closed = True
        if self.callback:
            self.callback(self._result)