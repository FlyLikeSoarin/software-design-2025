import abc


class ContextProtocol(abc.ABC):
    def add_unscoped_param(name: str, value: str) -> None:
        ...

    def add_scoped_param(name: str, value: str) -> None:
        ...

    def exit_scope() -> None:
        ...
    
    def get_env() -> dict[str, str]:
        ...
    
    def get_value(name: str) -> str:
        ...

    def populate_values(template: str) -> str:
        ...
