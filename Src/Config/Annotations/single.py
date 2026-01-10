from dataclasses import dataclass



@dataclass
class Single:
    node_type: type


    def __class_getitem__(cls, item):
        return Single(item)