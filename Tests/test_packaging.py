import importlib
import json
import os
from pathlib import Path
import subprocess
import sys

import dearpygui.dearpygui as dpg
import pytest

from Src.resources import resource_path


@pytest.mark.parametrize("filename", [
    "themes.json", "logger_config.json", "logger_debug.json",
    "logger_group.json", "logger_stream.json", "notomono-regular.ttf",
])
def test_resources_do_not_depend_on_working_directory(tmp_path, monkeypatch, filename):
    monkeypatch.chdir(tmp_path)
    path = resource_path(filename)
    assert path.is_file()
    if path.suffix == ".json":
        assert isinstance(json.loads(path.read_text(encoding="utf-8")), dict)
    else:
        assert path.stat().st_size > 0


def test_importing_entry_point_does_not_create_gui(monkeypatch):
    def unexpected_context():
        pytest.fail("Importing the entry point must not open the GUI")
    monkeypatch.setattr(dpg, "create_context", unexpected_context)
    module = importlib.import_module("Src.application")
    importlib.reload(module)
    assert callable(module.main)


def test_logging_uses_user_directory_outside_checkout(tmp_path):
    root = Path(__file__).resolve().parents[1]
    log_directory = tmp_path / "nested" / "logs"
    env = os.environ | {"PYTHONPATH": str(root), "GRAPHNET_LOG_DIR": str(log_directory)}
    script = (
        "from Src.Logging import config, logging; "
        "from pathlib import Path; "
        "assert Path(config['filename']).parent == Path(__import__('os').environ['GRAPHNET_LOG_DIR']); "
        "logging()('main').warning('packaging-check')"
    )
    subprocess.run([sys.executable, "-c", script], cwd=tmp_path, env=env,
                   capture_output=True, text=True, check=True)
    assert any("packaging-check" in p.read_text() for p in log_directory.glob("*.log"))
    assert not (tmp_path / "Logs").exists()
