import abc
import itertools
import subprocess
import sys

import src.models as models


class ExecutorProtocol(abc.ABC):
    def execute_pipeline(self, env: dict[str, str], commands: list[models.Command]) -> models.Status:
        ...


class Executor(ExecutorProtocol):
    def execute_pipeline(self, env: dict[str, str], commands: list[models.Command]) -> models.Status:
        previous_stdout = b""
        for index, command in enumerate(commands):
            if index == 0:
                kwargs = {"stdin": sys.stdin}
            else:
                kwargs = {"input": previous_stdout}
            
            result = subprocess.run(
                [command.name, *command.args, *itertools.chain([(f"--{k}", v) for k, v in command.kwargs])],
                env=env,
                capture_output=True,
                **kwargs,
            )

            previous_stdout = result.stdout

            if result.returncode != 0:
                status = models.Status()
                status.index, status.code = index, result.returncode
                return status
        print(previous_stdout.decode())
