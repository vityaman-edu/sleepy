from test.tafka.emit import tafka_emit

import pytest
from pytest_golden.plugin import (  # type: ignore  # noqa: PGH003
    GoldenTestFixture,
)

from sleepy.asmik import AsmikUnit


@pytest.mark.golden_test("group/*/*.yml")
def test_all(golden: GoldenTestFixture) -> None:
    given_sleepy_text: str = golden["sleepy"]

    expected_tafka_text: str = golden.out["tafka"]

    actual_tafka = tafka_emit(given_sleepy_text)

    actual_tafka_text = actual_tafka.to_text()[:-1]
    assert expected_tafka_text == actual_tafka_text

    expected_asmik_virt: str = golden.out["asmik-virt"]

    actual_asmik = AsmikUnit.emited_from(actual_tafka)

    actual_asmik_virt: str = actual_asmik.to_text()[:-1]
    assert expected_asmik_virt == actual_asmik_virt
