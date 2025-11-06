import subprocess


def test_exceptions():
    input = (
        'file=tests/example.txt echo "${file}" \\\n'
        '| wc\n'
        'exit\n'
    ).encode()
    result = subprocess.run(["python", "src/main.py"], input=input, capture_output=True)
    assert result.stdout.decode().strip().split() == "[ terminal ]: 1 1 18\n[ terminal ]: Quitting...".strip().split()