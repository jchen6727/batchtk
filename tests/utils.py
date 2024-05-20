import re
import subprocess

def get_exports(filename):
    with open(filename, 'r') as fptr:
        items = re.findall(r'export (.*?)="(.*?)"', fptr.read())
        return {key: val for key, val in items}

def get_port_info(port):
    output = subprocess.run(shlex.split('lsof -i :{}'.format(port)), capture_output=True, text=True)
    if output.returncode == 0:
        return output.stdout
    else:
        return output.returncode