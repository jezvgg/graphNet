import json
import logging
from pathlib import Path
import dearpygui.dearpygui as dpg

from Src.Utils.serialization.serializers import serialize_project
from Src.Utils.serialization.deserializers import deserialize_node



logger = logging.getLogger(__name__)

class ProjectManager:
    def __init__(self, node_editor_tag: str, builder, start_nodes: list, link_callback=None):
        self.node_editor_tag = node_editor_tag
        self.builder = builder
        self.start_nodes = start_nodes
        self.link_callback = link_callback

    def save_project(self, filepath: Path | str):
        try:
            project_data = serialize_project(self.start_nodes)
            with open(filepath, 'w', encoding="utf-8") as f:
                json.dump(project_data, f)
            logger.info("Проект сохранен в ", filepath)
        except Exception as e:
            logger.error("Ошибка при сохранении проекта ", e)
