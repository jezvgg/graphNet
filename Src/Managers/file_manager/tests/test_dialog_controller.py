import pytest
import time
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import MagicMock, patch

from file_manager.controller import FileDialogController
from file_manager.scanner import FileScanner, FileItem


@pytest.fixture
def fs():
    """pyfakefs fixture for virtual filesystem tests."""
    pass


@pytest.fixture
def mock_scanner(fs):
    """Creates a scanner with mock filesystem structure."""
    # Create test filesystem
    fs.create_dir("/home/user")
    fs.create_dir("/home/user/Documents")
    fs.create_dir("/home/user/Pictures")
    fs.create_file("/home/user/Documents/report.txt", contents="test")
    fs.create_file("/home/user/Documents/data.csv", contents="1,2,3")
    fs.create_file("/home/user/Pictures/vacation.jpg", contents="image")
    fs.create_file("/home/user/script.py", contents="print('hello')")
    
    # Create scanner with virtual FS
    scanner = FileScanner(show_hidden=False, dirs_only=False)
    return scanner


@pytest.fixture
def controller(mock_scanner):
    """Controller fixture with mocked callback."""
    mock_callback = MagicMock()
    controller = FileDialogController(
        scanner=mock_scanner,
        callback=mock_callback,
        dirs_only=False
    )
    controller.current_path = "/home/user"
    return controller


class TestNavigation:
    """Tests for directory navigation functionality."""
    
    def test_navigate_to_updates_path(self, controller):
        """Verify navigation updates current path correctly."""
        controller.navigate_to("/home/user/Documents")
        assert controller.current_path == "/home/user/Documents"
        
        # Verify path normalization
        controller.navigate_to("/home/../home/user/Pictures")
        assert controller.current_path == str(Path("/home/user/Pictures").resolve())
    
    def test_go_back_moves_to_parent(self, controller):
        """Verify back navigation moves to parent directory."""
        controller.current_path = "/home/user/Documents"
        controller.go_back()
        assert controller.current_path == "/home/user"
    
    def test_go_back_at_root_does_nothing(self, controller, fs):
        """Verify back navigation at filesystem root has no effect."""
        # Create root structure
        fs.create_dir("/root_dir")
        controller.current_path = "/root_dir"
        
        # Get root path (platform independent)
        root_path = str(Path("/root_dir").resolve().root)
        controller.current_path = root_path
        
        original_path = controller.current_path
        controller.go_back()
        assert controller.current_path == original_path


class TestFileSelection:
    """Tests for file selection logic with modifiers."""
    
    def test_select_file_single_selection(self, controller):
        """Verify single selection replaces existing selection."""
        controller.refresh_directory()
        
        controller.select_file("/home/user/Documents")
        assert controller.selected_files == {"/home/user/Documents"}
        
        controller.select_file("/home/user/Pictures")
        assert controller.selected_files == {"/home/user/Pictures"}
    
    def test_select_file_ctrl_toggle(self, controller):
        """Verify Ctrl+click toggles items in selection."""
        controller.refresh_directory()
        
        # First item
        controller.select_file("/home/user/Documents", ctrl_pressed=True)
        assert controller.selected_files == {"/home/user/Documents"}
        
        # Add second item
        controller.select_file("/home/user/Pictures", ctrl_pressed=True)
        assert controller.selected_files == {
            "/home/user/Documents",
            "/home/user/Pictures"
        }
        
        # Remove first item
        controller.select_file("/home/user/Documents", ctrl_pressed=True)
        assert controller.selected_files == {"/home/user/Pictures"}
    
    def test_select_file_shift_range(self, controller):
        """Verify Shift+click selects range between anchor and current."""
        controller.refresh_directory()
        
        # First click sets anchor
        controller.select_file("/home/user/Documents")
        assert controller.anchor_index == 0  # Assuming Documents is first item
        
        # Shift+click selects range
        controller.select_file("/home/user/Pictures", shift_pressed=True)
        
        # Should have both items selected
        assert controller.selected_files == {
            "/home/user/Documents",
            "/home/user/Pictures"
        }
    
    def test_select_file_mixed_modifiers(self, controller):
        """Verify modifier combinations work correctly."""
        controller.refresh_directory()
        
        # Select first item
        controller.select_file("/home/user/Documents")
        
        # Ctrl+click to add second
        controller.select_file("/home/user/script.py", ctrl_pressed=True)
        
        # Shift+click from first to third item
        controller.select_file("/home/user/Pictures", shift_pressed=True)
        
        # Should have range selection from Documents to Pictures
        expected = {
            "/home/user/Documents",
            "/home/user/Pictures"
        }
        # script.py should be deselected due to shift range
        assert controller.selected_files == expected


