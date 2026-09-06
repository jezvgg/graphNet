import sys
import importlib
import inspect
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