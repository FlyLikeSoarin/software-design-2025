import io
import os

import src.exceptions as exceptions
import src.models as models


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
    def cat(in_io: io.TextIOBase, out_io: io.TextIOBase, *args, **kwargs) -> models.ProcessResult:
        """Читает данные из входного потока или файлов и записывает в выходной поток.

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
        """Выводит аргументы в выходной поток, разделенные пробелами.

        :param in_io: входной поток (не используется)
        :param out_io: выходной поток для записи результатов
        :param args: аргументы для вывода
        """
        out_io.write(' '.join(args) + '\n')
        
        return models.ProcessResult(0)

    @staticmethod
    def wc(in_io: io.TextIOBase, out_io: io.TextIOBase, *args, **kwargs) -> models.ProcessResult:
        """Подсчитывает строки, слова и байты во входном потоке или файлах.

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
        """Выводит текущую рабочую директорию.

        :param in_io: входной поток (не используется)
        :param out_io: выходной поток для записи текущей директории
        :param args: аргументы (игнорируются)
        """
        out_io.write(os.getcwd() + '\n')
        
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
