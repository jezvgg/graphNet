from dataclasses import dataclass, field
from typing import Callable, Any
import inspect

from Src.Config.parameter import Parameter
from Src.Config.Annotations import ANode
from Src.Enums import AttrType


class NodeAnnotation:
    label: str
    node_type: type
    logic: Callable
    annotations: dict[str, Parameter]
    docs: str = None
    input: Parameter | bool
    output: Parameter | bool


    def __init__(self, label: str, node_type: type, logic: Callable, 
                 annotations: dict[str, Parameter] = {}, docs: str = None, 
                 input: bool = Any, output: bool = None):
        self.label = label
        self.node_type = node_type
        self.logic = logic
        self.annotations = annotations

        self.docs = docs
        if not self.docs: self.docs = inspect.getdoc(self.logic)

        self.input = input
        if self.input: 
            self.input = Parameter(AttrType.INPUT, ANode[input])
            self.annotations['INPUT'] = self.input

        self.output = output
        if self.output == None: self.output = node_type
        if self.output: self.output = Parameter(AttrType.OUTPUT, ANode[self.output])


    @property
    def kwargs(self):
        return {'annotations': self.annotations,
                'logic': self.logic,
                'docs': self.docs}


