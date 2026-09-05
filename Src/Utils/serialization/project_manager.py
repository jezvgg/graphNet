import json
from pathlib import Path
from typing import TypedDict, List, Any
import dearpygui.dearpygui as dpg

from Src.Utils.serialization.serializers import ProjectEncoder
from Src.Utils.serialization.deserializers import ProjectDecoder
from Src.Utils import get_userdata, clear_userdata
from Src.Enums.dpg_types import DPGType
from Src.Nodes.abstract_node import AbstractNode
from Src.Config.node_annotation import NodeAnnotation
from Src.node_builder import NodeBuilder
from Src.Logging.logger_factory import Logger_factory


logger = Logger_factory()(__name__)


class LinkData(TypedDict):
    sender_node_id: str
    sender_pin: str
    receiver_node_id: str
    receiver_pin: str


class ProjectData(TypedDict):
    nodes: List[Any]
    links: List[LinkData]


class ProjectManager:
    def __init__(self, node_editor_tag: str, builder: NodeBuilder, start_nodes: list, link_callback=None):
        self.node_editor_tag = node_editor_tag
        self.builder = builder
        self.start_nodes = start_nodes
        self.link_callback = link_callback
        self._node_data_by_label: dict[str, NodeAnnotation] | None = None


    def save_project(self, filepath: str | Path):
        """
        Собирает состояние текущего холста (узлы и связи) и сохраняет его в JSON-файл.
        """
        data = self._collect_project_data()

        with open(filepath, 'w', encoding="utf-8") as f:
            json.dump(data, f, cls=ProjectEncoder, indent=4)

        logger.info(f"Проект успешно сохранен в {filepath}")


    def _collect_project_data(self) -> ProjectData:
        """
        Обходит холст редактора узлов и превращает его в JSON-совместимую структуру,
        подменяя динамические UUID узлов на стабильные строковые id.
        """
        node_tags = dpg.get_item_children(self.node_editor_tag, slot=1) or []
        node_tag_to_id = {node_tag: f"node_{i}" for i, node_tag in enumerate(node_tags)}

        encoder = ProjectEncoder()
        serialized_nodes = []
        serialized_links = []

        for node_tag in node_tags:
            node: AbstractNode = get_userdata(node_tag)

            node_dict = node.to_dict(encoder.serialize)
            node_dict["id"] = node_tag_to_id[node_tag]
            serialized_nodes.append(node_dict)

            for attr_incoming, attr_outgoing_list in node.incoming.items():
                receiver_pin_label = dpg.get_item_label(attr_incoming)

                for attr_outgoing in attr_outgoing_list:
                    sender_node_tag = dpg.get_item_parent(attr_outgoing)
                    if sender_node_tag not in node_tag_to_id:
                        continue

                    serialized_links.append({
                        "sender_node_id": node_tag_to_id[sender_node_tag],
                        "sender_pin": dpg.get_item_label(attr_outgoing),
                        "receiver_node_id": node_tag_to_id[node_tag],
                        "receiver_pin": receiver_pin_label,
                    })

        return {
            "nodes": serialized_nodes,
            "links": serialized_links,
        }


    def clear_board(self, recreate_input: bool = False):
        """
        Очищает холст редактора узлов перед загрузкой нового проекта.
        """
        if not (children := dpg.get_item_children(self.node_editor_tag, slot=1)):
            return

        for item in children:
            if dpg.does_item_exist(item):
                clear_userdata(item)
                dpg.delete_item(item)

        # Очищаем внутренний список узлов
        self.start_nodes.clear()
        logger.debug("Рабочая область очищена.")

        if recreate_input and self.builder:
            input_id = self.builder.build_input(self.node_editor_tag)
            self.start_nodes.append(get_userdata(input_id))


    def _get_node_data_by_label(self, label: str) -> NodeAnnotation | None:
        """
        Ищет NodeAnnotation узла по его лейблу среди доступных типов узлов (self.builder.node_list).

        Лейбл используется вместо сериализации самого NodeAnnotation (он содержит колбэки и
        типы, которые невозможно восстановить из JSON), что также даёт обратную совместимость:
        если тип узла с сохранённым лейблом был удалён из приложения, мы можем аккуратно
        пропустить его вместо падения.
        """
        if self._node_data_by_label is None:
            self._node_data_by_label = {
                node.label: node
                for category in self.builder.node_list.values()
                for subcategory in category.values()
                for node in subcategory
            }

        return self._node_data_by_label.get(label)


    def _find_attribute_by_label(self, node_id: int | str, pin_label: str):
        """Ищет ID атрибута (пина) внутри узла по его имени."""
        if not (children := dpg.get_item_children(node_id, slot=1)):
            return None

        for attr in children:
            if DPGType(attr) == DPGType.NODE_ATTRIBUTE and dpg.get_item_label(attr) == pin_label:
                return attr
        return None


    def load_project(self, filepath: Path | str):
        """
        Очищает текущий граф, читает JSON и воссоздает узлы и связи.
        """
        with open(filepath, 'r', encoding="utf-8") as f:
            project_data: ProjectData = json.load(f)

        self.clear_board(recreate_input=False)
        id_mapping = {}

        for node_info in project_data.get("nodes", []):
            node_label = node_info.get("label")
            if not node_label:
                continue

            if node_label == "Input":
                new_node_id = self.builder.build_input(parent=self.node_editor_tag)
            else:
                node_data = self._get_node_data_by_label(node_label)
                if not node_data:
                    logger.error(f"Неизвестный тип узла: {node_label}")
                    continue
                new_node_id = self.builder.build_node(node_data, parent=self.node_editor_tag)

            new_node = get_userdata(new_node_id)

            if not ProjectDecoder.deserialize_node(new_node, node_info):
                logger.warning(f"Не удалось полностью десериализовать параметры узла: {node_label}")

            id_mapping[node_info["id"]] = new_node_id
            self.start_nodes.append(new_node)

        for link_info in project_data.get("links", []):
            sender_old_id = link_info.get("sender_node_id")
            receiver_old_id = link_info.get("receiver_node_id")

            if sender_old_id not in id_mapping or receiver_old_id not in id_mapping:
                logger.warning("Невозможно восстановить связь")
                continue

            sender_attr = self._find_attribute_by_label(id_mapping[sender_old_id], link_info.get("sender_pin"))
            receiver_attr = self._find_attribute_by_label(id_mapping[receiver_old_id], link_info.get("receiver_pin"))

            if not (sender_attr and receiver_attr):
                logger.warning("Невозможно восстановить связь: не найден пин узла")
                continue

            if self.link_callback:
                # link_callback сам создаёт dpg.node_link и обновляет incoming/outgoing узлов,
                # поэтому здесь не нужно (и нельзя) создавать связь ещё раз вручную.
                self.link_callback(self.node_editor_tag, (sender_attr, receiver_attr))
            else:
                dpg.add_node_link(sender_attr, receiver_attr, parent=self.node_editor_tag)

        logger.info(f"Проект успешно загружен из {filepath}")
