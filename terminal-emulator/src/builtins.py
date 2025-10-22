import io

import src.exceptions as exceptions


def cat(
    in_io: io.TextIOBase,
    out_io: io.TextIOBase,
    *args: list[str],
    **kwargs: dict[str, str],
) -> None:
    raise NotImplementedError()


def echo(
    in_io: io.TextIOBase,
    out_io: io.TextIOBase,
    *args: list[str],
    **kwargs: dict[str, str],
) -> None:
    raise NotImplementedError()


def wc(
    in_io: io.TextIOBase,
    out_io: io.TextIOBase,
    *args: list[str],
    **kwargs: dict[str, str],
) -> None:
    raise NotImplementedError()


def pwd(
    in_io: io.TextIOBase,
    out_io: io.TextIOBase,
    *args: list[str],
    **kwargs: dict[str, str],
) -> None:
    raise NotImplementedError()


def exit(
    in_io: io.TextIOBase,
    out_io: io.TextIOBase,
    *args: list[str],
    **kwargs: dict[str, str],
) -> None:
    raise exceptions.ExitException()