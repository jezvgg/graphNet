from typing import List, Callable, Optional, Tuple

from pathlib import Path

from .controller import FileDialogController
from .scanner import FileScanner
from .ui import FileDialogUI
from .icon_handler import IconHandler




class FileDialog:
    """Main facade class for the file dialog system.
    
    Provides a unified interface for creating and managing file dialogs:
    
    **Asynchronous mode** (callback-based):
        ```python
        dialog = FileDialog(callback=lambda result: print(f"Selected: {result}"))
        dialog.show()
        ```
    
    Attributes:
        title: Dialog window title.
        tag: Base identifier for Dear PyGui widgets.
        width: Initial dialog width in pixels.
        height: Initial dialog height in pixels.
        min_size: Minimum allowed size (width, height).
        dirs_only: If True, only directories can be selected.
        default_path: Initial directory path. Defaults to user home directory.
        filter_list: Available file extension filters.
        file_filter: Currently selected file filter.
        callback: Function called when selection is confirmed.
        show_dir_size: Whether to display directory sizes (not implemented).
        allow_drag: Whether drag-and-drop is enabled (not implemented).
        multi_selection: Whether multiple files can be selected.
        show_shortcuts_menu: Whether to show platform-specific shortcuts sidebar.
        no_resize: Whether to disable window resizing.
        modal: Whether dialog blocks interaction with other windows.
        show_hidden_files: Whether to show hidden files/directories.
        user_style: Reserved for future UI theming (not implemented).
        controller: Business logic controller instance.
        ui: User interface component instance.
    """
    
    def __init__(
        self,
        *,
        title: str = "File dialog",
        tag: str = "file_dialog",
        width: int = 950,
        height: int = 650,
        min_size: Tuple[int, int] = (460, 320),
        dirs_only: bool = False,
        default_path: Optional[str] = None,
        filter_list: Optional[List[str]] = None,
        file_filter: str = ".*",
        callback: Optional[Callable[[List[str]], None]] = None,
        show_dir_size: bool = False,
        allow_drag: bool = True,
        multi_selection: bool = True,
        show_shortcuts_menu: bool = True,
        no_resize: bool = True,
        modal: bool = True,
        show_hidden_files: bool = False,
        user_style: int = 0,
        icon_handler: Optional[IconHandler] = None
    ):
        """Initializes a new file dialog instance.
        
        Creates all necessary dependencies and sets up the UI. Parameters are stored directly
        on the instance rather than in a separate configuration object.
        
        Args:
            title: Window title text.
            tag: Base identifier for Dear PyGui widgets (suffixes will be added).
            width: Initial window width in pixels.
            height: Initial window height in pixels.
            min_size: Minimum allowed window dimensions (width, height).
            dirs_only: If True, only directories can be selected; files are ignored.
            default_path: Initial directory to display. If None, uses user's home directory.
            filter_list: List of available file filters (e.g., [".*", ".txt", ".py"]).
            file_filter: Initially selected file filter. Defaults to ".*" (all files).
            callback: Function to call when selection is confirmed. Receives list of paths.
            show_dir_size: Whether to calculate and show directory sizes (computationally expensive).
            allow_drag: Whether to enable drag-and-drop functionality (reserved for future).
            multi_selection: Whether multiple files/directories can be selected.
            show_shortcuts_menu: Whether to display the platform-specific shortcuts sidebar.
            no_resize: If True, disables window resizing by the user.
            modal: If True, blocks interaction with other application windows.
            show_hidden_files: Whether to show hidden files (dotfiles on Unix, hidden on Windows).
            user_style: Reserved for future theming support (0=default, 1=dark, etc.).
            icon_handler: Custom icon handler. If None, creates default handler with built-in icons.
        """
        self.title = title
        self.tag = tag
        self.width = width
        self.height = height
        self.min_size = min_size
        self.dirs_only = dirs_only
        self.default_path = default_path or str(Path.home())
        self.filter_list = filter_list or self._default_filter_list()
        self.file_filter = file_filter
        self.callback = callback
        self.show_dir_size = show_dir_size
        self.allow_drag = allow_drag
        self.multi_selection = multi_selection
        self.show_shortcuts_menu = show_shortcuts_menu
        self.no_resize = no_resize
        self.modal = modal
        self.show_hidden_files = show_hidden_files
        self.user_style = user_style
        
        self._result_ready = False
        self._result: List[str] = []
        
        self._setup_dependencies(icon_handler)

    def _setup_dependencies(self, icon_handler: Optional[IconHandler]):
        """Initializes and wires together all internal dependencies.
        
        Creates the scanner, controller, and UI components with appropriate parameters.
        This method is called during initialization and should not be called externally.
        
        Args:
            icon_handler: Optional custom icon handler. If None, creates a default handler
                pointing to the built-in assets/icons directory.
        
        Note:
            The icon handler path is resolved relative to this module's location.
            Icons are loaded immediately to prevent UI delays later.
        """
        scanner = FileScanner(
            show_hidden=self.show_hidden_files,
            dirs_only=self.dirs_only
        )
        
        self.controller = FileDialogController(
            scanner=scanner,
            callback=self._handle_callback,
            dirs_only=self.dirs_only
        )
        
        if icon_handler is None:
            icon_path = Path(__file__).parent.parent.parent.parent / "Assets" / "icons"
            icon_handler = IconHandler(icon_path)
        icon_handler.load_icons()  
        
        self.ui = FileDialogUI(
            controller=self.controller,
            title=self.title,
            tag=self.tag,
            width=self.width,
            height=self.height,
            min_size=self.min_size,
            show_shortcuts_menu=self.show_shortcuts_menu,
            no_resize=self.no_resize,
            modal=self.modal,
            icon_handler=icon_handler
        )

    def _handle_callback(self, result: List[str]):
        """Internal callback handler for controller confirmation events.
        
        Stores the result and sets the ready flag for synchronous mode.
        Invokes the user-provided callback if available.
        
        Args:
            result: List of selected file/directory paths from the controller.
        """
        self._result = result
        self._result_ready = True
        if self.callback:
            self.callback(result)

    def show(self):
        """Displays the dialog window in asynchronous mode.
        
        The dialog appears immediately and runs in the background. Results are delivered
        via the callback function when the user confirms selection.
        
        Note:
            In Dear PyGui applications, this typically doesn't block the main thread
            because Dear PyGui processes events in its own render loop.
        """
        self.ui.show()

    @staticmethod
    def _default_filter_list() -> List[str]:
        """Returns the default list of file extension filters.
        
        Provides common file types grouped by category for the file type dropdown.
        
        Returns:
            List of file extension filters including:
              - ".*" for all files
              - Text files (.txt)
              - Scripts (.py)
              - Images (.png, .jpg, .jpeg, .gif, .bmp)
              - Documents (.pdf, .doc, .docx)
              - Spreadsheets (.xls, .xlsx)
              - Archives (.zip, .rar, .7z)
        """
        return [
            ".*", ".txt", ".py", ".png", ".jpg", ".jpeg", ".gif", ".bmp", 
            ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip", ".rar", ".7z"
        ]