from Src.Logging.logger_factory import Logger_factory as logging, Logger

logging(logging.open_config("Assets/logger_config.json", False))

debug_config = logging.open_config('Assets/logger_debug.json')
group_config = logging.open_config('Assets/logger_group.json')
stream_config = logging.open_config('Assets/logger_stream.json')

logging()('main', group_config)
logging()('nodes', group_config | debug_config)
logging()('functions', group_config | debug_config)