import abc


class ContextProtocol(abc.ABC):
    def add_unscoped_param(self, name: str, value: str) -> None:
        ...

    def add_scoped_param(self, name: str, value: str) -> None:
        ...

    def exit_scope(self) -> None:
        ...
    
    def get_env(self) -> dict[str, str]:
        ...
    
    def get_value(self, name: str) -> str:
        ...

    def populate_values(self, template: str) -> str:
        ...



class Context(ContextProtocol):
    def __init__(self):
        self.unscoped_params: dict[str, str] = {}
        self.scoped_params: dict[str, str] = {}

    def add_unscoped_param(self, name: str, value: str) -> None:
        self.unscoped_params[name] = value

    def add_scoped_param(self, name: str, value: str) -> None:
        self.scoped_params[name] = value

    def exit_scope(self) -> None:
        self.scoped_params.clear()

    def get_env(self) -> dict[str, str]:
        return {**self.unscoped_params, **self.scoped_params}

    def get_value(self, name: str) -> str:
        return {**self.unscoped_params, **self.scoped_params}.get(name, "")

    def populate_values(self, template: str) -> str:
        updated_template = template
        for k, v in {**self.unscoped_params, **self.scoped_params}.items():
            updated_template.replace(f'${k}', v)
        return updated_template
