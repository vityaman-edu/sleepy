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


class AsmikEmitListener(TafkaWalker.Listener):
    def __init__(self) -> None:
        self.virt_regs = (VirtReg(n) for n in range(10000))
        self.memory = Memory()
        self.regs: dict[str, Reg] = {}

        self.resolved: dict[str, int] = {}

        self.block: tafka.Block
        self.block_until: list[tafka.Block] = []

    @override
    def enter_procedure(self, procedure: tafka.Procedure) -> None:
        addr = self.memory.data_put(IntegerData(self.next_instr_addr))
        self.resolved[repr(procedure.const)] = addr
        for i, param in enumerate(procedure.parameters):
            param_reg = self.reg_var(param)
            self.emit_i(mov(param_reg, PhysReg.arg(i + 1)))

    @override
    def exit_procedure(self, procedure: tafka.Procedure) -> None:
        pass

    @override
    def enter_block(self, block: tafka.Block) -> None:
        self.resolved[repr(block.label)] = self.next_instr_addr
        self.block = block

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
        self.emit_i(mov(Reg.a1(), self.reg_var(ret.value)))
        self.emit_i(Brn(Reg.ze(), Reg.ra()))

    @override
    def on_goto(self, goto: tafka.Goto) -> None:
        label = self.reg_tmp()
        self.emit_i(movi(label, Unassigned(repr(goto.block.label))))
        self.emit_i(Brn(Reg.ze(), label))

    @override
    def on_conditional(self, conditional: tafka.Conditional) -> None:
        else_label = repr(conditional.else_branch.label)

        condition = self.reg_var(conditional.condition)
        else_address = self.reg_tmp()
        self.emit_i(movi(else_address, Unassigned(else_label)))
        self.emit_i(Brn(condition, else_address))

    @override
    def on_invokation(
        self,
        target: tafka.Var,
        source: tafka.Invokation,
    ) -> None:
        for i, arg in enumerate(source.args):
            arg_reg = self.reg_var(arg)
            self.emit_i(mov(PhysReg.arg(i + 1), arg_reg))

        prev_ra = self.reg_tmp()
        self.emit_i(mov(prev_ra, Reg.ra()))

        proc_reg = self.reg_var(source.closure)
        self.emit_i(Addim(Reg.ra(), Reg.ip(), Integer(4)))
        self.emit_i(Brn(Reg.ze(), proc_reg))

        res_reg = self.reg_var(target)
        self.emit_i(mov(res_reg, Reg.a1()))

        self.emit_i(mov(Reg.ra(), prev_ra))

    @override
    def on_load(self, target: tafka.Var, source: tafka.Load) -> None:
        dst = self.reg_var(target)
        addr = self.addr_of(source.constant)
        self.emit_i(Addim(dst, Reg.ze(), addr))
        self.emit_i(Load(dst, dst))

    @override
    def on_copy(self, target: tafka.Var, source: tafka.Copy) -> None:
        dst = self.reg_var(target)
        src = self.reg_var(source.argument)
        self.emit_i(mov(dst, src))

    @override
    def on_sum(self, target: tafka.Var, source: tafka.Sum) -> None:
        dst = self.reg_var(target)
        lhsr = self.reg_var(source.left)
        rhsr = self.reg_var(source.right)
        self.emit_i(Addi(dst, lhsr, rhsr))

    @override
    def on_mul(self, target: tafka.Var, source: tafka.Mul) -> None:
        dst = self.reg_var(target)
        lhsr = self.reg_var(source.left)
        rhsr = self.reg_var(source.right)
        self.emit_i(Muli(dst, lhsr, rhsr))

    @override
    def on_div(self, target: tafka.Var, source: tafka.Div) -> None:
        dst = self.reg_var(target)
        lhsr = self.reg_var(source.left)
        rhsr = self.reg_var(source.right)
        self.emit_i(Divi(dst, lhsr, rhsr))

    @override
    def on_rem(self, target: tafka.Var, source: tafka.Rem) -> None:
        dst = self.reg_var(target)
        lhsr = self.reg_var(source.left)
        rhsr = self.reg_var(source.right)
        self.emit_i(Remi(dst, lhsr, rhsr))

    @override
    def on_eq(self, target: tafka.Var, source: tafka.Eq) -> None:
        rdst = self.reg_var(target)
        lhsr = self.reg_var(source.left)
        rhsr = self.reg_var(source.right)

        l2r = orb = rdst
        r2l = self.reg_tmp()
        neg = self.reg_tmp()

        self.emit_i(Slti(l2r, lhsr, rhsr))
        self.emit_i(Slti(r2l, rhsr, lhsr))
        self.emit_i(Orb(orb, l2r, r2l))
        self.emit_i(Addim(neg, Reg.ze(), Integer(2**64 - 1)))
        self.emit_i(Xorb(rdst, orb, neg))

    @override
    def on_lt(self, target: tafka.Var, source: tafka.Lt) -> None:
        dst = self.reg_var(target)
        lhsr = self.reg_var(source.left)
        rhsr = self.reg_var(source.right)
        self.emit_i(Slti(dst, lhsr, rhsr))

    @override
    def on_and(self, target: tafka.Var, source: tafka.And) -> None:
        dst = self.reg_var(target)
        lhsr = self.reg_var(source.left)
        rhsr = self.reg_var(source.right)
        self.emit_i(Andb(dst, lhsr, rhsr))

    @override
    def on_or(self, target: tafka.Var, source: tafka.Or) -> None:
        dst = self.reg_var(target)
        lhsr = self.reg_var(source.left)
        rhsr = self.reg_var(source.right)
        self.emit_i(Orb(dst, lhsr, rhsr))

    def emit_i(self, instr: Instruction) -> None:
        self.memory.instr.append(instr)

    def reg_var(self, var: tafka.Var) -> Reg:
        var_repr = repr(var)
        if var_repr not in self.regs:
            self.regs[var_repr] = self.reg_tmp()
        return self.regs[var_repr]

    def reg_tmp(self) -> VirtReg:
        return next(self.virt_regs)

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
