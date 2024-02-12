from typing import Any, cast

from sleepy.asmik import (
    Addi,
    Addim,
    Andb,
    AsmikUnit,
    Brn,
    Divi,
    Hlt,
    Instruction,
    Integer,
    IntegerData,
    Load,
    Muli,
    Orb,
    Register,
    Remi,
    Slti,
    Stor,
    Xorb,
)
from sleepy.core import SleepyError


class AsmikInterpreter:
    STOP = 666666666

    def __init__(self) -> None:
        self.registers: dict[str, int] = {}

        self.stack: dict[int, int] = {}
        self.instr: list[Instruction] = []

        self.registers["ze"] = 0
        self.registers["ip"] = 0
        self.registers["ra"] = self.STOP

        self.running = False

    def load(self, unit: AsmikUnit) -> None:
        self.stack = {}
        self.instr = []

        for addr, data in sorted(unit.memory.stack.items()):
            data = cast(IntegerData, data)
            self.stack[addr] = data.value

        for instr in unit.memory.instr:
            self.instr.append(instr)

        self.write(Register.ip(), 0)

    def run(self) -> None:
        self.running = True
        while self.running:
            ip = Register.ip()
            instr = self.instr[self.read(ip) // 4]
            self.write(ip, self.read(ip) + 4)
            self.execute(instr)
            if self.read(ip) == self.STOP:
                self.running = False

    def execute(self, instr: Instruction) -> None:
        match instr:
            case Addi(dst, lhs, rhs):
                self.write(dst, self.read(lhs) + self.read(rhs))
            case Addim(dst, lhs, rhs):
                rhs = cast(Integer, rhs)
                self.write(dst, self.read(lhs) + rhs.value)
            case Muli(dst, lhs, rhs):
                self.write(dst, self.read(lhs) * self.read(rhs))
            case Divi(dst, lhs, rhs):
                self.write(dst, self.read(lhs) // self.read(rhs))
            case Remi(dst, lhs, rhs):
                self.write(dst, self.read(lhs) % self.read(rhs))
            case Slti(dst, lhs, rhs):
                lt = 1 if self.read(lhs) < self.read(rhs) else 0
                self.write(dst, lt)
            case Orb(dst, lhs, rhs):
                self.write(dst, self.read(lhs) | self.read(rhs))
            case Andb(dst, lhs, rhs):
                self.write(dst, self.read(lhs) & self.read(rhs))
            case Xorb(dst, lhs, rhs):
                self.write(dst, self.read(lhs) ^ self.read(rhs))
            case Load(dst, src_addr):
                self.write(dst, self.stack[self.read(src_addr)])
            case Stor(dst_addr, src):
                self.stack[self.read(dst_addr)] = self.read(src)
            case Brn(cond, label):
                if self.read(cond) % 2 == 0:
                    self.write(Register.ip(), self.read(label))
            case Hlt():
                self.running = False

    @property
    def state(self) -> dict[str, Any]:
        return {"registers": self.registers}

    def read(self, reg: Register) -> int:
        return self.registers[repr(reg)]

    def write(self, reg: Register, value: int) -> None:
        match reg:
            case "ze":
                message = "ze is readonly"
                raise SleepyError(message)
            case _:
                self.registers[repr(reg)] = value
