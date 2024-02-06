from test.tafka.emit import tafka_emit

import pytest

from sleepy.asmik.emit import AsmikUnit, asmik_emit
from sleepy.asmik.text import asmik_text
from sleepy.tafka.text import tafka_text


def purified(source: str) -> str:
    return "\n".join(
        line.lstrip()  # enable indentation
        for line in source.split("\n")
        if len(line) != 0  # enable empty lines
    )


@pytest.mark.golden_test("group/*/*.yml")
def test_all(golden: dict[str, str]) -> None:
    given_sleepy_text: str = golden["sleepy"]

    expected_tafka_text: str = golden["tafka"]
    expected_tafka_text = purified(expected_tafka_text)

    actual_tafka = tafka_emit(given_sleepy_text)

    actual_tafka_text = tafka_text(actual_tafka)[:-1]
    assert expected_tafka_text == actual_tafka_text

    expected_asmik_virt: str = golden["asmik-virt"]
    expected_asmik_virt = purified(expected_asmik_virt)

    if expected_asmik_virt == "TODO":
        return

    actual_asmik: AsmikUnit = asmik_emit(actual_tafka)

    actual_asmik_virt: str = asmik_text(actual_asmik)[:-1]
    assert expected_asmik_virt == actual_asmik_virt
