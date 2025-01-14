import json
from Src.Logging import logger

with open("Src/Logging/logger_config_debug.json") as f:
    config = json.load(f)
logger = logger("nodes", config)

from Src.Nodes.node import Node, node_link
from Src.Nodes.node_editor import node_editor, NodeEditor