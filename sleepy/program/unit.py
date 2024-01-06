from dataclasses import dataclass

from .bindings import Bindings
from .namespace import Namespace
from .representation import Program


@dataclass
class ProgramUnit:
    program: Program
    bindings: Bindings
    root: Namespace
