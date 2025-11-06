class Command:
    def __init__(self):
        self.args = []
        self.kwargs = {}

    name: str
    args: list[str]
    kwargs: dict[str, str]


class Status:
    code: int  # Return code of last command or first command that failed
    index: int  # Index of command which return code is written above


class ProcessResult:
    returncode: int

    def __init__(self, code: int):
        self.returncode = code
