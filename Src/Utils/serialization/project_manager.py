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
        """
        Собирает текущее состояние графа и сохраняет его в JSON.
        """
        try:
            project_data = serialize_project(self.start_nodes)
            with open(filepath, 'w', encoding="utf-8") as f:
                json.dump(project_data, f)
            logger.info("Проект сохранен в ", filepath)
        except Exception as e:
            logger.error("Ошибка при сохранении проекта ", e)


    def clear_board(self):
        """
        Очищает холст редактора узлов перед загрузкой нового проекта.
        """
        children = dpg.get_item_children(self.node_editor_tag)
        if children:
            for slot in children.values():
                for item in slot:
                    if dpg.does_item_exist(item):
                        dpg.delete_item(item)

        self.start_nodes.clear()
        logger.debug("Рабочая область очищена")


    def _find_attribute_by_label(self, node_id: int | str, pin_label: str):
        """Ищет ID атрибута (пина) внутри узла по его имени."""
        children = dpg.get_item_children(node_id, slot=1)
        if children:
            for attr in children:
                if dpg.get_item_type(attr) == "mvAppItemType::mvNodeAttribute":
                    if dpg.get_item_label(attr) == pin_label:
                        return attr
        return None


    