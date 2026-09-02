import os
from pathlib import Path

from Src.Logging.logger_factory import Logger_factory as logging, Logger
from Src.resources import resource_path

config = logging.open_config(resource_path("logger_config.json"), False)
log_directory = Path(os.environ.get("GRAPHNET_LOG_DIR", Path.home() / ".graphnet" / "logs")).expanduser()
log_directory.mkdir(parents=True, exist_ok=True)
config["filename"] = str(log_directory / Path(config["filename"]).name)
logging(config)

debug_config = logging.open_config(resource_path("logger_debug.json"))
group_config = logging.open_config(resource_path("logger_group.json"))
stream_config = logging.open_config(resource_path("logger_stream.json"))

logging()("main", group_config)
logging()("nodes", group_config | debug_config)
logging()("functions", group_config | debug_config)
