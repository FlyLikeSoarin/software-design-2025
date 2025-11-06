import src.context as context_lib
import src.exceptions as exceptions_lib
import src.executor as executor_lib
import src.io as io_lib


context = context_lib.Context()
executor = executor_lib.Executor()
io = io_lib.IO(context, executor)

try:
    while io.parse_command():
        pass
except exceptions_lib.ExitException:
    print("Quitting...")