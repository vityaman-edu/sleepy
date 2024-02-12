from typing import override

import sleepy.tafka.representation as tafka
from sleepy.tafka.walker import TafkaWalker

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
    Xorb,
    mov,
    movi,
)
from .memory import Memory


class VirtualRegisters:
    def __init__(self) -> None:
        self.sequence = (VirtReg(n) for n in range(10000))
        self.binded: dict[str, Reg] = {}

    def binded_to(self, var: tafka.Var) -> Reg:
        var_repr = repr(var)
        if var_repr not in self.binded:
            self.binded[var_repr] = self.temporary()
        return self.binded[var_repr]

    def temporary(self) -> VirtReg:
        return next(self.sequence)


class AsmikEmitListener(TafkaWalker.Listener):
    def __init__(self) -> None:
        self.memory = Memory()
        self.registers = VirtualRegisters()

        self.resolved: dict[str, int] = {}

    @override
    def enter_procedure(self, procedure: tafka.Procedure) -> None:
        addr = self.memory.data_put(IntegerData(self.next_instr_addr))
        self.resolved[repr(procedure.const)] = addr
        for i, param in enumerate(procedure.parameters):
            register = self.registers.binded_to(param)
            self.emit_i(mov(register, PhysReg.arg(i + 1)))

    @override
    def exit_procedure(self, procedure: tafka.Procedure) -> None:
        pass

    @override
    def enter_block(self, block: tafka.Block) -> None:
        self.resolved[repr(block.label)] = self.next_instr_addr

    @override
    def exit_block(self, block: tafka.Block) -> None:
        pass

    @override
    def enter_statement(self, statement: tafka.Statement) -> None:
        pass

    @override
    def exit_statement(self, statement: tafka.Statement) -> None:
        pass

    @override
    def on_return(self, ret: tafka.Return) -> None:
        retr = self.registers.binded_to(ret.value)
        self.emit_i(mov(Reg.a1(), retr))
        self.emit_i(Brn(Reg.ze(), Reg.ra()))

    @override
    def on_goto(self, goto: tafka.Goto) -> None:
        block_label = repr(goto.block.label)
        label = self.registers.temporary()
        self.emit_i(movi(label, Unassigned(block_label)))
        self.emit_i(Brn(Reg.ze(), label))

    @override
    def on_conditional(self, conditional: tafka.Conditional) -> None:
        else_label = repr(conditional.else_branch.label)
        condition = self.registers.binded_to(conditional.condition)
        else_address = self.registers.temporary()
        self.emit_i(movi(else_address, Unassigned(else_label)))
        self.emit_i(Brn(condition, else_address))

    @override
    def on_invokation(
        self,
        target: tafka.Var,
        source: tafka.Invokation,
    ) -> None:
        for i, arg in enumerate(source.args):
            arg_reg = self.registers.binded_to(arg)
            self.emit_i(mov(PhysReg.arg(i + 1), arg_reg))

        prev_ra = self.registers.temporary()
        self.emit_i(mov(prev_ra, Reg.ra()))

        proc_reg = self.registers.binded_to(source.closure)
        self.emit_i(Addim(Reg.ra(), Reg.ip(), Integer(4)))
        self.emit_i(Brn(Reg.ze(), proc_reg))

        res_reg = self.registers.binded_to(target)
        self.emit_i(mov(res_reg, Reg.a1()))

        self.emit_i(mov(Reg.ra(), prev_ra))

    @override
    def on_load(self, target: tafka.Var, source: tafka.Load) -> None:
        dst = self.registers.binded_to(target)
        addr = self.addr_of(source.constant)
        self.emit_i(Addim(dst, Reg.ze(), addr))
        self.emit_i(Load(dst, dst))

    @override
    def on_copy(self, target: tafka.Var, source: tafka.Copy) -> None:
        dst = self.registers.binded_to(target)
        src = self.registers.binded_to(source.argument)
        self.emit_i(mov(dst, src))

    @override
    def on_sum(self, target: tafka.Var, source: tafka.Sum) -> None:
        self.on_trivial_binary_operation(target, source)

    @override
    def on_mul(self, target: tafka.Var, source: tafka.Mul) -> None:
        self.on_trivial_binary_operation(target, source)

    @override
    def on_div(self, target: tafka.Var, source: tafka.Div) -> None:
        self.on_trivial_binary_operation(target, source)

    @override
    def on_rem(self, target: tafka.Var, source: tafka.Rem) -> None:
        self.on_trivial_binary_operation(target, source)

    @override
    def on_eq(self, target: tafka.Var, source: tafka.Eq) -> None:
        dstr = self.registers.binded_to(target)
        lhsr = self.registers.binded_to(source.left)
        rhsr = self.registers.binded_to(source.right)

        l2r = orb = dstr
        r2l = self.registers.temporary()
        neg = self.registers.temporary()

        self.emit_i(Slti(l2r, lhsr, rhsr))
        self.emit_i(Slti(r2l, rhsr, lhsr))
        self.emit_i(Orb(orb, l2r, r2l))
        self.emit_i(Addim(neg, Reg.ze(), Integer(2**64 - 1)))
        self.emit_i(Xorb(dstr, orb, neg))

    @override
    def on_lt(self, target: tafka.Var, source: tafka.Lt) -> None:
        self.on_trivial_binary_operation(target, source)

    @override
    def on_and(self, target: tafka.Var, source: tafka.And) -> None:
        self.on_trivial_binary_operation(target, source)

    @override
    def on_or(self, target: tafka.Var, source: tafka.Or) -> None:
        self.on_trivial_binary_operation(target, source)

    def on_trivial_binary_operation(
        self,
        target: tafka.Var,
        source: tafka.BinaryOperator,
    ) -> None:
        dstr = self.registers.binded_to(target)
        lhsr = self.registers.binded_to(source.left)
        rhsr = self.registers.binded_to(source.right)

        instruction: Instruction
        match source:
            case tafka.Sum():
                instruction = Addi(dstr, lhsr, rhsr)
            case tafka.Mul():
                instruction = Muli(dstr, lhsr, rhsr)
            case tafka.Div():
                instruction = Divi(dstr, lhsr, rhsr)
            case tafka.Rem():
                instruction = Remi(dstr, lhsr, rhsr)
            case tafka.Lt():
                instruction = Slti(dstr, lhsr, rhsr)
            case tafka.And():
                instruction = Andb(dstr, lhsr, rhsr)
            case tafka.Or():
                instruction = Orb(dstr, lhsr, rhsr)

        self.emit_i(instruction)

    def emit_i(self, instr: Instruction) -> None:
        self.memory.instr.append(instr)

    def addr_of(self, cnst: tafka.Const) -> Immediate:
        match cnst.kind:
            case tafka.Int():
                data = IntegerData(int(cnst.name))
                addr = self.memory.data_put(data)
                return Integer(addr)
            case tafka.Signature():
                return Unassigned(repr(cnst))
            case _:
                raise NotImplementedError

    @property
    def next_instr_addr(self) -> int:
        return len(self.memory.instr) * 4
