from typing import override

import sleepy.tafka.representation as taf
from sleepy.tafka import Context, TafkaWalker, Usages

from .argument import Immediate, Integer, Unassigned
from .argument import PhysicalRegister as PhysReg
from .argument import Register as Reg
from .argument import VirtualRegister as VirtReg
from .data import IntegerData
from .instruction import (
    Addi,
    Addim,
    Andb,
    Brn,
    Divi,
    Instruction,
    Load,
    Muli,
    Orb,
    Remi,
    Slti,
    Stor,
    Xorb,
    mov,
    movi,
)
from .memory import Memory


class VirtualRegisters:
    def __init__(self) -> None:
        self.sequence = (VirtReg(n) for n in range(10000))
        self.binded: dict[str, Reg] = {}

    def binded_to(self, var: taf.Var) -> Reg:
        var_repr = repr(var)
        if var_repr not in self.binded:
            self.binded[var_repr] = self.temporary()
        return self.binded[var_repr]

    def temporary(self) -> VirtReg:
        return next(self.sequence)


class AsmikEmitListener(TafkaWalker.ContextedListener):
    def __init__(self) -> None:
        super().__init__()

        self.memory = Memory()
        self.registers = VirtualRegisters()

        self.resolved: dict[str, int] = {}

        self.procedure: taf.Procedure
        self.usages: Usages

    @override
    def enter_procedure(self, procedure: taf.Procedure) -> None:
        super().enter_procedure(procedure)

        self.usages = Usages.analyzed(procedure)
        self.procedure = procedure

        addr = self.memory.data_put(IntegerData(self.next_instr_addr))
        self.resolved[f"${procedure.const.name}"] = addr
        for i, param in enumerate(procedure.parameters):
            register = self.registers.binded_to(param)
            self.emit(mov(register, PhysReg.arg(i + 1)))

    @override
    def exit_procedure(self, procedure: taf.Procedure) -> None:
        pass

    @override
    def enter_block(self, block: taf.Block) -> None:
        super().enter_block(block)
        self.resolved[repr(block.label)] = self.next_instr_addr

    @override
    def exit_block(self, block: taf.Block) -> None:
        pass

    @override
    def enter_statement(self, statement: taf.Statement) -> None:
        super().enter_statement(statement)

    @override
    def exit_statement(self, statement: taf.Statement) -> None:
        pass

    @override
    def on_return(self, ret: taf.Return) -> None:
        retr = self.registers.binded_to(ret.value)
        self.emit(mov(Reg.a1(), retr))
        self.emit(Brn(Reg.ze(), Reg.ra()))

    @override
    def on_goto(self, goto: taf.Goto) -> None:
        block_label = repr(goto.block.label)
        label = self.registers.temporary()
        self.emit(movi(label, Unassigned(block_label)))
        self.emit(Brn(Reg.ze(), label))

    @override
    def on_conditional(self, conditional: taf.Conditional) -> None:
        else_label = repr(conditional.else_branch.label)
        condition = self.registers.binded_to(conditional.condition)
        else_address = self.registers.temporary()
        self.emit(movi(else_address, Unassigned(else_label)))
        self.emit(Brn(condition, else_address))

    def push_context(self, variables: list[taf.Var]) -> None:
        def push(register: Reg) -> None:
            self.emit(Stor(Reg.sp(), register))
            self.emit(Addim(Reg.sp(), Reg.sp(), Integer(8)))

        for local in variables:
            if self.is_alive(local):
                push(self.registers.binded_to(local))
        push(Reg.ra())

    def pop_context(self, variables: list[taf.Var]) -> None:
        def pop(register: Reg) -> None:
            self.emit(Addim(Reg.sp(), Reg.sp(), Integer(-8)))
            self.emit(Load(register, Reg.sp()))

        pop(Reg.ra())
        for local in variables[::-1]:
            if self.is_alive(local):
                pop(self.registers.binded_to(local))

    @override
    def on_invokation(
        self,
        target: taf.Var,
        source: taf.Invokation,
    ) -> None:
        variables = list(self.procedure.locals)

        self.push_context(variables)

        for i, arg in enumerate(source.args):
            arg_reg = self.registers.binded_to(arg)
            self.emit(mov(PhysReg.arg(i + 1), arg_reg))

        proc_reg = self.registers.binded_to(source.closure)
        self.emit(Addim(Reg.ra(), Reg.ip(), Integer(4)))
        self.emit(Brn(Reg.ze(), proc_reg))

        result = self.registers.binded_to(target)
        self.emit(mov(result, Reg.a1()))

        self.pop_context(variables)

    @override
    def on_load(self, target: taf.Var, source: taf.Load) -> None:
        dst = self.registers.binded_to(target)
        addr = self.addr_of(source.constant)
        self.emit(Addim(dst, Reg.ze(), addr))
        self.emit(Load(dst, dst))

    @override
    def on_copy(self, target: taf.Var, source: taf.Copy) -> None:
        dst = self.registers.binded_to(target)
        src = self.registers.binded_to(source.argument)
        self.emit(mov(dst, src))

    @override
    def on_sum(self, target: taf.Var, source: taf.Sum) -> None:
        self.on_trivial_binary_operation(target, source)

    @override
    def on_mul(self, target: taf.Var, source: taf.Mul) -> None:
        self.on_trivial_binary_operation(target, source)

    @override
    def on_div(self, target: taf.Var, source: taf.Div) -> None:
        self.on_trivial_binary_operation(target, source)

    @override
    def on_rem(self, target: taf.Var, source: taf.Rem) -> None:
        self.on_trivial_binary_operation(target, source)

    @override
    def on_eq(self, target: taf.Var, source: taf.Eq) -> None:
        dstr = self.registers.binded_to(target)
        lhsr = self.registers.binded_to(source.left)
        rhsr = self.registers.binded_to(source.right)

        l2r = orb = dstr
        r2l = self.registers.temporary()
        neg = self.registers.temporary()

        self.emit(Slti(l2r, lhsr, rhsr))
        self.emit(Slti(r2l, rhsr, lhsr))
        self.emit(Orb(orb, l2r, r2l))
        self.emit(Addim(neg, Reg.ze(), Integer(2**64 - 1)))
        self.emit(Xorb(dstr, orb, neg))

    @override
    def on_lt(self, target: taf.Var, source: taf.Lt) -> None:
        self.on_trivial_binary_operation(target, source)

    @override
    def on_and(self, target: taf.Var, source: taf.And) -> None:
        self.on_trivial_binary_operation(target, source)

    @override
    def on_or(self, target: taf.Var, source: taf.Or) -> None:
        self.on_trivial_binary_operation(target, source)

    def on_trivial_binary_operation(
        self,
        target: taf.Var,
        source: taf.BinaryOperator,
    ) -> None:
        dstr = self.registers.binded_to(target)
        lhsr = self.registers.binded_to(source.left)
        rhsr = self.registers.binded_to(source.right)

        instruction: Instruction
        match source:
            case taf.Sum():
                instruction = Addi(dstr, lhsr, rhsr)
            case taf.Mul():
                instruction = Muli(dstr, lhsr, rhsr)
            case taf.Div():
                instruction = Divi(dstr, lhsr, rhsr)
            case taf.Rem():
                instruction = Remi(dstr, lhsr, rhsr)
            case taf.Lt():
                instruction = Slti(dstr, lhsr, rhsr)
            case taf.And():
                instruction = Andb(dstr, lhsr, rhsr)
            case taf.Or():
                instruction = Orb(dstr, lhsr, rhsr)

        self.emit(instruction)

    def emit(self, instr: Instruction) -> None:
        self.memory.instr.append(instr)

    def addr_of(self, cnst: taf.Const) -> Immediate:
        match cnst.kind:
            case taf.Int():
                data = IntegerData(int(cnst.name))
                addr = self.memory.data_put(data)
                return Integer(addr)
            case taf.Signature():
                return Unassigned(f"${cnst.name}")
            case _:
                raise NotImplementedError

    def is_alive(self, var: taf.Var) -> bool:
        read = self.usages.next_read(var, self.context)
        write = self.usages.next_write(var, self.context)
        init = self.usages.next_write(var, Context(-1, self.procedure.entry))

        assert init is not None  # noqa: S101
        if write is not None:
            return read is not None and read <= write
        return read is not None and init < self.position

    @property
    def next_instr_addr(self) -> int:
        return len(self.memory.instr) * 4
