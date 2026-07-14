import sys
import zipfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from graphnet_sdk import GraphNetSDK
from Src.Enums import ExtensionStatus

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))



def test_init_extension(tmp_path):
    ext_name = "test-ext"
    target_dir = tmp_path / ext_name

    with patch("pathlib.Path.cwd", return_value=tmp_path):
        GraphNetSDK.init_extension(ext_name)

        assert target_dir.exists()
        assert target_dir.is_dir()
        assert (target_dir / "__init__.py").exists()
        assert (target_dir / "extension_config.py").exists()

        init_content = (target_dir / "__init__.py").read_text(encoding="utf-8")
        assert "TestExtNode" in init_content
        assert "test-ext" in init_content

        config_content = (target_dir / "extension_config.py").read_text(encoding="utf-8")
        assert "class TestExtNode(AbstractNode):" in config_content

        GraphNetSDK.init_extension(ext_name)
        assert target_dir.exists()


def test_compile_extension(tmp_path):
    ext_name = "my_ext"
    source_dir = tmp_path / ext_name
    source_dir.mkdir()
    
    GraphNetSDK.compile_extension(str(source_dir), str(tmp_path / "output.zip"))
    assert not (tmp_path / "output.zip").exists()

    (source_dir / "__init__.py").write_text("print('hello')", encoding="utf-8")
    (source_dir / "extension_config.py").write_text("config = {}", encoding="utf-8")
    
    pycache_dir = source_dir / "__pycache__"
    pycache_dir.mkdir()
    (pycache_dir / "test.pyc").write_text("binary", encoding="utf-8")
    (source_dir / "ignore.pyc").write_text("binary", encoding="utf-8")

    zip_output = tmp_path / f"{ext_name}.zip"
    
    GraphNetSDK.compile_extension(str(source_dir), str(zip_output))
    
    assert zip_output.exists()
    
    with zipfile.ZipFile(zip_output, 'r') as zf:
        names = zf.namelist()
        assert f"{ext_name}/__init__.py" in names
        assert f"{ext_name}/extension_config.py" in names
        assert all("__pycache__" not in name for name in names)
        assert all(not name.endswith(".pyc") for name in names)


@patch("graphnet_sdk.ExtensionManager")
def test_run_extension(mock_manager_class, tmp_path):
    mock_manager = mock_manager_class.return_value
    mock_extension = MagicMock()
    mock_extension.status = ExtensionStatus.DISCOVERED
    mock_manager.install_from_zip.return_value = mock_extension

    zip_file = tmp_path / "dummy.zip"
    
    GraphNetSDK.run_extension(str(zip_file))
    mock_manager.install_from_zip.assert_not_called()

    zip_file.touch()
    GraphNetSDK.run_extension(str(zip_file), overwrite=True)
    
    mock_manager.install_from_zip.assert_called_once_with(zip_file, overwrite=True)
    mock_manager.load_active_extensions.assert_called_once_with([mock_extension])


@patch("sys.argv", ["graphnet_sdk", "init", "my_ext"])
@patch("graphnet_sdk.GraphNetSDK.init_extension")
def test_execute_init(mock_init):
    GraphNetSDK.execute()
    mock_init.assert_called_once_with("my_ext")


@patch("sys.argv", ["graphnet_sdk", "compile", "my_ext", "-o", "out.zip"])
@patch("graphnet_sdk.GraphNetSDK.compile_extension")
def test_execute_compile(mock_compile):
    GraphNetSDK.execute()
    mock_compile.assert_called_once_with("my_ext", "out.zip")


@patch("sys.argv", ["graphnet_sdk", "run", "my_ext.zip", "--overwrite"])
@patch("graphnet_sdk.GraphNetSDK.run_extension")
def test_execute_run(mock_run):
    GraphNetSDK.execute()
    mock_run.assert_called_once_with("my_ext.zip", True)
