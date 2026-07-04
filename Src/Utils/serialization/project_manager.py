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


    def load_project(self, filepath: Path | str):
        """
        Очищает текущий граф, читает JSON и воссоздает узлы и связи.
        """
        try:
            with open(filepath, 'r', encoding="utf-8"):
                project_data = json.load(f)
        except Exception as e:
            logger.error("Ошибка при чтении файла ", e)
            return
        
        self.clear_board()
        id_mapping = {}

        for node_info in project_data.get("nodes", []):
            node_label = node_info.get("label")
            if not node_label:
                continue
            
            new_node_id = self.builder.build_node(node_label, parent=self.node_editor_tag)
            new_node = dpg.get_item_user_data(new_node_id)

            deserialize_node(new_node, node_info)
            id_mapping[node_info["id"]] = new_node_id
            self.start_nodes.append(new_node)

        for link_info in project_data.get("links", []):
            sender_old_id = link_info.get("sender_node_id")
            receiver_old_id = link_info.get("receiver_node_id")
            
            if sender_old_id not in id_mapping or receiver_old_id not in id_mapping:
                logger.warning("Невозможно восстановить связь")

            sender_new_id = id_mapping[sender_old_id]
            receiver_new_id = id_mapping[receiver_old_id]

            sender_attr = self._find_attribute_by_label(sender_new_id, link_info.get("sender_pin"))
            receiver_attr = self._find_attribute_by_label(receiver_new_id, link_info.get("receiver_pin"))

            if sender_attr and receiver_attr:
                dpg.add_node_link(sender_attr, receiver_attr, parent=self.node_editor_tag)
                
                if self.link_callback:
                    self.link_callback(sender_attr, receiver_attr)
                    
        logger.info(f"Проект успешно загружен из {filepath}")
