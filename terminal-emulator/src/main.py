import src.context as context
import src.executor as executor
import src.io as io


context = context.Context()
executor = executor.Executor()
io = io.IO(context, executor)

while True:
    io.parse_command()