from enum import Enum




class CallbackType(Enum):
    """Типы отслеживаемых изменений элементов интерфейса."""
    VALUE = "value"
    STATE = "state"