import src.io as terminal_io
import src.models as models


def test_tokenize():
    io = terminal_io.IO(None, None)  # noqa

    assert [
        r"'some'",
        r"'\"\\''",
    ] == io.tokenize([io.single_quotes_pattern], r"echo 'some' --out='\"\\'' -n 10")

    assert [
        r'"some"',
        r'"\'\\""',
    ] == io.tokenize([io.double_quotes_pattern], r'echo "some" --out="\'\\""" -n 10')

    assert [
        r"var=value",
        r"echo",
        r"'single'",
        r"\"double\"",
        r"--out=",
        r"'\"\\''",
        r"--in=",
        r"file",
        r"-n",
        r"10",
        r"|",
        r"wc",
    ] == io.tokenize(io.pattern_pipeline, r"var=value echo 'single' \"double\" --out='\"\\'' --in=file -n 10 | wc")


def test_defenitions():
    io = terminal_io.IO(None, None)  # noqa

    assert (
        {"key1": "value1", "KeY2": "2Value"},
        ["echo", "$key1"],
    ) == io.consume_defenitions(["key1=value1",  "KeY2=2Value", "echo", "$key1"])

    assert (
        {"key1": "value1", "KeY2": "2Value"},
        [],
    ) == io.consume_defenitions(["key1=value1",  "KeY2=2Value"])


def test_consume_command():
    io = terminal_io.IO(None, None)  # noqa

    command, tail = io.consume_command(
        [
            r"echo",
            r"'single'",
            r"\"double\"",
            r"--out=",
            r"'\"\\''",
            r"--in=",
            r"file",
            r"-n",
            r"10",
            r"|",
            r"wc",
        ]
    )

    assert tail == [r"wc"]
    assert command.name == r"echo"
    assert command.args == [r"'single'", r"\"double\""]
    assert command.kwargs == {
        r"out": r"'\"\\''",
        r"in": r"file",
        r"n": r"10",
    }
