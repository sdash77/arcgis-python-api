import subprocess

def run_shell_command(cmd):
    try:
        byte_output = subprocess.check_output(cmd,
                                          stderr=subprocess.STDOUT,
                                          shell=True)
        str_output = str(byte_output.decode('utf-8'))
        return str_output
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.output.decode('utf-8'))
