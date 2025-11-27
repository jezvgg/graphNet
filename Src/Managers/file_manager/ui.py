import dearpygui.dearpygui as dpg

from typing import List, Tuple, Set, Dict, Any

from pathlib import Path

from .icon_handler import IconHandler
from .controller import FileDialogController
from .shortcuts import get_shortcuts_via_platform
from .scanner import FileItem




class FileDialogUI:
    """User interface component for the file dialog using Dear PyGui.
    
    This class handles all UI rendering, event handling, and synchronization between
    the user interface and the business logic controller. It implements a passive view
    pattern where all state is managed by the controller.
    
    The UI consists of:
      - Left sidebar with platform-specific shortcuts
      - Main toolbar with navigation controls
      - File table displaying current directory contents
      - Footer with file type filter and action buttons
    
    Note:
        This class has no business logic - it delegates all actions to the controller
        and updates the UI based on controller state.
    
    Attributes:
        controller: Business logic controller handling file operations.
        title: Window title displayed in the dialog header.
        window_tag: Unique Dear PyGui tag for the main window.
        show_shortcuts_menu: Whether to display the left sidebar with shortcuts.
        icon_handler: Handler for loading and accessing UI icons.
        _table_tag: Dear PyGui tag for the main file table.
    """

    def __init__(
        self,
        controller: FileDialogController,
        *,
        title: str,
        tag: str,
        width: int,
        height: int,
        min_size: Tuple[int, int],
        show_shortcuts_menu: bool,
        no_resize: bool,
        modal: bool,
        icon_handler: IconHandler
    ):
        """Initializes the file dialog UI.
        
        Creates all Dear PyGui widgets and sets up initial state synchronization.
        
        Args:
            controller: Business logic controller to delegate actions to.
            title: Title for the dialog window.
            tag: Base tag used to generate unique widget identifiers.
            width: Initial width of the dialog window.
            height: Initial height of the dialog window.
            min_size: Minimum allowed size (width, height) for the window.
            show_shortcuts_menu: Whether to show the shortcuts sidebar.
            no_resize: If True, disables window resizing by the user.
            modal: If True, makes the dialog modal (blocks interaction with other windows).
            icon_handler: Handler for loading and accessing UI icons.
        """
        self.controller = controller
        self.title = title
        self.window_tag = f"{tag}_window"
        self.show_shortcuts_menu = show_shortcuts_menu
        self.icon_handler = icon_handler
        self._table_tag = 'explorer' 
        
        self._setup_ui(
            width=width,
            height=height,
            min_size=min_size,
            no_resize=no_resize,
            modal=modal
        )
        
        self._refresh_view()


    def show(self):
        """Displays the file dialog window and focuses on it.
        
        Makes the window visible and sets keyboard focus to enable immediate interaction.
        This should be called after all UI setup is complete.
        """
        dpg.show_item(self.window_tag)
        dpg.focus_item(self.window_tag)
    
    def _close_window(self):
        """Closes the file dialog window.
        
        Hides the window from view but does not destroy widgets. The dialog can be
        shown again later by calling `show()` again.
        
        Note:
            This does not reset the controller state - use controller methods for that.
        """
        dpg.hide_item(self.window_tag)
    
    def _refresh_view(self):
        """Refreshes the entire UI based on current controller state.
        
        Updates all UI components to reflect the current state of the controller:
          1. Path input field
          2. File table contents
          3. Selection state of files
        
        This method should be called after any operation that changes the controller state
        (navigation, search, filtering, etc.).
        """
        dpg.set_value("ex_path_input", self.controller.current_path)
        
        files = self.controller.refresh_directory()
        self._update_table(files)
        
        self._sync_selection()

    
    def _on_path_enter(self, sender, app_data):
        """Handles path input submission (Enter key pressed).
        
        Validates the entered path and navigates to it if valid. Shows an error message
        if the path is invalid or not a directory.
        
        Args:
            sender: Dear PyGui item that triggered the event.
            app_data: New path value entered by the user.
        """
        new_path = app_data.strip()
        if Path(new_path).exists() and Path(new_path).is_dir():
            self.controller.navigate_to(new_path)
            self._refresh_view()
        else:
            print(f"❌ Invalid path: {new_path}")

    def _on_search(self, sender, app_data):
        """Handles search query input.
        
        Updates the controller's search query and refreshes the view to show filtered results.
        
        Args:
            sender: Dear PyGui item that triggered the event.
            app_data: Current search query text.
        """
        self.controller.set_search_query(app_data)
        self._refresh_view() 

    def _on_filter_change(self, sender, app_data):
        """Handles file type filter selection.
        
        Updates the controller's file filter and refreshes the view to show filtered results.
        
        Args:
            sender: Dear PyGui item that triggered the event.
            app_data: Selected file extension filter (e.g., ".py", ".*").
        """
        self.controller.set_file_filter(app_data)
        self._refresh_view() 

    def _on_file_click(self, sender, app_data, user_data):
        """Handles single click on a file or folder.
        
        Delegates selection logic to the controller with current keyboard modifiers
        (Ctrl/Shift keys) to support multi-selection patterns.
        
        Args:
            sender: Dear PyGui item that triggered the event.
            app_data: Event-specific data (not used).
            user_data: Dictionary containing file path and index in the list.
        """
        self.controller.select_file(
            user_data["path"],
            ctrl_pressed=dpg.is_key_down(dpg.mvKey_LControl),
            shift_pressed=dpg.is_key_down(dpg.mvKey_LShift)
        )
        self._sync_selection() 

    def _on_file_double_click(self, sender, app_data, user_data):
        """Handles double click on a file or folder.
        
        For folders: navigates to the directory.
        For files: selects the file and closes the dialog (confirms selection).
        
        Args:
            sender: Dear PyGui item that triggered the event.
            app_data: Event-specific data (not used).
            user_data: Dictionary containing file path and index in the list.
        """
        self.controller.handle_double_click(user_data["path"])
        if self.controller.closed:  
            self._close_window()
        else:
            self._refresh_view() 

    def _on_shortcut_click(self, sender, app_data, user_data):
        """Handles click on a shortcut in the sidebar.
        
        Navigates to the shortcut's target path and refreshes the view.
        
        Args:
            sender: Dear PyGui item that triggered the event.
            app_data: Event-specific data (not used).
            user_data: Dictionary containing the target path.
        """
        self.controller.navigate_to(user_data['path'])
        self._refresh_view()

    def _on_ok(self, sender, app_data):
        """Handles OK button click.
        
        Confirms the current selection and closes the dialog if successful.
        The controller's callback will be invoked with the result.
        """
        self.controller.confirm_selection()
        if self.controller.closed:
            self._close_window()

    def _on_cancel(self, sender, app_data):
        """Handles Cancel button click.
        
        Cancels the selection (clears selected files) and closes the dialog.
        The controller's callback will be invoked with an empty result.
        """
        self.controller.cancel_selection()
        self._close_window()

    
    def _sync_selection(self):
        """Synchronizes visual selection state with controller.
        
        Updates the checked state of all file selectables in the table to match
        the controller's current selection state. This method is called after
        any selection change operation.
        
        Note:
            This method assumes the file_list_cache in the controller is up to date
            and matches the current table contents.
        """
        try:
            rows = dpg.get_item_children(self._table_tag, slot=1)
            for row_idx, row in enumerate(rows):
                cells = dpg.get_item_children(row, slot=1)
                if not cells:
                    continue
                
                first_cell = cells[0]
                group_items = dpg.get_item_children(first_cell, slot=1)
                if len(group_items) < 2:
                    continue
                
                selectable = group_items[1]
                if dpg.get_item_type(selectable) == "mvAppItemType::mvSelectable":
                    if row_idx < len(self.controller.file_list_cache):
                        file_info = self.controller.file_list_cache[row_idx]
                        path = file_info["path"]
                        is_selected = path in self.controller.selected_files
                        dpg.set_value(selectable, is_selected)
        except Exception as e:
            print(f"❌ Error syncing selection: {e}")

    def _update_table(self, files: List[FileItem]):
        """Completely redraws the file table with new data.
        
        Clears the existing table contents and populates it with new file items.
        Also updates the controller's file_list_cache for selection synchronization.
        
        Args:
            files: List of FileItem objects to display in the table.
        """
        try:
            for child in dpg.get_item_children(self._table_tag, slot=1):
                dpg.delete_item(child)
                
            self.controller.file_list_cache = [
                {
                    "path": f.path,
                    "is_dir": f.is_dir,
                    "name": f.name
                } for f in files
            ]
            
            for idx, file in enumerate(files):
                with dpg.table_row(parent=self._table_tag):
                    with dpg.table_cell():
                        with dpg.group(horizontal=True) as item_group:
                            dpg.add_image(
                                file.icon_tag,
                                width=16,
                                height=16
                            )
                            dpg.add_selectable(
                                label=file.name,
                                span_columns=False,
                                height=20,
                                user_data={"path": file.path, "index": idx}
                            )
                        
                        with dpg.item_handler_registry() as handler:
                            dpg.add_item_clicked_handler(
                                callback=self._on_file_click,
                                user_data={"path": file.path, "index": idx}
                            )
                            dpg.add_item_double_clicked_handler(
                                callback=self._on_file_double_click,
                                user_data={"path": file.path, "index": idx}
                            )
                        dpg.bind_item_handler_registry(item_group, handler)
                    
                    # Остальные ячейки
                    with dpg.table_cell():
                        dpg.add_text(file.date_str)
                    with dpg.table_cell():
                        dpg.add_text(file.type_str)
                    with dpg.table_cell():
                        dpg.add_text(file.size_str)
                        
        except Exception as e:
            print(f"❌ Error updating table: {e}")

    
    def _setup_ui(
        self,
        width: int,
        height: int,
        min_size: Tuple[int, int],
        no_resize: bool,
        modal: bool
    ):
        """Creates all Dear PyGui widgets for the dialog.
        
        Builds the entire UI hierarchy including window, layout containers,
        and all interactive elements. This method is called once during initialization.
        
        Args:
            width: Initial window width.
            height: Initial window height.
            min_size: Minimum allowed window size (width, height).
            no_resize: Whether to disable window resizing.
            modal: Whether to make the window modal.
        """
        with dpg.window(
            label=self.title,
            tag=self.window_tag,
            no_resize=no_resize,
            show=False,
            modal=modal,
            width=width,
            height=height,
            min_size=min_size,
            no_collapse=True,
            pos=(50, 50)
        ):
            with dpg.group(horizontal=True):
                if self.show_shortcuts_menu:
                    with dpg.child_window(width=200, height=-50, border=True):
                        self._build_shortcuts_menu()
                else:
                    dpg.add_spacer(width=10)
                
                with dpg.child_window(height=-50, border=True):
                    self._build_toolbar()
                    self._build_table()
            
            self._build_footer()

    def _build_shortcuts_menu(self):
        """Builds the left sidebar with platform-specific shortcuts.
        
        Creates menu items for each shortcut returned by get_shortcuts_via_platform().
        Each item displays an icon and label, and navigates to the target path on click.
        
        Note:
            Shortcuts are generated based on the current operating system.
        """
        config = get_shortcuts_via_platform() 
        
        for item in config.items:
            with dpg.group(horizontal=True):
                dpg.add_image(
                    self.icon_handler.get_icon_tag(item.icon_tag),
                    width=16,
                    height=16
                )
                dpg.add_menu_item(
                    label=item.label,
                    user_data={'path': str(item.path)},
                    callback=self._on_shortcut_click
                )

    def _build_toolbar(self):
        """Builds the top toolbar with navigation controls.
        
        Creates:
          - Refresh button (rescans current directory)
          - Back button (navigates to parent directory)
          - Path input field (allows manual path entry)
          - Search field (filters files by name)
        """
        with dpg.group(horizontal=True):
            dpg.add_image_button(
                self.icon_handler.get_icon_tag("refresh"),
                width=20,
                height=20,
                callback=lambda: self._refresh_view()
            )
            dpg.add_image_button(
                self.icon_handler.get_icon_tag("back"),
                width=20,
                height=20,
                callback=lambda: [self.controller.go_back(), self._refresh_view()]
            )
            
            dpg.add_input_text(
                hint="Path",
                on_enter=True,
                callback=self._on_path_enter,
                default_value=self.controller.current_path,
                width=-1,
                tag="ex_path_input"
            )
        
        dpg.add_input_text(
            hint="Search files",
            callback=self._on_search,
            tag="ex_search",
            width=-1
        )

    def _build_table(self):
        """Builds the main file table.
        
        Creates a resizable, scrollable table with columns for:
          - File name (with icon)
          - Modification date
          - File type
          - File size
        """
        with dpg.table(
            tag=self._table_tag,
            height=-1,
            width=-1,
            resizable=True,
            policy=dpg.mvTable_SizingStretchProp,
            borders_innerV=True,
            borders_outerV=True,
            borders_innerH=True,
            borders_outerH=True,
            reorderable=True,
            sortable=False,
            scrollX=True,
            scrollY=True,
        ):
            dpg.add_table_column(label='Name', init_width_or_weight=300)
            dpg.add_table_column(label='Date', init_width_or_weight=150)
            dpg.add_table_column(label='Type', init_width_or_weight=100)
            dpg.add_table_column(label='Size', init_width_or_weight=80)

    def _build_footer(self):
        """Builds the footer section with filter and action buttons.
        
        Creates:
          - File type filter dropdown
          - OK button (confirms selection)
          - Cancel button (closes dialog without selection)
        """
        with dpg.group(horizontal=True):
            dpg.add_text('File type filter', color=(200, 200, 200))
            dpg.add_combo(
                items=list(self.controller.scanner._ICON_MAP.keys()) or [".*", ".txt", ".py"],
                default_value=self.controller.filter_selected,
                width=150,
                callback=self._on_filter_change
            )
        
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=400)
                dpg.add_button(
                    label="   OK   ",
                    width=80,
                    height=30,
                    callback=self._on_ok
                )
                dpg.add_button(
                    label=" Cancel ",
                    width=80,
                    height=30,
                    callback=self._on_cancel
                )