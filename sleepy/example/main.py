import logging

from sleepy.example.library import hello


def main() -> None:
    logging.warning(hello("World"))
