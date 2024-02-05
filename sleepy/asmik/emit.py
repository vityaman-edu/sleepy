import sleepy.tafka.representation as tafka
from sleepy.tafka.emit import TafkaUnit

from .argument import Immediate, Integer, Unassigned
from .argument import Register as Reg
from .argument import VirtualRegister as VirtReg
from .instruction import (
    Addi,
    Addim,
    Divi,
    Hlt,
    Instruction,
    Load,
    Muli,
    Orb,
    Remi,
    Slti,
    Xorb,
    mov,
)


class AsmikEmiter:
    def __init__(self) -> None:
        self.virt_regs = (VirtReg(n) for n in range(10000))
        self.unassigned: dict[str, int] = {}
        self.memory_instr: list[Instruction] = []
        self.regs: dict[str, VirtReg] = {}

    def emit_block(self, block: tafka.Block) -> None:
        for statement in block.statements:
            self.emit_stmt(statement)

    def emit_stmt(self, stmt: tafka.Statement) -> None:
        match stmt:
            case tafka.Jump() as jump:
                self.emit_jump(jump)
            case tafka.Set() as set_stmt:
                self.emit_set_stmt(set_stmt)

    def emit_jump(self, jump: tafka.Jump) -> None:
        match jump:
            case tafka.Return(value):
                self.emit_i(mov(Reg.a1(), self.reg_var(value)))
                self.emit_i(Hlt())
            case tafka.Goto(block):
                raise NotImplementedError
            case tafka.Conditional(cond, then_br, else_br, next):
                raise NotImplementedError

    def emit_set_stmt(self, stmt: tafka.Set) -> None:
        match stmt.source:
            case tafka.Intrinsic() as intrinsic:
                self.emit_intrinsic(stmt.target, intrinsic)
            case tafka.Invokation() as invokation:
                self.emit_invokation(stmt.target, invokation)

    def emit_intrinsic(
        self,
        target: tafka.Var,
        source: tafka.Intrinsic,
    ) -> None:
        dst = self.reg_var(target)
        match source:
            case tafka.Load(cnst):
                self.emit_i(Addim(dst, Reg.ze(), self.addr_of(cnst)))
                self.emit_i(Load(dst, dst))
            case tafka.Copy(var):
                src = self.reg_var(var)
                self.emit_i(mov(dst, src))
            case tafka.Sum(lhs, rhs):
                lhsr = self.reg_var(lhs)
                rhsr = self.reg_var(rhs)
                self.emit_i(Addi(dst, lhsr, rhsr))
            case tafka.Mul(lhs, rhs):
                lhsr = self.reg_var(lhs)
                rhsr = self.reg_var(rhs)
                self.emit_i(Muli(dst, lhsr, rhsr))
            case tafka.Div(lhs, rhs):
                lhsr = self.reg_var(lhs)
                rhsr = self.reg_var(rhs)
                self.emit_i(Divi(dst, lhsr, rhsr))
            case tafka.Rem(lhs, rhs):
                lhsr = self.reg_var(lhs)
                rhsr = self.reg_var(rhs)
                self.emit_i(Remi(dst, lhsr, rhsr))
            case tafka.Eq(lhs, rhs):
                lhsr = self.reg_var(lhs)
                rhsr = self.reg_var(rhs)

                l2r = orb = dst
                r2l = self.reg_tmp()
                neg = self.reg_tmp()

                self.emit_i(Slti(l2r, lhsr, rhsr))
                self.emit_i(Slti(r2l, rhsr, lhsr))
                self.emit_i(Orb(orb, l2r, r2l))
                self.emit_i(Addim(neg, Reg.ze(), Integer(-1)))
                self.emit_i(Xorb(dst, orb, neg))
            case tafka.Lt(lhs, rhs):
                lhsr = self.reg_var(lhs)
                rhsr = self.reg_var(rhs)
                self.emit_i(Slti(dst, lhsr, rhsr))

    def emit_invokation(
        self,
        target: tafka.Var,
        source: tafka.Invokation,
    ) -> None:
        raise NotImplementedError

    def emit_i(self, instr: Instruction) -> None:
        self.memory_instr.append(instr)

    def reg_var(self, var: tafka.Var) -> VirtReg:
        var_repr = repr(var)
        if var_repr not in self.regs:
            self.regs[var_repr] = self.reg_tmp()
        return self.regs[var_repr]

    def reg_tmp(self) -> VirtReg:
        return next(self.virt_regs)

    def addr_of(self, cnst: tafka.Const) -> Immediate:
        return Unassigned(f"{cnst!r}")


AsmikUnit = AsmikEmiter


def asmik_emit(tafka: TafkaUnit) -> AsmikUnit:
    asmik = AsmikEmiter()
    asmik.emit_block(tafka.main)
    return asmik
