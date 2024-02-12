from bisect import bisect_right
from io import StringIO
from typing import override

import sleepy.tafka.representation as taf

from .walker import Context, TafkaWalker


class Usages:

    """
    Usages.

             |
       |-----|------|
       |            |
    |-----|     |-------|
    |  i  |     | j + 1 |
    | ... |     |  ...  |
    |     |     |       |
    | ... |     |  ...  |
    |  j  | ~~~ |   k   | <- ths
    |-----|     |-------|
       |             |
       |-----|-------|
             |
         |-------|
         | k + 1 | <- nxt
         |  ...  |
    """

    def __init__(self) -> None:
        self.writes: dict[str, list[int]] = {}
        self.reads: dict[str, list[int]] = {}

        self.start: dict[str, int] = {}
        self.end: dict[str, int] = {}

    def next_write(self, var: taf.Var, ctx: Context) -> int | None:
        key = repr(var)
        i = Usages.find_next(self.writes.get(key, []), ctx.position)
        if i is None:
            return None
        (ths, nxt) = self.this_and_next_position(ctx.block)
        if nxt is None or i <= ths or nxt <= i:
            return i
        return Usages.find_next(self.writes.get(key, []), nxt - 1)

    def next_read(self, var: taf.Var, ctx: Context) -> int | None:
        read = self.__next_read_naive(var, ctx)
        if read is None:
            return None

        write = self.next_write(var, ctx)
        if write is None:
            return read

        if read <= write:
            return read
        return None

    def __next_read_naive(self, var: taf.Var, ctx: Context) -> int | None:
        key = repr(var)
        i = Usages.find_next(self.reads.get(key, []), ctx.position)
        if i is None:
            return None
        (ths, nxt) = self.this_and_next_position(ctx.block)
        if nxt is None or i <= ths or nxt <= i:
            return i
        return Usages.find_next(self.reads.get(key, []), nxt - 1)

    def this_and_next_position(
        self,
        block: taf.Block,
    ) -> tuple[int, int | None]:
        ths: int = self.end[block.label.name]
        nxt: int | None
        match block.last:
            case taf.Goto(next):
                nxt = self.start[next.label.name]
            case taf.Conditional(_, then_branch, _, _):
                nxt = self.start[then_branch.label.name]
            case taf.Return():
                nxt = None
            case _:
                raise NotImplementedError
        return (ths, nxt)

    @staticmethod
    def find_next(lst: list[int], e: int) -> int | None:
        i = bisect_right(lst, e)
        if i == len(lst):
            return None
        return lst[i]

    def to_text(self, block: taf.Block) -> str:
        dumper = UsageDumper(self)
        walker = TafkaWalker(dumper)
        walker.explore_block(block)
        return dumper.text.getvalue()

    @staticmethod
    def analyzed(block: taf.Block) -> "Usages":
        collector = Usages.Collector()
        walker = TafkaWalker(collector)
        walker.explore_block(block)
        return collector.usages

    class Collector(TafkaWalker.ContextedListener):
        def __init__(self) -> None:
            super().__init__()
            self.usages = Usages()

        @override
        def enter_procedure(self, procedure: taf.Procedure) -> None:
            pass

        @override
        def exit_procedure(self, procedure: taf.Procedure) -> None:
            pass

        @override
        def enter_block(self, block: taf.Block) -> None:
            super().enter_block(block)
            self.usages.start[block.label.name] = self.position + 1

        @override
        def exit_block(self, block: taf.Block) -> None:
            self.usages.end[block.label.name] = self.position

        @override
        def exit_statement(self, statement: taf.Statement) -> None:
            pass

        @override
        def on_return(self, ret: taf.Return) -> None:
            self.read(ret.value)

        @override
        def on_goto(self, goto: taf.Goto) -> None:
            pass

        @override
        def on_conditional(self, conditional: taf.Conditional) -> None:
            self.read(conditional.condition)

        @override
        def on_invokation(
            self,
            target: taf.Var,
            source: taf.Invokation,
        ) -> None:
            self.read(source.closure)
            for argument in source.args:
                self.read(argument)
            self.write(target)

        @override
        def on_load(self, target: taf.Var, source: taf.Load) -> None:
            self.write(target)

        @override
        def on_copy(self, target: taf.Var, source: taf.Copy) -> None:
            self.read(source.argument)
            self.write(target)

        @override
        def on_sum(self, target: taf.Var, source: taf.Sum) -> None:
            self.on_binary_operation(target, source)

        @override
        def on_mul(self, target: taf.Var, source: taf.Mul) -> None:
            self.on_binary_operation(target, source)

        @override
        def on_div(self, target: taf.Var, source: taf.Div) -> None:
            self.on_binary_operation(target, source)

        @override
        def on_rem(self, target: taf.Var, source: taf.Rem) -> None:
            self.on_binary_operation(target, source)

        @override
        def on_eq(self, target: taf.Var, source: taf.Eq) -> None:
            self.on_binary_operation(target, source)

        @override
        def on_lt(self, target: taf.Var, source: taf.Lt) -> None:
            self.on_binary_operation(target, source)

        @override
        def on_and(self, target: taf.Var, source: taf.And) -> None:
            self.on_binary_operation(target, source)

        @override
        def on_or(self, target: taf.Var, source: taf.Or) -> None:
            self.on_binary_operation(target, source)

        def on_binary_operation(
            self,
            target: taf.Var,
            source: taf.BinaryOperator,
        ) -> None:
            self.read(source.left)
            self.read(source.right)
            self.write(target)

        def write(self, var: taf.Var) -> None:
            key = repr(var)
            self.usages.writes[key] = self.usages.writes.get(key, [])
            self.usages.writes[key].append(self.position)

        def read(self, var: taf.Var) -> None:
            key = repr(var)
            self.usages.reads[key] = self.usages.reads.get(key, [])
            self.usages.reads[key].append(self.position)


