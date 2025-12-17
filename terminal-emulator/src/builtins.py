import io
import os
import re

import src.exceptions as exceptions
import src.models as models


class Builtin:
    """
    Класс встроенных команд оболочки (shell)

    Содержит статические методы для реализации встроенных команд shell.
    Каждая команда принимает входной и выходной потоки, а также аргументы.

    Команды:
    - cat: чтение и вывод файлов или входного потока
    - echo: вывод аргументов в поток
    - wc: подсчет строк, слов и байтов
    - pwd: вывод текущей директории
    - exit: завершение работы оболочки
    """

    @staticmethod
    def cat(in_io: io.TextIOBase, out_io: io.TextIOBase, *args, **kwargs) -> models.ProcessResult:
        """
        Читает данные из входного потока или файлов и записывает в выходной поток.

        Если аргументы не переданы, читает данные из входного потока.
        Если переданы имена файлов, читает и выводит их содержимое.

        :param in_io: входной поток для чтения данных
        :param out_io: выходной поток для записи результатов
        :param args: имена файлов для обработки
        :raises FileNotFoundError: если файл не найден
        """
        if not args:
            out_io.write(in_io.read())
        else:
            for filename in args:
                with open(filename, 'r') as f:
                    out_io.write(f.read())
        out_io.write("\n")
        
        return models.ProcessResult(0)

    @staticmethod
    def echo(in_io: io.TextIOBase, out_io: io.TextIOBase, *args, **kwargs) -> models.ProcessResult:
        """
        Выводит аргументы в выходной поток, разделенные пробелами.

        :param in_io: входной поток (не используется)
        :param out_io: выходной поток для записи результатов
        :param args: аргументы для вывода
        """
        out_io.write(' '.join(args) + '\n')
        
        return models.ProcessResult(0)

    @staticmethod
    def wc(in_io: io.TextIOBase, out_io: io.TextIOBase, *args, **kwargs) -> models.ProcessResult:
        """
        Подсчитывает строки, слова и байты во входном потоке или файлах.

        Если аргументы не переданы, анализирует данные из входного потока.
        Если переданы имена файлов, анализирует каждый файл и выводит общую статистику.

        :param in_io: входной поток для анализа
        :param out_io: выходной поток для записи статистики
        :param args: имена файлов для анализа
        :raises FileNotFoundError: если файл не найден
        """

        def count_stats(text):
            """Вспомогательная функция для подсчета статистики текста"""
            lines = text.count('\n')
            words = len(text.split())
            bytes_count = len(text.encode())
            return lines, words, bytes_count

        if not args:
            text = in_io.read()
            lines, words, bytes_count = count_stats(text)
            out_io.write(f"{lines} {words} {bytes_count}\n")
        else:
            total_lines, total_words, total_bytes = 0, 0, 0
            for filename in args:
                with open(filename, 'r') as f:
                    text = f.read()
                    lines, words, bytes_count = count_stats(text)
                    total_lines += lines
                    total_words += words
                    total_bytes += bytes_count
                    out_io.write(f"{lines} {words} {bytes_count} {filename}\n")

            if len(args) > 1:
                out_io.write(f"{total_lines} {total_words} {total_bytes} total\n")
        
        return models.ProcessResult(0)

    @staticmethod
    def pwd(in_io: io.TextIOBase, out_io: io.TextIOBase, *args, **kwargs) -> models.ProcessResult:
        """
        Выводит текущую рабочую директорию.

        :param in_io: входной поток (не используется)
        :param out_io: выходной поток для записи текущей директории
        :param args: аргументы (игнорируются)
        """
        out_io.write(os.getcwd() + '\n')
        
        return models.ProcessResult(0)

    @staticmethod
    def grep(in_io: io.TextIOBase, out_io: io.TextIOBase, *args, **kwargs) -> models.ProcessResult:
        """
        Фильтрует файлы по заданым параметрам.
        -f FILE  --  файл из которого будем читать, если не указан, то читаем из stdio [--file]
        -e BOOL  --  интерпретируем PATTERN как regexp [--regexp]
        -i BOOL  --  игнорировать регистр [--nocase]
        -c BOOL  --  вывести только кол-во строк [--count]
        -m INT   --  максимальное кол-во вхождений [--max-count]
        -A INT   --  строки после вхождения
        -B INT   --  строки до вхождения
        -C INT   --  строки до и после вхождения
        PATTERN  --  паттерн, по которому будут искаться значения [Всегда последний агрумент]

        :param in_io: входной поток (не используется)
        :param out_io: выходной поток для записи текущей директории
        :param args: аргументы (игнорируются)
        """

        lines: list[str]
        if filename := (kwargs.get("f") or kwargs.get("file")):
            with open(filename, mode="r") as file:
                lines = file.readlines()
        else:
            lines = in_io.readlines()

        ignore_case = bool(kwargs.get("i") or kwargs.get("nocase"))
        as_regexp = bool(kwargs.get("e") or kwargs.get("regexp"))
        pattern: str = args[-1]

        if ignore_case:
            pattern = pattern.lower()

        matches: list[int] = []
        for i, line in enumerate(lines):
            if ignore_case:
                line = line.lower()
            if as_regexp:
                if re.search(pattern, line):
                    matches.append(i)
            else:
                if pattern in line:
                    matches.append(i)
        
        if max_count := (kwargs.get("m") or kwargs.get("max-count")):
            matches = matches[:max_count]

        if kwargs.get("c") or kwargs.get("count"):
            out_io.write(str(len(matches)) + "\n")
            return models.ProcessResult(0)

        matches_set: set[int] = set(matches)
        if after := max(int(kwargs.get("A", 0)), int(kwargs.get("C", 0))):
            for i in matches:
                for j in range(i, min(len(lines), i + after + 1)):
                    matches_set.add(j)
        if before := max(int(kwargs.get("B", 0)), int(kwargs.get("C", 0))):
            for i in matches:
                for j in range(max(0, i - before), i + 1):
                    matches_set.add(j)

        filtered_lines = list(map(lambda x: x[1], filter(lambda x: x[0] in matches_set, enumerate(lines))))

        out_io.writelines(filtered_lines)
        out_io.write("\n")

        return models.ProcessResult(0)

    @staticmethod
    def exit(in_io: io.TextIOBase, out_io: io.TextIOBase, *args, **kwargs) -> models.ProcessResult:
        """Завершает выполнение оболочки.

        Выбрасывает специальное исключение ExitException, которое должно быть
        обработано на уровне IO для корректного завершения работы.

        :param in_io: входной поток (не используется)
        :param out_io: выходной поток (не используется)
        :param args: аргументы (игнорируются)
        :raises ExitException: всегда выбрасывает исключение для завершения работы
        """
        raise exceptions.ExitException("Shell termination requested")
