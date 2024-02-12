from dataclasses import dataclass, field


@dataclass(repr=False)
class Node:
    note: str = field(default="", init=False)
