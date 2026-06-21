import sys
import importlib
import inspect
from pathlib import Path

from Src.Nodes import AbstractNode
from Src.Config.node_list import node_list

class ExtensionManager:

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.extensions_dir = self.base_dir / 'Extensions'

        self.discovered_plugins = {}
        self.active_plugins = {}

        self._prepare_infrastructure()

    def _prepare_infrastructure(self):
        self.extensions_dir.mkdir(parents=True, exist_ok=True)
            
        if str(self.base_dir) not in sys.path:
            sys.path.insert(0, str(self.base_dir))

    def discover_extensions(self):
        self.discovered_plugins.clear()
        
        candidates = (p for p in self.extensions_dir.iterdir() if p.is_dir() and not p.name.startswith('__'))

        for path in candidates:
            if not self._validate_structure(path):
                continue
            
            self.discovered_plugins[path.name] = {"path": path, "status": "discovered"}

    def _validate_structure(self, plugin_path: Path) -> bool:
        return (plugin_path / "__init__.py").exists() and (plugin_path / "extension_config.py").exists()

    def load_active_plugins(self):
        to_load = [name for name, meta in self.discovered_plugins.items() if meta["status"] == "discovered"]
        
        for plugin_name in to_load:
            self._import_plugin(plugin_name)

    def _is_valid_node(self, node_class) -> bool:
        return inspect.isclass(node_class) and issubclass(node_class, AbstractNode)

    def _import_plugin(self, plugin_name: str):
        plugin_module = importlib.import_module(f"Extensions.{plugin_name}.extension_config")
            
        if not hasattr(plugin_module, "ExtensionList"):
            return

        if not (valid_nodes := [node for node in getattr(plugin_module, "ExtensionList") if self._is_valid_node(node)]): return

        node_list.setdefault("Plugins", []).extend(valid_nodes)
            
        self.active_plugins[plugin_name] = plugin_module
        self.discovered_plugins[plugin_name]["status"] = "loaded"