import os
import sys
from io import TextIOBase


class ExitException(Exception):
    """Специальное исключение для завершения работы оболочки

    Данное исключение используется для корректного завершения работы shell.
    Позволяет IO слою корректно закрыть ресурсы перед выходом из приложения.

    """


class Builtin:
    """Класс встроенных команд оболочки (shell)

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
    def cat(input: TextIOBase, out: TextIOBase, *args, **kwargs) -> None:
        """Читает данные из входного потока или файлов и записывает в выходной поток.

        Если аргументы не переданы, читает данные из входного потока.
        Если переданы имена файлов, читает и выводит их содержимое.

        :param input: входной поток для чтения данных
        :param out: выходной поток для записи результатов
        :param args: имена файлов для обработки
        :raises FileNotFoundError: если файл не найден
        """
        if not args:
            out.write(input.read())
        else:
            for filename in args:
                with open(filename, 'r') as f:
                    out.write(f.read())

    @staticmethod
    def echo(input: TextIOBase, out: TextIOBase, *args, **kwargs) -> None:
        """Выводит аргументы в выходной поток, разделенные пробелами.

        :param input: входной поток (не используется)
        :param out: выходной поток для записи результатов
        :param args: аргументы для вывода
        """
        out.write(' '.join(args) + '\n')

    @staticmethod
    def wc(input: TextIOBase, out: TextIOBase, *args, **kwargs) -> None:
        """Подсчитывает строки, слова и байты во входном потоке или файлах.

        Если аргументы не переданы, анализирует данные из входного потока.
        Если переданы имена файлов, анализирует каждый файл и выводит общую статистику.

        :param input: входной поток для анализа
        :param out: выходной поток для записи статистики
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
            text = input.read()
            lines, words, bytes_count = count_stats(text)
            out.write(f"{lines} {words} {bytes_count}\n")
        else:
            total_lines, total_words, total_bytes = 0, 0, 0
            for filename in args:
                with open(filename, 'r') as f:
                    text = f.read()
                    lines, words, bytes_count = count_stats(text)
                    total_lines += lines
                    total_words += words
                    total_bytes += bytes_count
                    out.write(f"{lines} {words} {bytes_count} {filename}\n")

            if len(args) > 1:
                out.write(f"{total_lines} {total_words} {total_bytes} total\n")



    @staticmethod
    def pwd(input: TextIOBase, out: TextIOBase, *args, **kwargs) -> None:
        """Выводит текущую рабочую директорию.

        :param input: входной поток (не используется)
        :param out: выходной поток для записи текущей директории
        :param args: аргументы (игнорируются)
        """
        out.write(os.getcwd() + '\n')

    @staticmethod
    def exit(input: TextIOBase, out: TextIOBase, *args, **kwargs) -> None:
        """Завершает выполнение оболочки.

        Выбрасывает специальное исключение ExitException, которое должно быть
        обработано на уровне IO для корректного завершения работы.

        :param input: входной поток (не используется)
        :param out: выходной поток (не используется)
        :param args: аргументы (игнорируются)
        :raises ExitException: всегда выбрасывает исключение для завершения работы
        """
        raise ExitException("Shell termination requested")

