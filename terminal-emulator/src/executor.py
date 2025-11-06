import abc
import contextlib
import io
import itertools
import os
import subprocess
import sys
import typing
import threading

import src.builtins as builtins
import src.models as models


class ExecutorProtocol(abc.ABC):
    @abc.abstractmethod
    def execute_pipeline(self, env: dict[str, str], commands: list[models.Command]) -> models.Status:
        ...


class Executor(ExecutorProtocol):
    def execute_pipeline(self, env: dict[str, str], commands: list[models.Command]) -> models.Status:
        """
        Запускает выполнение команды 

        Если команда есть в модуле builtins, то будет вызвана она
        Иначе вызывает subprocess.run(...)
        """
        previous_stdout = ""
        for index, command in enumerate(commands):
            with io.StringIO() as out_io, io.StringIO() as err_io, io.StringIO(initial_value=previous_stdout) as in_io:
                try:
                    if builtin_cmd := getattr(builtins.Builtin, command.name, None):
                        result: models.ProcessResult = builtin_cmd(
                            sys.stdin if index == 0 else in_io, out_io, *command.args, **command.kwargs
                        )
                    else:
                        with (
                            Executor.pipe_in_io(previous_stdout) as wrapped_in_io,
                            Executor.pipe_out_io(out_io) as wrapped_out_io,
                            Executor.pipe_out_io(err_io) as wrapped_err_io,
                        ):
                            kw_pairs = ((f"--{k}" if len(k) > 1 else f"-{k}", v) for k, v in command.kwargs.items())
                            subprocess_kwargs = typing.cast(typing.Iterable[str], itertools.chain(*kw_pairs))
                            result_ = subprocess.run(
                                [command.name, *command.args, *subprocess_kwargs],
                                env=env,
                                stdin=wrapped_in_io,
                                stdout=wrapped_out_io,
                                stderr=wrapped_err_io,
                            )
                            result = typing.cast(models.ProcessResult, result_)
                except FileNotFoundError:
                    sys.stderr.write(f"Command {command.name} not found\n")
                    status = models.Status()
                    status.index, status.code = index, -1
                    return status

                out_io.seek(0)
                previous_stdout = out_io.read()
                err_io.seek(0)
                previous_stderr = err_io.read()

            status = models.Status()
            status.index, status.code = index, result.returncode
            if result.returncode != 0:
                sys.stderr.write(previous_stderr)
                return status
        sys.stdout.write(previous_stdout)
        return status

    @contextlib.contextmanager
    @staticmethod
    def pipe_in_io(maybe_s: str | None) -> typing.Generator[io.FileIO, None, None]:
        """Оборачивает строку в FileIO или возвращает sys.stdin, если строки нет"""
        if maybe_s is None:
            try:
                yield typing.cast(io.FileIO, sys.stdin)
            finally:
                return

        r, w = os.pipe()

        def target():
            os.write(w, maybe_s.encode())
            os.close(w)

        t = threading.Thread(target=target)
        try:
            t.start()
            with io.FileIO(r, "r", closefd=True) as file:
                yield file
        finally:
            t.join()


    @contextlib.contextmanager
    @staticmethod
    def pipe_out_io(out_io: io.StringIO) -> typing.Generator[io.FileIO, None, None]:
        """Оборачивает io.StringIO в FileIO"""
        r, w = os.pipe()

        def target():
            while next_byte := os.read(r, 4096):
                out_io.write(next_byte.decode())

        t = threading.Thread(target=target)
        try:
            t.start()
            with io.FileIO(w, "w", closefd=True) as file:
                yield file
        finally:
            t.join()
