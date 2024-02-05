from sleepy.asmik.emit import AsmikUnit


def asmik_text(asmik: AsmikUnit) -> str:
    text = ""

    for instruction in asmik.memory_instr:
        text += f"{instruction!r}\n"

    return text
