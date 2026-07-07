from enum import Enum, auto

class ExtensionStatus(Enum):
    DISCOVERED = auto()
    LOADED = auto()
    DISABLED = auto()
    ERROR = auto()