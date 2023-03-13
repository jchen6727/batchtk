import subprocess
import os
import json

class remote_runner(object):
# runner that calls remote net_runner
    cmdstr = "mpiexec -n {} nrniv -python -mpi {}".format( 1, 'runner.py' )
    savekey = 'NETM_SAV'
    def __init__(self, cmdstr=None, env={}):
        if cmdstr:
            self.cmdstr = self.cmdstr
        self.cmdarr = self.cmdstr.split()
        # need to copy environ or else cannot find necessary paths.
        self.__osenv = os.environ.copy()
        self.__osenv.update(env)
        self.env = env
        filevar = env[self.savekey].split('=')[-1].strip()
        self.filename = "{}".format(filevar)

    def get_command(self):
        return self.cmdstr

    def run(self):
        self.proc = subprocess.run(self.cmdarr, env=self.__osenv, text=True, stdout=subprocess.PIPE, \
            stderr=subprocess.PIPE)
        self.stdout = self.proc.stdout
        self.stderr = self.proc.stderr
        return self.stdout, self.stderr

    def gather_data(self):
        filename = "{}_data.json".format(self.filename)
        self.data = json.load( open(filename) )
        return self.data
