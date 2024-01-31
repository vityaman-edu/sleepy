from .bindings import BasicBindings
from .namespace import LocalNamespace
from .representation import Intrinsic, Kind, Parameter, Symbol

intrinsic_sum = Intrinsic(
    Symbol("sum"),
    [
        Parameter(Symbol("a"), Kind("int")),
        Parameter(Symbol("b"), Kind("int")),
    ],
    Kind("int"),
)

intrinsic_div = Intrinsic(
    Symbol("div"),
    [
        Parameter(Symbol("a"), Kind("int")),
        Parameter(Symbol("b"), Kind("int")),
    ],
    Kind("int"),
)

intrinsic_rem = Intrinsic(
    Symbol("rem"),
    [
        Parameter(Symbol("a"), Kind("int")),
        Parameter(Symbol("b"), Kind("int")),
    ],
    Kind("int"),
)

intrinsic_eq = Intrinsic(
    Symbol("eq"),
    [
        Parameter(Symbol("a"), Kind("int")),
        Parameter(Symbol("b"), Kind("int")),
    ],
    Kind("bool"),
)

intrinsic_lt = Intrinsic(
    Symbol("lt"),
    [
        Parameter(Symbol("a"), Kind("int")),
        Parameter(Symbol("b"), Kind("int")),
    ],
    Kind("bool"),
)

intrinsic_not = Intrinsic(
    Symbol("not"),
    [Parameter(Symbol("a"), Kind("bool"))],
    Kind("bool"),
)

intrinsic_or = Intrinsic(
    Symbol("or"),
    [
        Parameter(Symbol("a"), Kind("bool")),
        Parameter(Symbol("b"), Kind("bool")),
    ],
    Kind("bool"),
)

intrinsic_and = Intrinsic(
    Symbol("and"),
    [
        Parameter(Symbol("a"), Kind("bool")),
        Parameter(Symbol("b"), Kind("bool")),
    ],
    Kind("bool"),
)

intrinsics = [
    intrinsic_sum,
    intrinsic_div,
    intrinsic_rem,
    intrinsic_eq,
    intrinsic_lt,
    intrinsic_not,
    intrinsic_and,
    intrinsic_or,
]


class BuiltinLayer:
    def __init__(self) -> None:
        self.namespace = LocalNamespace()
        self.bindings = BasicBindings()
        for intrinsic in intrinsics:
            self.bindings.bind(
                self.namespace.define(intrinsic.name),
                intrinsic,
            )
