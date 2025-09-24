
from .manager import FileDialogManager
import logging



file_dialog = FileDialogManager()

def show_file_dialog(**kwargs):
    return file_dialog.show(**kwargs)

def ask_open_file(**kwargs):
    kwargs.setdefault("multi_selection", False)
    kwargs.setdefault("dirs_only", False)
    return file_dialog.show_and_get_result(**kwargs)

def ask_open_files(**kwargs):
    kwargs.setdefault("multi_selection", True)
    kwargs.setdefault("dirs_only", False)
    return file_dialog.show_and_get_result(**kwargs)

def ask_directory(**kwargs):
    kwargs.setdefault("dirs_only", True)
    kwargs.setdefault("multi_selection", False)
    return file_dialog.show_and_get_result(**kwargs)