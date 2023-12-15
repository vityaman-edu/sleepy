from dataclasses import dataclass

from .bindings import Bindings
from .representation import Program


@dataclass
class ProgramUnit:
    program: Program
    bindings: Bindings