class TestDoubleClickActions:
    """Tests for double-click behavior on files and directories."""
    
    def test_double_click_directory_navigates(self, controller):
        """Verify double-click on directory navigates to it."""
        controller.handle_double_click("/home/user/Documents")
        assert controller.current_path == "/home/user/Documents"
    
    def test_double_click_file_confirms_selection(self, controller):
        """Verify double-click on file confirms selection in file mode."""
        controller.handle_double_click("/home/user/script.py")
        assert controller.closed is True
        assert controller._result == ["/home/user/script.py"]
        controller.callback.assert_called_once_with(["/home/user/script.py"])
    
    def test_double_click_file_in_dirs_only_ignored(self, controller):
        """Verify double-click on file is ignored in directory-only mode."""
        controller.dirs_only = True
        controller.handle_double_click("/home/user/script.py")
        assert controller.closed is False
        assert controller._result == []
    
    @patch("time.time")
    def test_double_click_detection_timing(self, mock_time, controller):
        """Verify double-click detection respects timing threshold."""
        mock_time.side_effect = [0.0, 0.3, 1.0]  # First click, second click (within threshold), third click
        
        # First click
        controller.select_file("/home/user/Documents")
        
        # Second click within threshold should trigger double-click
        with patch.object(controller, "handle_double_click") as mock_double_click:
            controller.select_file("/home/user/Documents")
            mock_double_click.assert_called_once_with("/home/user/Documents")
        
        # Third click after threshold should be single click
        with patch.object(controller, "handle_double_click") as mock_double_click:
            controller.select_file("/home/user/Documents")
            mock_double_click.assert_not_called()


class TestFiltering:
    """Tests for search and file type filtering."""
    
    def test_set_search_query_filters_files(self, controller):
        """Verify search query filters files by name."""
        controller.set_search_query("doc")
        items = controller.refresh_directory()
        
        # Should only show items containing "doc" (case-insensitive)
        names = [item.name.lower() for item in items]
        assert "documents" in names
        assert "report.txt" in names
        assert "pictures" not in names
    
    def test_set_file_filter_by_extension(self, controller):
        """Verify file extension filter works correctly."""
        controller.set_file_filter(".py")
        items = controller.refresh_directory()
        
        # Should only show .py files and directories
        paths = [item.path for item in items]
        assert "/home/user/script.py" in paths
        assert "/home/user/Documents" in paths  # Directories always shown
        assert "/home/user/Documents/report.txt" not in paths
    
    def test_combined_search_and_filter(self, controller):
        """Verify search and extension filters work together."""
        controller.set_search_query("data")
        controller.set_file_filter(".csv")
        items = controller.refresh_directory()
        
        # Should only show data.csv
        assert len(items) == 1
        assert items[0].name == "data.csv"


class TestConfirmationAndCancellation:
    """Tests for dialog confirmation and cancellation."""
    
    def test_confirm_selection_dirs_only_mode(self, controller):
        """Verify directory-only mode filters out files."""
        controller.dirs_only = True
        controller.selected_files = {
            "/home/user/Documents",
            "/home/user/Pictures",
            "/home/user/script.py"
        }
        controller.confirm_selection()
        
        assert controller.closed is True
        assert sorted(controller._result) == [
            "/home/user/Documents",
            "/home/user/Pictures"
        ]
    
    def test_confirm_selection_files_only_mode(self, controller):
        """Verify file-only mode filters out directories."""
        controller.dirs_only = False
        controller.selected_files = {
            "/home/user/Documents",
            "/home/user/Pictures",
            "/home/user/script.py",
            "/home/user/Documents/report.txt"
        }
        controller.confirm_selection()
        
        assert controller.closed is True
        assert sorted(controller._result) == [
            "/home/user/Documents/report.txt",
            "/home/user/script.py"
        ]
    
    def test_cancel_selection_clears_result(self, controller):
        """Verify cancellation clears selection and returns empty result."""
        controller.selected_files = {"/home/user/Documents"}
        controller.cancel_selection()
        
        assert controller.closed is True
        assert controller._result == []
        controller.callback.assert_called_once_with([])


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_refresh_empty_directory(self, controller, fs):
        """Verify refreshing an empty directory returns empty list."""
        fs.create_dir("/empty")
        controller.current_path = "/empty"
        items = controller.refresh_directory()
        assert items == []
    
    def test_select_nonexistent_file(self, controller):
        """Verify selecting nonexistent file doesn't crash."""
        controller.refresh_directory()
        controller.select_file("/nonexistent/file.txt")
        assert "/nonexistent/file.txt" in controller.selected_files
    
    def test_double_click_invalid_path(self, controller):
        """Verify double-click on invalid path handles gracefully."""
        with patch("pathlib.Path.is_dir") as mock_is_dir:
            mock_is_dir.side_effect = OSError("Permission denied")
            controller.handle_double_click("/invalid/path")
        # Should not crash and not close dialog
        assert controller.closed is False
    
    def test_anchor_index_reset_on_ctrl_deselect(self, controller):
        """Verify anchor index resets when last anchored item is deselected."""
        controller.refresh_directory()
        
        # Set anchor with first item
        controller.select_file("/home/user/Documents")
        assert controller.anchor_index is not None
        
        # Deselect anchor item with Ctrl
        controller.select_file("/home/user/Documents", ctrl_pressed=True)
        assert controller.anchor_index is None