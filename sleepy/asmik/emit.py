import sleepy.tafka.representation as tafka
from sleepy.tafka.emit import TafkaUnit

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


class AsmikEmiter:
    def __init__(self) -> None:
        self.virt_regs = (VirtReg(n) for n in range(10000))
        self.memory = Memory()
        self.regs: dict[str, Reg] = {}

        self.resolved: dict[str, int] = {}

        self.block: tafka.Block
        self.block_until: list[tafka.Block] = []

    def emit_procedure(self, proc: tafka.Procedure) -> None:
        addr = self.memory.data_put(IntegerData(self.next_instr_addr))
        self.resolved[repr(proc.const)] = addr

        for i, param in enumerate(proc.parameters):
            param_reg = self.reg_var(param)
            self.emit_i(mov(param_reg, PhysReg.arg(i + 1)))

        self.emit_block(proc.entry)

    def emit_block(self, block: tafka.Block) -> None:
        if (
            len(self.block_until) > 0
            and self.block_until[-1].label == block.label
        ):
            return

        self.resolved[repr(block.label)] = self.next_instr_addr

        self.block = block
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
            case tafka.Return() as ret:
                self.emit_jump_return(ret)
            case tafka.Goto() as goto:
                self.emit_jump_goto(goto)
            case tafka.Conditional() as cond:
                self.emit_jump_cond(cond)

    def emit_jump_return(self, stmt: tafka.Return) -> None:
        self.emit_i(mov(Reg.a1(), self.reg_var(stmt.value)))
        self.emit_i(Brn(Reg.ze(), Reg.ra()))

    def emit_jump_goto(self, stmt: tafka.Goto) -> None:
        label = self.reg_tmp()
        label_val = Unassigned(repr(stmt.block.label))
        self.emit_i(movi(label, label_val))

        self.emit_i(Brn(Reg.ze(), label))

    def emit_jump_cond(self, conditional: tafka.Conditional) -> None:
        self.block_until.append(conditional.next_block)

        cond = self.reg_var(conditional.condition)

        els = self.reg_tmp()
        els_val = Unassigned(repr(conditional.else_branch.label))
        self.emit_i(movi(els, els_val))

        self.emit_i(Brn(cond, els))

        self.emit_block(conditional.then_branch)
        self.emit_block(conditional.else_branch)

        self.block_until.pop()

        self.emit_block(conditional.next_block)

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
                self.emit_i(Addim(neg, Reg.ze(), Integer(2**64 - 1)))
                self.emit_i(Xorb(dst, orb, neg))
            case tafka.Lt(lhs, rhs):
                lhsr = self.reg_var(lhs)
                rhsr = self.reg_var(rhs)
                self.emit_i(Slti(dst, lhsr, rhsr))
            case tafka.And(lhs, rhs):
                lhsr = self.reg_var(lhs)
                rhsr = self.reg_var(rhs)
                self.emit_i(Andb(dst, lhsr, rhsr))
            case _:
                raise NotImplementedError(str(source))

    def emit_invokation(
        self,
        target: tafka.Var,
        source: tafka.Invokation,
    ) -> None:
        for i, arg in enumerate(source.args):
            arg_reg = self.reg_var(arg)
            self.emit_i(mov(PhysReg.arg(i + 1), arg_reg))

        prev_ra = self.reg_tmp()
        self.emit_i(mov(prev_ra, Reg.ra()))

        self.emit_i(Addim(Reg.ra(), Reg.ip(), Integer(4)))

        proc_reg = self.reg_var(source.closure)
        self.emit_i(Brn(Reg.ze(), proc_reg))

        res_reg = self.reg_var(target)
        self.emit_i(mov(res_reg, Reg.a1()))

        self.emit_i(mov(Reg.ra(), prev_ra))

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


AsmikUnit = AsmikEmiter


def asmik_resolve(asmik: AsmikUnit) -> None:
    for instr in asmik.memory.instr:
        if (
            isinstance(instr, Addim)  #
            and isinstance(instr.rhs, Unassigned)
        ):
            label = instr.rhs.label
            instr.rhs = Integer(asmik.resolved[label])


def asmik_emit(tafka: TafkaUnit) -> AsmikUnit:
    asmik = AsmikEmiter()
    asmik.emit_block(tafka.main)
    for proc in tafka.procedures:
        asmik.emit_procedure(proc)
    asmik_resolve(asmik)
    return asmik