class UsageDumper(TafkaWalker.ContextedListener):
    def __init__(self, usages: Usages) -> None:
        super().__init__()
        self.text = StringIO()
        self.indent = 0
        self.usages = usages

    def write(self, text: str) -> None:
        self.text.write(text)

    def writeln(self, line: str) -> None:
        self.write(f"{(self.position):03d}. {'  ' * self.indent}{line}\n")

    @override
    def enter_procedure(self, procedure: taf.Procedure) -> None:
        pass

    @override
    def exit_procedure(self, procedure: taf.Procedure) -> None:
        pass

    @override
    def exit_block(self, block: taf.Block) -> None:
        pass

    @override
    def exit_statement(self, statement: taf.Statement) -> None:
        pass

    @override
    def on_return(self, ret: taf.Return) -> None:
        self.writeln_next_rw(ret.value)

    @override
    def on_goto(self, goto: taf.Goto) -> None:
        pass

    @override
    def on_conditional(self, conditional: taf.Conditional) -> None:
        self.writeln_next_rw(conditional.condition)

    @override
    def on_invokation(
        self,
        target: taf.Var,
        source: taf.Invokation,
    ) -> None:
        self.writeln_next_rw(*[target, source.closure, *source.args])

    @override
    def on_load(self, target: taf.Var, source: taf.Load) -> None:
        self.writeln_next_rw(target)

    @override
    def on_copy(self, target: taf.Var, source: taf.Copy) -> None:
        self.writeln_next_rw(target, source.argument)

    @override
    def on_sum(self, target: taf.Var, source: taf.Sum) -> None:
        self.on_binary_operation(target, source)

    @override
    def on_mul(self, target: taf.Var, source: taf.Mul) -> None:
        self.on_binary_operation(target, source)

    @override
    def on_div(self, target: taf.Var, source: taf.Div) -> None:
        self.on_binary_operation(target, source)

    @override
    def on_rem(self, target: taf.Var, source: taf.Rem) -> None:
        self.on_binary_operation(target, source)

    @override
    def on_eq(self, target: taf.Var, source: taf.Eq) -> None:
        self.on_binary_operation(target, source)

    @override
    def on_lt(self, target: taf.Var, source: taf.Lt) -> None:
        self.on_binary_operation(target, source)

    @override
    def on_and(self, target: taf.Var, source: taf.And) -> None:
        self.on_binary_operation(target, source)

    @override
    def on_or(self, target: taf.Var, source: taf.Or) -> None:
        self.on_binary_operation(target, source)

    def on_binary_operation(
        self,
        target: taf.Var,
        source: taf.BinaryOperator,
    ) -> None:
        self.writeln_next_rw(source.left, source.right, target)

    def writeln_next_rw(self, *var: taf.Var) -> None:
        self.writeln(", ".join(self.next_rw(_) for _ in var))

    def next_rw(self, var: taf.Var) -> str:
        return (
            f"%{var.name}: "
            f"r{self.usages.next_read(var, self.context) or "0"} "
            f"w{self.usages.next_write(var, self.context) or "0"}"
        )
