import shlex
from subprocess import PIPE, Popen


def get_exitcode_stdout_stderr(cmd):
    """
    Execute the external command and get its exitcode, stdout and stderr.
    """
    args = shlex.split(cmd)

    proc = Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    out, err = out.decode("utf8"), err.decode("utf8")
    exitcode = proc.returncode
    #
    return exitcode, out.rstrip("\n"), err.rstrip("\n")


def recognize(fname: str) -> str:
    cmd = f"ocrad {fname}"
    _, out, _ = get_exitcode_stdout_stderr(cmd)
    out = out.strip()
    if out == "s":
        out = "5"
    elif out == "o":
        out = "0"
    return out
