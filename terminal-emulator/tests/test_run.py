import subprocess


def test_exceptions():
    input = (
        'file=tests/example.txt echo "${file}" \\\n'
        '| wc\n'
        'exit\n'
    ).encode()
    result = subprocess.run(["python", "src/main.py"], input=input, capture_output=True)
    assert result.stdout.decode().strip().split() == "[ terminal ]: 1 1 18\n[ terminal ]: Quitting...".strip().split()

def test_grep():
    input = b"grep -f README.md --regexp true '(I|i)nt'\nexit"
    result = subprocess.run(["python", "src/main.py"], input=input, capture_output=True)
    assert result.stdout.decode().strip().split() == (
        "[ terminal ]: ## Command-Line Interface (terminal-emulator)\n"
        "Проект реализует первую часть архитектуры Command-Line Interface (CLI), включающую поддержку Read–Execute–Print Loop и базовых встроенных команд. По мере работы описание будет дополняться. \n"
        "poetry run make lint [ terminal ]: Quitting..."
    ).strip().split()

    input = b"grep -f README.md --count true poetry\nexit"
    result = subprocess.run(["python", "src/main.py"], input=input, capture_output=True)
    assert result.stdout.decode().strip().split() == "[ terminal ]: 4 [ terminal ]: Quitting...".strip().split()