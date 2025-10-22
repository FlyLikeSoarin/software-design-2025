import io

import pytest

import src.builtins as buildins
import src.exceptions as exceptions


def test_exceptions():
    with pytest.raises(exceptions.ExitException):
        buildins.exit(io.StringIO(), io.StringIO())