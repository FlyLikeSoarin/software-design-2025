import abc
import re

import src.context as context_lib
import src.executor as executor_lib
import src.models as models


class IOProtocol(abc.ABC):
    @abc.abstractmethod
    def parse_command(self) -> bool:
        ...


class IO(IOProtocol):
    def __init__(self, context: context_lib.ContextProtocol, executor: executor_lib.ExecutorProtocol):
        self.context = context
        self.executor = executor

        self.single_quotes_pattern = re.compile(r"'([^']|\\')+[^\\]'")
        self.double_quotes_pattern = re.compile(r'"([^"]|\\")+[^\\]"')
        self.param_pattern = re.compile(r'--?(?P<key>[a-zA-Z_]+[a-zA-Z0-9_]*)=?')
        self.token_pattern = re.compile(r'[^\s]+')
        self.pattern_pipeline = [
            self.single_quotes_pattern,
            self.double_quotes_pattern,
            self.param_pattern,
            self.token_pattern,
        ]

        self.defenition_matcher = re.compile(r"(?P<key>[a-zA-Z_]+[a-zA-Z0-9_]*)=(?P<value>[^\s]+)")

    def read_command(self) -> str:
        """Читает строки из stdin, пока строки заканчиваются на \\"""
        command = ""
        is_first_line = True
        while True:
            snippet = input("[ terminal ]: " if is_first_line else "").strip()
            is_first_line = False
            command += snippet
            if snippet.endswith("\\"):
                command = command[:-1]
                continue
            return command
    
    def tokenize(self, patterns: list[re.Pattern], command) -> list[str]:
        """
        Разделяет строку на токены рекурсивно запуская регулярные выражения

        Порядок выражений задаёт приоритет различных конструкций языка при парсинге
        """
        pattern, *next_patterns = patterns
        def recurse(s: str) -> list[str]:
            if next_patterns:
                return self.tokenize(next_patterns, s)
            else:
                return []
        tail: str = command
        tokens = []
        while tail:
            m = pattern.search(tail)
            if m:
                start, end = m.span()
                tokens.extend(recurse(tail[:start]))
                tokens.append(m.group())
                tail = tail[end:]
            else:
                tokens.extend(recurse(tail))
                tail = ""
        return tokens

    def consume_defenitions(self, tokens: list[str]) -> tuple[dict[str, str], list[str]]:
        """Забрать из начала списка определения"""
        env = {}
        for index, token in enumerate(tokens):
            if m := self.defenition_matcher.match(token):
                groupdict = m.groupdict()
                env[groupdict["key"]] = groupdict["value"]
            else:
                return env, tokens[index:]
        return env, []
            
    def consume_command(self, tokens: list[str]) -> tuple[models.Command, list[str]]:
        """Забрать из начала списка токенов комманду, потребяет все токены до "|" или до конца строки"""
        if "|" in tokens:
            pos = tokens.index("|")
            tail = tokens[pos+1:]
            tokens = tokens[:pos]
        else:
            tail = []

        command = models.Command()
        command.name, *tokens = tokens

        while tokens:
            head, *tokens = tokens
            if (m := self.param_pattern.match(head)) and tokens and not self.param_pattern.match(tokens[0]):
                key = m.groupdict()["key"]
                value, *tokens = tokens
                command.kwargs[key] = value
            else:
                command.args.append(head)
        
        return command, tail


    def populate(self, value: str) -> str:
        """Применить для конкретного токера подставновки из контекста"""
        if value.startswith(r'"'):
            value = self.context.populate_quote(value.strip(r'"'))
        elif value.startswith(r"'"):
            value = value.strip(r"'")
        else:
            value = self.context.populate_naked(value)
        return value


    def parse_command(self) -> bool:
        """Считывает команду из stdin, парсит её превращая в Command и запускает Executor"""
        raw_command = self.read_command()
    
        tokens = self.tokenize(self.pattern_pipeline, raw_command)
        env, tokens = self.consume_defenitions(tokens)
        for k, v in env.items():
            if tokens:
                self.context.add_scoped_param(k, v)
            else:
                self.context.add_unscoped_param(k, v)
        
        commands = []
        while tokens:
            command, tokens = self.consume_command(tokens)
            command.args = [self.populate(value) for value in command.args]
            command.kwargs = {key: self.populate(value) for key, value in command.kwargs.items()}
            commands.append(command)
        
        if commands:
            self.executor.execute_pipeline(self.context.get_env(), commands)

        self.context.exit_scope()
        
        return True
