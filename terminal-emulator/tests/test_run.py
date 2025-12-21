import os
import subprocess


def test_exceptions():
    input = (
        'file=tests/example.txt echo "${file}" \\\n'
        '| wc\n'
        'exit\n'
    ).encode()
    result = subprocess.run(["python", "src/main.py"], input=input, capture_output=True)
    assert result.stdout.decode().strip().split() == "[ terminal ]: 1 1 18\n[ terminal ]: Quitting...".strip().split()

def test_ls():
    for ls_arg in ['src', '.', '..']:
        input = (
            f'ls {ls_arg}'
        ).encode()
        result = subprocess.run(["python", "src/main.py"], input=input, capture_output=True)
        assert result.stdout.decode().strip().split() == f"[ terminal ]: {"\n".join(sorted(os.listdir(ls_arg)))}\n[ terminal ]: ".strip().split()
    
    input = (
        f'ls abc def'
    ).encode()
    result = subprocess.run(["python", "src/main.py"], input=input, capture_output=True)
    assert result.returncode > 0

    input = (
        f'ls notfoundfile'
    ).encode()
    result = subprocess.run(["python", "src/main.py"], input=input, capture_output=True)
    assert result.returncode > 0


def test_cd():
    input = (
        'cd src\n'
        'pwd\n'
    ).encode()
    result = subprocess.run(["python", "src/main.py"], input=input, capture_output=True)
    assert result.stdout.decode().strip().split() == f"[ terminal ]: [ terminal ]: {os.path.join(os.getcwd(), 'src')}\n[ terminal ]: ".strip().split()

    input = (
        'cd .\n'
        'pwd\n'
    ).encode()
    result = subprocess.run(["python", "src/main.py"], input=input, capture_output=True)
    assert result.stdout.decode().strip().split() == f"[ terminal ]: [ terminal ]: {os.getcwd()}\n[ terminal ]: ".strip().split()
    
    input = (
        f'cd abc def'
    ).encode()
    result = subprocess.run(["python", "src/main.py"], input=input, capture_output=True)
    assert result.returncode > 0

    input = (
        f'cd notfoundfile'
    ).encode()
    result = subprocess.run(["python", "src/main.py"], input=input, capture_output=True)
    assert result.returncode > 0
