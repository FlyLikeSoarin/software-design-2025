import abc
import itertools
import re

import src.context as context_lib
import src.executor as executor_lib
import src.models as models


class IOProtocol(abc.ABC):
    def parse_command() -> bool:
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

        self.defenition_matcher = re.compile(r"(?P<key>[a-zA-Z_]+[a-zA-Z0-9_]*)=(?P<value>[a-zA-Z0-9_]+)")

    def read_command(self) -> str:
        """ Read command until line does not end with \\"""
        command = ""
        while True:
            snippet = input()
            command += snippet
            if snippet.strip().endswith("\\"):
                continue
            return command
    
    def tokenize(self, patterns: list[re.Pattern], command) -> list[str]:
        pattern, *next_patterns = patterns
        if next_patterns:
            recurse = lambda s: self.tokenize(next_patterns, s)
        else:
            recurse = lambda _: []
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
        env = {}
        for index, token in enumerate(tokens):
            if m := self.defenition_matcher.match(token):
                groupdict = m.groupdict()
                env[groupdict["key"]] = groupdict["value"]
            else:
                return env, tokens[index:]
        return env, []
            
    def consume_command(self, tokens: list[str]) -> tuple[models.Command, list[str]]:
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
            if m := self.param_pattern.match(head):
                key = m.groupdict()["key"]
                value, *tokens = tokens
                command.kwargs[key] = value
            else:
                command.args.append(head)
        
        return command, tail


    def populate(self, value: str) -> str:
        if value.startswith(r'"'):
            value = value.strip(r'"')
        elif value.startswith(r"'"):
            value = value.strip(r"'")
        return self.context.populate_values(value)


    def parse_command(self) -> bool:
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
            command.kwargs = {key: self.populate(value) for key, value in command.kwargs}
            commands.append(command)
        
        self.executor.execute_pipeline(self.context.get_env(), commands)

        self.context.exit_scope()
