from test.tafka.emit import tafka_emit

import pytest
from pytest_golden.plugin import (  # type: ignore  # noqa: PGH003
    GoldenTestFixture,
)

from sleepy.asmik import AsmikUnit
from sleepy.tafka import TafkaUnit, Usages


def usages(tafka: TafkaUnit) -> str:
    text = ""

    for procedure in [*tafka.procedures, tafka.main]:
        text += f"{procedure.const!r}:\n"
        text += Usages.analyzed(procedure).to_text(procedure)

    return text


@pytest.mark.golden_test("group/*/*.yml")
def test_all(golden: GoldenTestFixture) -> None:
    given_sleepy_text: str = golden["sleepy"]

    expected_tafka_text: str = golden.out["tafka"]

    actual_tafka = tafka_emit(given_sleepy_text)

    actual_tafka_text = actual_tafka.to_text()[:-1]
    assert expected_tafka_text == actual_tafka_text

    expected_tafka_usages: str = golden.out["tafka-usages"]
    actual_tafka_usages = usages(actual_tafka)

    assert expected_tafka_usages == actual_tafka_usages

    expected_asmik_virt: str = golden.out["asmik-virt"]

    actual_asmik = AsmikUnit.emited_from(actual_tafka)

    actual_asmik_virt: str = actual_asmik.to_text()[:-1]
    assert expected_asmik_virt == actual_asmik_virt
