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
    base_dir: Path
    extensions_dir: Path
    extensions: list[Extension]
    logger: Logger

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.extensions_dir = self.base_dir / 'Extensions'
        self.extensions = []
        self.logger = logging()("extensions")

        self.extensions_dir.mkdir(parents=True, exist_ok=True)
        if str(self.base_dir) not in sys.path:
            sys.path.insert(0, str(self.base_dir))
        self.logger.info(f"Инфраструктура расширений подготовлена: {self.extensions_dir}")


    def __import_extension(self, extension: Extension):
        self.logger.info(f"Импорт расширения: {extension.name}")
        plugin_module = importlib.import_module(f"Extensions.{extension.name}")
            
        if not hasattr(plugin_module, "EXTENSION_CONFIG"):
            self.logger.error(f"Расширение '{extension.name}' не содержит EXTENSION_CONFIG")
            return

        extension_config = getattr(plugin_module, "EXTENSION_CONFIG")
        
        plugins = node_list.setdefault("Plugins", {})
        for category, nodes in extension_config.items():
            plugins.setdefault(category, []).extend(nodes)
        
        extension.module = plugin_module
        extension.status = ExtensionStatus.LOADED
        self.logger.info(f"Расширение '{extension.name}' успешно загружено.")


    def discover_extensions(self, folder: str = "Extensions") -> list[Extension]:
        self.extensions.clear()
        self.logger.info("Поиск расширений...")
        
        extensions_dir = self.base_dir / folder
        extensions_dir.mkdir(parents=True, exist_ok=True)
        
        candidates = (p for p in extensions_dir.iterdir() if p.is_dir())
        
        for path in candidates:
            ext = Extension(path)
            self.extensions.append(ext)

            if ext.status != ExtensionStatus.DISCOVERED:
                self.logger.warning(f"Расширение '{path.name}' не прошло валидацию структуры")
                continue
            self.logger.info(f"Обнаружено расширение: {ext.name}")
                
        self.logger.info(f"Найдено расширений: {len(self.extensions)}")
        return self.extensions

    def load_active_extensions(self, exts: list[Extension] = None):
        if exts is None:
            exts = [
                ext for ext in self.extensions 
                if ext.status == ExtensionStatus.DISCOVERED
            ]
        self.logger.info(f"Загрузка расширений: {len(exts)} шт.")
        list(map(self.__import_extension, exts))

            
    def install_from_zip(self, zip_path: Path, overwrite: bool = False) -> Extension:
        self.logger.info(f"Установка расширения из архива: {zip_path}")
        target_dir = self.extensions_dir / zip_path.stem

        if target_dir.exists() and not overwrite:
            self.logger.error(f"Расширение '{target_dir.name}' уже установлено")
            return
        
        shutil.rmtree(target_dir, ignore_errors=True)

        temp_dir = self.extensions_dir / f"temp_{zip_path.stem}"
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(temp_dir)

        items = list(temp_dir.iterdir())
        source_root = items[0] if len(items) == 1 and items[0].is_dir() else temp_dir
        shutil.move(str(source_root), str(target_dir))
        shutil.rmtree(temp_dir, ignore_errors=True)

        exts = self.discover_extensions()
        for ext in exts:
            if ext.path != target_dir:
                continue
                
            if ext.status != ExtensionStatus.DISCOVERED:
                shutil.rmtree(target_dir, ignore_errors=True)
                self.logger.error(f"Неверная структура расширения: {target_dir.name}")
                return
                
            self.logger.info(f"Расширение '{ext.name}' успешно установлено из архива")
            return ext

        shutil.rmtree(target_dir, ignore_errors=True)
        self.logger.error("Неверная структура расширения. Отсутствуют обязательные файлы.")
        return