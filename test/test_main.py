from sleepy.example.library import hello


def test_example() -> None:
    assert hello("World") == "Hello, World!"
