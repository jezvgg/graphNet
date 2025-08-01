from dataclasses import dataclass, field
from typing import Callable
import inspect

from Src.Config.parameter import Parameter


@dataclass
class NodeAnnotation:
    label: str
    node_type: type
    logic: Callable
    annotations: dict[str, Parameter] = field(default_factory=dict)
    docs: str = None
    input: bool = True
    output: bool = True


    def __post_init__(self):
        if not self.docs: self.docs = inspect.getdoc(self.logic)


    @property
    def kwargs(self):
        return {'annotations': self.annotations,
                'logic': self.logic,
                'docs': self.docs,
                'input': self.input,
                'output': self.output}


