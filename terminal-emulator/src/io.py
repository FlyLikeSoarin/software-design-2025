import abc


class IOProtocol(abc.ABC):
    def parse_command() -> bool:
        ...
