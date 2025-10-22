import abc

import src.models as models


class ExecutorProtocol(abc.ABC):
    def execute_pipeline(env: dict[str, str], commands: list[models.Command]) -> models.Status:
        ...
