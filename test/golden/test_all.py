from test.tafka.emit import tafka_emit, tafka_text

import pytest


@pytest.mark.golden_test("group/*/*.yml")
def test_all(golden: dict[str, str]) -> None:
    given_sleepy_text: str = golden["sleepy"]
    expected_tafka_text: str = golden["tafka"]

    expected_tafka_text = "\n".join(
        line.lstrip()
        for line in expected_tafka_text.split("\n")
        if len(line) != 0
    )

    actual_tafka = tafka_emit(given_sleepy_text)

    actual_tafka_text = tafka_text(actual_tafka.main)[:-1]

    assert expected_tafka_text == actual_tafka_text
