# CLI

### Общая архитектура проекта

#### Требования к проекту

- Поддержка встроенных команд `cat [FILE]`, `echo`, `wc [FILE]`, `pwd` и `exit`. Если вызванной команды нет в списке встроенных, то вызывать через `Process`.
- Поддержка операторов `''`, `""`, `$` и `|`. (Одинарные кавычки не поддерживают использование оператора `${}`).
- Поддержка переменных окружения, которые задаются с помощью оператора `name=variable`. Может быть только в начале строки, если после идёт команда, то переменная будет доступна только для этой команды.

#### Модули программы

- `IO` - превращает текст в готовую к исполнению команду, вызывает все остальные модули. Публичный интерфейс:

    - `def parse_command() -> bool` - Читает `stdin`. После превращения входного потока в некоторую осмысленную команду она передаётся в другие модули. Если этот метод возвращает `False`, то завершаем выполнение программы.

  Для всех токенов, кроме названия программ и имён переменных применяется `Context.populate_values`, если они находятся в двойных ковычках или `Context.get_value`, если кавычек нет и токен начинается с `$`. Если в конце строки находится символ `\`, то текущая команда продолжается на следующей строчке.

  После обработки команды получаем список объектов `Command`:

  ```
  class Command:
      name: str
      args: list[str]
      kwargs: dict[str, str]
  ```

  Которые передаются в `Executor` вместе с `Context.get_env()`

- `Context` - модуль хранения переменных окружения. `IO` модуль передаёт `Context` переменные окружения в том же порядке, в котором их передал пользователь. Важно, что для передачи переменных есть два метода `scoped` и `unscoped`, переменные переданные через `scoped` метод живут только до вызова `exit_scope`, а `unscoped` переменные считаются глобальными и могуть быть перезаписаны, но не удалены. Публичный интерфейс:

    - `def add_unscoped_param(name: str, value: str) -> None`
    - `def add_scoped_param(name: str, value: str) -> None`
    - `def exit_scope() -> None`
    - `def get_env() -> dict[str, str]` - возвращает словать из всех `scoped` и `unscoped` переменных. `scoped` переменные пишутся поверх `unscoped` переменных в случае конфликта имён.
    - `def get_value(name: str) -> str` - возвращает значение по имени `name`
    - `def populate_values(template: str) -> str` - находит все вхождения оператора `...${<var_name>}...` в строке и заменяет из на значение переменных с соотвествующим именем.

  **`IO` модуль передаёт переменные, ПОСЛЕ вызова `get_value` или `populate_values` на значении**

- `Executor` - модуль выполнения, для каждой команды вызывает `subprocesses.run`, если количество команд `k > 1` перенаправляет вывод команды `i` на ввод команды `i + 1` для всех `i in range(k)`. Это выполняется для всех команд, кроме тех у которых имя совпадает с одной из встроенных команд, тогда вместо `subprocesses` будет вызван соответствующий метод `Builtin`. Публичный интерфейс:

    - `def execute_pipeline(env: dict[str, str], commands: list[Command])`

  Первая команда читает из `stdin`, последняя команда выводит в `stdout`.

- `Buildin` - модель встроенных команд, команды имеют следующий интерфейс:
    
    ```
    def <command_name>(
        in: io.TextIOBase,
        out: io.TextIOBase,
        *args: list[str],
        **kwargs: dict[str, str],
    ) -> None
    ```

    Если вызвана команда `exit` нужно бросить специально исключение `ExitException`, которое обработает `IO` и завершит исполнение.

### Схема

### Диаграмма классов
classDiagram
    class IO {
        -context: Context
        -executor: Executor
        +parse_command() bool
    }

    class Context {
        -unscoped_vars: dict
        -scoped_vars: list~dict~
        +add_unscoped_param(name: str, value: str) void
        +add_scoped_param(name: str, value: str) void
        +exit_scope() void
        +get_env() dict
        +get_value(name: str) str
        +populate_values(template: str) str
    }

    class Executor {
        -builtin: Builtin
        +execute_pipeline(env: dict, commands: list~Command~) void
        -execute_single_command(env: dict, command: Command, input_fd, output_fd) void
        -create_process(env: dict, command: Command) Process
    }

    class Builtin {
        +cat(input: TextIOBase, output: TextIOBase, *args, **kwargs) void
        +echo(input: TextIOBase, output: TextIOBase, *args, **kwargs) void
        +wc(input: TextIOBase, output: TextIOBase, *args, **kwargs) void
        +pwd(input: TextIOBase, output: TextIOBase, *args, **kwargs) void
        +exit(input: TextIOBase, output: TextIOBase, *args, **kwargs) void
    }

    class Command {
        +name: str
        +args: list~str~
        +kwargs: dict~str, str~
    }



    IO --> Context : uses
    IO --> Executor : uses
    Executor --> Builtin : uses
    Executor --> Command : processes
    
#### TODO