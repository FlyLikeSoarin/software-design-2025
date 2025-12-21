import io
import os
import sys

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
    def cd(in_io: io.TextIOBase, out_io: io.TextIOBase, *args, **kwargs) -> models.ProcessResult:
        """Меняет текущую директорию на заданную в аргументе

        :param in_io: входной поток
        :param out_io: выходной поток (не используется)
        :param args: аргументы
        """
        def go_to_user_home():
            user_homedir = os.path.expanduser("~")
            os.chdir(user_homedir)
        
        if len(args) == 0:
            go_to_user_home()
        elif len(args) == 1:
            if args[0] == "~":
                go_to_user_home()
            else:
                if not os.path.exists(args[0]):
                    print(f"cd: {args[0]}: No such file or directory", file=sys.stderr)
                    return models.ProcessResult(1)
                os.chdir(args[0])
        else:
            print("cd: too many args", file=sys.stderr)
            return models.ProcessResult(1)
        
        return models.ProcessResult(0)
    
    @staticmethod
    def ls(in_io: io.TextIOBase, out_io: io.TextIOBase, *args, **kwargs) -> models.ProcessResult:
        """Выводит список файлов в директории, если передан файл, выводит его же путь

        :param in_io: входной поток
        :param out_io: выходной поток
        :param args: аргументы
        """
        ls_path = ""
        if len(args) == 0:
            ls_path = "."
        elif len(args) == 1:
            ls_path = args[0]
        else:
            print("ls: too many args", file=sys.stderr)
            return models.ProcessResult(1)
        
        if not os.path.exists(ls_path):
            print(f"ls: {ls_path}: No such file or directory", file=sys.stderr)
            return models.ProcessResult(1)
        
        if os.path.isdir(ls_path):
            out_io.write("\n".join(sorted(os.listdir(ls_path))) + '\n')
        else:
            out_io.write(ls_path + '\n')

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
