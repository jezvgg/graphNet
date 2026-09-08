import json
from itertools import chain
from pathlib import Path
import dearpygui.dearpygui as dpg

from Src.Utils.serialization.serializers import ProjectEncoder
from Src.Utils.serialization.deserializers import ProjectDecoder
from Src.Utils import get_userdata, clear_userdata
from Src.Enums.dpg_types import DPGType
from Src.Nodes.abstract_node import AbstractNode
from Src.node_builder import NodeBuilder
from Src.Logging.logger_factory import Logger_factory


logger = Logger_factory()(__name__)


class ProjectManager:
    def __init__(self, node_editor_tag: str, builder: NodeBuilder, start_nodes: list, link_callback=None):
        self.node_editor_tag = node_editor_tag
        self.builder = builder
        self.start_nodes = start_nodes
        self.link_callback = link_callback


    def save_project(self, filepath: str | Path):
        """
        Собирает узлы холста обходом в ширину и сохраняет их список в JSON-файл.
        Связи не хранятся отдельно — каждый узел несёт свои входящие связи внутри себя.
        """
        nodes = self._ordered_nodes()
        node_ids = {node.node_tag: f"node_{i}" for i, node in enumerate(nodes)}
        serialize_value = ProjectEncoder().serialize

        serialized = [self._serialize_node(node, node_ids, serialize_value) for node in nodes]

        with open(filepath, 'w', encoding="utf-8") as f:
            json.dump(serialized, f, cls=ProjectEncoder, indent=4)

        logger.info(f"Проект успешно сохранён в {filepath}")


    def _ordered_nodes(self) -> list[AbstractNode]:
        """
        Узлы в порядке обхода в ширину от стартовых. Такой порядок гарантирует, что при
        десериализации отправитель любой связи уже создан. Несвязанные узлы дописываются в конец.
        """
        ordered, seen = [], set()
        queue = list(self.start_nodes)

        while queue:
            node = queue.pop(0)
            if node is None or node.node_tag in seen: continue
            seen.add(node.node_tag)
            ordered.append(node)

            for attr_id in chain.from_iterable(node.outgoing.values()):
                queue.append(get_userdata(dpg.get_item_parent(attr_id)))

        for node_tag in dpg.get_item_children(self.node_editor_tag, slot=1) or []:
            if node_tag not in seen:
                seen.add(node_tag)
                ordered.append(get_userdata(node_tag))

        return ordered


    def _serialize_node(self, node: AbstractNode, node_ids: dict, serialize_value) -> dict:
        """Дополняет node.to_dict() стабильным id, группой/подгруппой и списком входящих связей."""
        data = node.to_dict(serialize_value)
        data["id"] = node_ids[node.node_tag]
        data["group"], data["subgroup"] = self._locate(node)
        data["inputs"] = [
            {
                "sender": node_ids[dpg.get_item_parent(sender_attr)],
                "sender_pin": dpg.get_item_label(sender_attr),
                "receiver_pin": dpg.get_item_label(receiver_attr),
            }
            for receiver_attr, senders in node.incoming.items()
            for sender_attr in senders
            if dpg.get_item_parent(sender_attr) in node_ids
        ]
        return data


    def _locate(self, node: AbstractNode) -> tuple[str | None, str | None]:
        """Группа и подгруппа узла в текущем node_list (поиск по объекту node_data, затем по лейблу)."""
        target = getattr(node, "node_data", None)
        label = dpg.get_item_label(node.node_tag)

        for group, subgroups in self.builder.node_list.items():
            for subgroup, annotations in subgroups.items():
                for annotation in annotations:
                    if annotation is target or annotation.label == label:
                        return group, subgroup

        return None, None


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
        Очищает текущий граф и восстанавливает узлы и связи из JSON.

        Десериализация идёт через json.load(object_hook=...): хук — это замыкание,
        которое захватывает builder, node_list и уже построенные узлы, а на вход получает
        только очередной JSON-объект. Узлы в файле лежат в порядке обхода в ширину,
        поэтому отправитель любой связи к моменту её восстановления уже создан.
        """
        self.clear_board(recreate_input=False)
        built: dict[str, str | int] = {}

        def rebuild(obj: dict):
            if obj.get("__type__") != "node":
                return obj

            annotation = self._annotation_for(obj)
            if annotation is None:
                logger.error(f"Неизвестный тип узла: {obj.get('label')}")
                return obj

            node_id = self.builder.build_node(annotation, parent=self.node_editor_tag)
            node = get_userdata(node_id)

            if "position" in obj: dpg.set_item_pos(node_id, obj["position"])
            self._apply_parameters(node, obj.get("parameters", {}))

            built[obj["id"]] = node_id
            for link in obj.get("inputs", []):
                self._restore_link(built, node_id, link)

            self.start_nodes.append(node)
            return obj

        with open(filepath, 'r', encoding="utf-8") as f:
            json.load(f, object_hook=rebuild)

        logger.info(f"Проект успешно загружен из {filepath}")


    def _annotation_for(self, obj: dict):
        """NodeAnnotation напрямую из текущего node_list по сохранённым группе, подгруппе и лейблу."""
        subgroups = self.builder.node_list.get(obj.get("group"), {})
        for annotation in subgroups.get(obj.get("subgroup"), []):
            if annotation.label == obj.get("label"):
                return annotation
        return None


    def _apply_parameters(self, node: AbstractNode, parameters: dict):
        """Заполняет параметры воссозданного узла сохранёнными значениями."""
        for argument in dpg.get_item_children(node.node_tag, slot=1) or []:
            name = dpg.get_item_label(argument)
            if name not in node.annotations or name not in parameters: continue

            parameter = node.annotations[name]
            value = ProjectDecoder.deserialize_value(parameter.hint, parameters[name])
            parameter.set_value(argument, value)


    def _restore_link(self, built: dict, receiver_id: str | int, link: dict):
        """Восстанавливает одну входящую связь узла по описанию из его поля inputs."""
        sender_id = built.get(link["sender"])
        if sender_id is None:
            logger.warning("Невозможно восстановить связь: отправитель ещё не создан")
            return

        sender_attr = self._find_attribute_by_label(sender_id, link["sender_pin"])
        receiver_attr = self._find_attribute_by_label(receiver_id, link["receiver_pin"])
        if not (sender_attr and receiver_attr):
            logger.warning("Невозможно восстановить связь: не найден пин узла")
            return

        if self.link_callback:
            # link_callback сам создаёт dpg.node_link и обновляет incoming/outgoing узлов.
            self.link_callback(self.node_editor_tag, (sender_attr, receiver_attr))
        else:
            dpg.add_node_link(sender_attr, receiver_attr, parent=self.node_editor_tag)
