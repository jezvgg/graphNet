from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

from Src.Enums import ExtensionStatus

@dataclass
class Extension:
    path: Path
    name: str = field(init=False)
    status: ExtensionStatus = field(default=ExtensionStatus.ERROR, init=False)
    module: Any = field(default=None, init=False)

    def __post_init__(self):
        self.name = self.path.name
        has_init = (self.path / "__init__.py").exists()
        has_config = (self.path / "extension_config.py").exists()
        if has_init and has_config:
            self.status = ExtensionStatus.DISCOVERED