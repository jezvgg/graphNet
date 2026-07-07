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
from Src.Logging import logging, Logger


class ExtensionManager:


    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.extensions_dir = self.base_dir / 'Extensions'

        self.extensions: list[Extension] = []

        self.logger: Logger = logging()("extensions")

        self.__prepare_infrastructure()


    def __prepare_infrastructure(self):
        self.extensions_dir.mkdir(parents=True, exist_ok=True)
        if str(self.base_dir) not in sys.path:
            sys.path.insert(0, str(self.base_dir))
        self.logger.info(f"Инфраструктура расширений подготовлена: {self.extensions_dir}")


    def __import_extension(self, extension: Extension):
        self.logger.info(f"Импорт расширения: {extension.name}")
        plugin_module = importlib.import_module(f"Extensions.{extension.name}.extension_config")
            
        if not hasattr(plugin_module, "ExtensionList"):
            self.logger.warning(f"Расширение '{extension.name}' не содержит ExtensionList")
            return

        if not (
            valid_nodes := [
                node for node in getattr(plugin_module, "ExtensionList")
                if inspect.isclass(node) and issubclass(node, AbstractNode)
            ]
        ):
            self.logger.warning(f"Расширение '{extension.name}' не содержит валидных узлов")
            return

        node_list.setdefault("Plugins", []).extend(valid_nodes)
        
        extension.module = plugin_module
        extension.status = ExtensionStatus.LOADED
        self.logger.info(f"Расширение '{extension.name}' успешно загружено. Узлов: {len(valid_nodes)}")


    def discover_extensions(self) -> list[Extension]:
        self.extensions.clear()
        self.logger.info("Поиск расширений...")
        
        candidates = (p for p in self.extensions_dir.iterdir() if p.is_dir() and p.name.startswith('ext_'))
        
        for path in candidates:
            ext = Extension(path)
            self.extensions.append(ext)

            if ext.status == ExtensionStatus.DISCOVERED:
                self.logger.info(f"Обнаружено расширение: {ext.name}")
            else:
                self.logger.warning(f"Расширение '{path.name}' не прошло валидацию структуры")
                
        self.logger.info(f"Найдено расширений: {len(self.extensions)}")
        return self.extensions

    def load_active_extensions(self, extensions_to_load: list[Extension] = None):
        if extensions_to_load is None:
            extensions_to_load = [
                ext for ext in self.extensions 
                if ext.status == ExtensionStatus.DISCOVERED
            ]
        self.logger.info(f"Загрузка расширений: {len(extensions_to_load)} шт.")
        for extension in extensions_to_load:
            self.__import_extension(extension)

            
    def install_from_zip(self, zip_path: Path, overwrite: bool = False) -> Extension:
        self.logger.info(f"Установка расширения из архива: {zip_path}")
        target_dir = self.extensions_dir / (zip_path.stem if zip_path.stem.startswith("ext_") else f"ext_{zip_path.stem}")

        if target_dir.exists() and not overwrite:
            self.logger.error(f"Расширение '{target_dir.name}' уже установлено")
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
            self.logger.error(f"Неверная структура расширения: {target_dir.name}")
            raise ValueError("Неверная структура расширения. Отсутствуют обязательные файлы.")

        self.extensions.append(extension)
        self.logger.info(f"Расширение '{extension.name}' успешно установлено из архива")
        return extension