import abc


class ContextProtocol(abc.ABC):
    @abc.abstractmethod
    def add_unscoped_param(self, name: str, value: str) -> None:
        ...

    @abc.abstractmethod
    def add_scoped_param(self, name: str, value: str) -> None:
        ...

    @abc.abstractmethod
    def exit_scope(self) -> None:
        ...
    
    @abc.abstractmethod
    def get_env(self) -> dict[str, str]:
        ...
    
    @abc.abstractmethod
    def get_value(self, name: str) -> str:
        ...

    @abc.abstractmethod
    def populate_values(self, template: str) -> str:
        ...



class Context(ContextProtocol):
    def __init__(self):
        self.unscoped_params: dict[str, str] = {}
        self.scoped_params: dict[str, str] = {}

    def add_unscoped_param(self, name: str, value: str) -> None:
        """Add an environment variable. Cannot be removed by scope."""
        self.unscoped_params[name] = value

    def add_scoped_param(self, name: str, value: str) -> None:
        """Add a temporary variable valid until exit_scope() is called."""
        self.scoped_params[name] = value

    def exit_scope(self) -> None:
        """Remove all scoped variables from the current scope."""
        self.scoped_params.clear()

    def get_env(self) -> dict[str, str]:
        """Return a dictionary of all current variables."""
        return {**self.unscoped_params, **self.scoped_params}

    def get_value(self, name: str) -> str:
        """Return the value of a variable, or empty string if not found."""
        return self.get_env().get(name, "")

    def populate_values(self, template: str) -> str:
        """Return template filled with variable values."""
        updated_template = template
        for k, v in {**self.unscoped_params, **self.scoped_params}.items():
            updated_template = updated_template.replace(f'${{{k}}}', v)
        return updated_template
