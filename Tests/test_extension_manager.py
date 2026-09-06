import sys
import zipfile
import pytest
from pathlib import Path
from unittest.mock import patch

from Src.Managers.extension_manager import ExtensionManager
from Src.Enums import ExtensionStatus

@pytest.fixture
def manager(tmp_path):
    mgr = ExtensionManager()
    mgr.base_dir = tmp_path
    mgr.extensions_dir = tmp_path / "Extensions"
    mgr.extensions_dir.mkdir(parents=True, exist_ok=True)
    return mgr

def test_discover_extensions(manager, tmp_path):
    ext_dir = manager.extensions_dir / "valid_ext"
    ext_dir.mkdir()
    (ext_dir / "__init__.py").touch()
    (ext_dir / "extension_config.py").touch()

    invalid_dir = manager.extensions_dir / "invalid_ext"
    invalid_dir.mkdir()
    (invalid_dir / "random.py").touch()

    exts = manager.discover_extensions()
    
    assert len(exts) == 2
    
    valid_ext = next(e for e in exts if e.name == "valid_ext")
    assert valid_ext.status == ExtensionStatus.DISCOVERED

    invalid_ext = next(e for e in exts if e.name == "invalid_ext")
    assert invalid_ext.status == ExtensionStatus.ERROR


def test_install_from_zip(manager, tmp_path):
    zip_path = tmp_path / "test_ext.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("test_ext/__init__.py", "print('init')")
        zf.writestr("test_ext/extension_config.py", "EXTENSION_CONFIG = {}")

    ext = manager.install_from_zip(zip_path)
    
    assert ext is not None
    assert ext.name == "test_ext"
    assert ext.status == ExtensionStatus.DISCOVERED
    assert (manager.extensions_dir / "test_ext").exists()


def test_install_from_zip_invalid(manager, tmp_path):
    zip_path = tmp_path / "bad_ext.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("bad_ext/random.py", "print('bad')")

    ext = manager.install_from_zip(zip_path)
    
    assert ext is None
    assert not (manager.extensions_dir / "bad_ext").exists()
