from enum import Enum, auto

class ExtensionStatus(Enum):
    DISCOVERED = auto()
    LOADED = auto()
    ERROR = auto()