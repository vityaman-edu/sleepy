from sleepy.core import SleepyError, SourceLocation


class ParsingError(SleepyError):
    def __init__(self, message: str, location: SourceLocation) -> None:
        super().__init__(f"({location.line}, {location.column}): {message}")
