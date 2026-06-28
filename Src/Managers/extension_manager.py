import sys
import importlib
import inspect
import zipfile        
import shutil
from pathlib import Path
from typing import Any

from Src.Nodes import AbstractNode
from Src.Config.node_list import node_list
from Src.Enums import ExtensionStatus
from Src.Managers.extension import Extension 


class ExtensionManager:


    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.extensions_dir = self.base_dir / 'Extensions'

        self.discovered_extensions: list[Extension] = [] 
        self.active_extensions: dict[str, Any] = {}

        self.__prepare_infrastructure()


    def __prepare_infrastructure(self):
        self.extensions_dir.mkdir(parents=True, exist_ok=True)
        if str(self.base_dir) not in sys.path:
            sys.path.insert(0, str(self.base_dir))


    def __is_valid_node(self, node_class) -> bool:
        return inspect.isclass(node_class) and issubclass(node_class, AbstractNode)


    def __import_extension(self, extension: Extension):
        plugin_module = importlib.import_module(f"Extensions.{extension.name}.extension_config")
            
        if not hasattr(plugin_module, "ExtensionList"):
            return

        if not (
            valid_nodes := [node for node in getattr(plugin_module, "ExtensionList") if self.__is_valid_node(node)]
        ):
            return

        node_list.setdefault("Plugins", []).extend(valid_nodes)
        
        self.active_extensions[extension.name] = plugin_module
        extension.module = plugin_module
        extension.status = ExtensionStatus.LOADED


    def discover_extensions(self) -> list[Extension]:
        self.discovered_extensions.clear()
        
        candidates = (p for p in self.extensions_dir.iterdir() if p.is_dir() and p.name.startswith('ext_'))
        
        for path in candidates:
            ext = Extension(path)
            
            if ext.status == ExtensionStatus.DISCOVERED:
                self.discovered_extensions.append(ext)
                
        return self.discovered_extensions

    def load_active_extensions(self, extensions_to_load: list[Extension]):
        for extension in extensions_to_load:
            self.__import_extension(extension)

            
    def install_from_zip(self, zip_path: Path, overwrite: bool = False) -> Extension:
        target_dir = self.extensions_dir / (zip_path.stem if zip_path.stem.startswith("ext_") else f"ext_{zip_path.stem}")

        if target_dir.exists() and not overwrite:
            raise FileExistsError(f"Расширение '{target_dir.name}' уже установлено.")
        
        shutil.rmtree(target_dir, ignore_errors=True)

        temp_dir = self.extensions_dir / f"temp_{zip_path.stem}"
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(temp_dir)

        items = list(temp_dir.iterdir())
        source_root = items[0] if len(items) == 1 and items[0].is_dir() else temp_dir
        shutil.move(str(source_root), str(target_dir))
        shutil.rmtree(temp_dir, ignore_errors=True)

        extension = Extension(target_dir)
        if extension.status != ExtensionStatus.DISCOVERED:
            shutil.rmtree(target_dir, ignore_errors=True)
            raise ValueError("Неверная структура расширения. Отсутствуют обязательные файлы.")

        self.discovered_extensions.append(extension)
        return extension