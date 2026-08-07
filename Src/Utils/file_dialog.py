import threading
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import Callable, Optional


def open_file_dialog(
    callback: Callable[[Optional[list[Path]]], None],
    title: str = "Выберите файл",
    filetypes: list[tuple[str, str]] | None = None,
    directory: bool = False,
    multi: bool = False,
) -> None:
    """Вызывает нативный файловый диалог ОС в отдельном потоке."""
    if filetypes is None:
        filetypes = [("All files", "*.*")]

    def _run_dialog():
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)

        result = None
        if directory:
            path = filedialog.askdirectory(title=title)
            if path:
                result = [Path(path)]
        elif multi:
            paths = filedialog.askopenfilenames(title=title, filetypes=filetypes)
            if paths:
                result = [Path(p) for p in paths]
        else:
            path = filedialog.askopenfilename(title=title, filetypes=filetypes)
            if path:
                result = [Path(path)]

        root.destroy()
        callback(result)

    threading.Thread(target=_run_dialog, daemon=True).start()
