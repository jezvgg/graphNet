import logging
from datetime import datetime
import json
import logging
import sys


class Logger:
    '''
    Класс для логирования, синглтон.

    Attributes:
        config: dict - конфигурация для создания логгеров.
    '''
    config: dict


    def __init__(self, config: dict[str, str|int]) -> "Logger":
        '''
        Класс для логирования, синглтон.

        Args:
            config: dict - конфигурация для создания логгеров.
        '''
        if 'filename' in config: 
            config['filename'] = config['filename'].format(curdata=datetime.now().strftime(config['datefmt']))

        self.config = config
        logging.basicConfig(**self.config)


    def __new__(cls, config: dict[str, str|int] = None) -> "Logger":
        '''
        Создаём синглтон. Если config не передаётся, то возращается старый экземпляр класса, иначе конфиг заменяется.
        '''
        if not hasattr(cls, 'instance'): 
            setattr(cls, 'instance', super(Logger, cls).__new__(cls))
        return getattr(cls, 'instance')



    def __call__(self, logger_name: str, config: dict = {}) -> logging.Logger:
        '''
        Фабричный метод. При использовании будет вызываться логгер для модуля.

        Args:
            logger_name: str - название логгера для модуля.
            config: dict - конфигурация нового логгера.

        Returns:
            logging.Logger - экземпляр логировщика
        '''
        config = self.config | config
        logger = logging.getLogger(logger_name)
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
    

with open("Src/Logging/logger_config.json") as f:
    config = json.load(f)

logger = Logger(config)