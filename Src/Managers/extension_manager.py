import sys
import importlib

from pathlib import Path
from Src.Logging.logger_factory import Logger_factory

class ExtensionManager:

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.extensions_dir = self.base_dir / 'Extensions'

        self.descovered_plugins = {}
        self.active_plugins = {}

        self.logger = Logger_factory.get_logger('ExtensionManager')

        self._prepare_infrastructure()


    def _prepare_infrastructure(self):

        if not self.extensions_dir.exists():
            self.extensions_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Создана базовая директория для расширений: {self.extensions_dir}")
        else:
            self.logger.info(f"Директория расширений найдена: {self.extensions_dir}")
            
        if str(self.base_dir) not in sys.path:
            sys.path.insert(0, str(self.base_dir))


    def discover_extensions(self):
        self.discovered_plugins.clear()
        
        for plugin_path in self.extensions_dir.iterdir():
            if plugin_path.is_dir() and not plugin_path.name.startswith('__'):
                if self._validate_structure(plugin_path):
                    self.discovered_plugins[plugin_path.name] = {
                        "path": plugin_path,
                        "status": "discovered"
                    }
                    self.logger.info(f"Обнаружено валидное расширение: {plugin_path.name}")
                else:
                    self.logger.warning(
                        f"Пропущена папка '{plugin_path.name}': отсутствует __init__.py или файл конфигурации."
                    )
    

    def _validate_structure(self, plugin_path: Path) -> bool:
    
        has_init = (plugin_path / "__init__.py").exists()
        has_config = (plugin_path / "extension_config.py").exists()
        return has_init and has_config
    
    def load_active_plugins(self):
      
        for plugin_name, meta in self.discovered_plugins.items():
            if meta["status"] == "discovered":
                self.logger.info(f"Подготовка к загрузке плагина {plugin_name}...")