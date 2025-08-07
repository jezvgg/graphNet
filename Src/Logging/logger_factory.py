import logging
from datetime import datetime
import json
import logging
import sys
from pathlib import Path

import dearpygui.dearpygui as dpg

from Src.Logging import Logger
from Src.Events import EventManager
from Src.Enums import EventType




class Logger_factory(object):
    '''
    Класс для логирования, синглтон.

    Attributes:
        config: dict - конфигурация для создания логгеров.
    '''
    config: dict
    __console_tag: str | int
    __stage_tag: str | int
    __layout_tag: str | int
    _instance = None
    _loggers = {}


    @classmethod
    def from_instance(cls) -> "Logger_factory":
        return cls._instance


    def __init__(self, config: dict[str, str | int] = None) -> "Logger_factory":
        '''
        Класс для логирования, синглтон.

        Args:
            config: dict - конфигурация для создания логгеров.
        '''
        if 'filename' in config:
            config['filename'] = config['filename'].format(curdata=datetime.now().strftime(config['datefmt']))

        Path.mkdir(Path(config['filename']).parent, exist_ok=True)

        self.config = config
        logging.basicConfig(**self.config)

        self.__console_tag = dpg.generate_uuid()
        self.__stage_tag = dpg.generate_uuid()

        with dpg.stage(tag=self.__stage_tag):
            with dpg.window(tag=self.__console_tag, autosize=True, \
                            pos=(dpg.get_viewport_width(), 0), \
                            no_background=True, no_collapse=True, no_move=True, no_resize=True, no_title_bar=True):
                pass

        Logger_factory._instance = self


    def __call__(self, logger_name: str, config: dict = {}) -> logging.Logger:
        '''
        Фабричный метод. При использовании будет вызываться логгер для модуля.

        Args:
            logger_name: str - название логгера для модуля.
            config: dict - конфигурация нового логгера.

        Returns:
            Logger - экземпляр логировщика
        '''
        if logger_name in Logger_factory._loggers:
            logger = Logger_factory._loggers[logger_name]
            if not config: return logger
        else:
            logger = Logger(logger_name, layout_tag=self.__console_tag)
            Logger_factory._loggers[logger_name] = logger

        config = self.config | config

        logger.propagate = False
        handler = None
        if 'filename' in config and config['filename'] == 'stream':
            handler = logging.StreamHandler(sys.stdout)
        elif 'filename' in config:
            handler = logging.FileHandler(config['filename'].format(curdata=f"{logger_name}_{datetime.now().strftime(config['datefmt'])}"))

        if 'format' in config and handler:
            handler.setFormatter(logging.Formatter(config['format']))

        if handler: logger.addHandler(handler)

        if 'level' in config:
            logger.setLevel(config['level'])

        return logger


    def show(self, parent: str | int):
        '''
        Установить окно, в котором будет отображаться логи. (Справа сверху)

        Args:
            parent_window: str | int - индетификатор родительского окна
        '''
        dpg.show_item(self.__console_tag)
        EventManager.add(EventType.VISIBLE, parent, lambda *_: self.resize())


    def hide(self):
        '''
        Скрыть окно логов.
        '''
        dpg.hide_item(self.__console_tag)


    def resize(self):
        '''
        Переместить консоль в верхний правый угол
        '''
        dpg.set_item_pos(self.__console_tag, (dpg.get_viewport_width() - dpg.get_item_width(self.__console_tag), 0))