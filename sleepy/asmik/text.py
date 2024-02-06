from sleepy.asmik.emit import AsmikUnit


def asmik_text(asmik: AsmikUnit) -> str:
    text = ""

    text += "memory stack\n"
    for addr, data in sorted(asmik.memory.stack.items()):
        text += f"{addr:04d}: {data!r}\n"

    text += "memory instr\n"
    for i, instruction in enumerate(asmik.memory.instr):
        text += f"{(i * 4):04d}: {instruction!r}\n"

    return text
