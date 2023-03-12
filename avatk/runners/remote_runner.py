import subprocess
import os
import json

class remote_runner(object):
# runner that calls remote net_runner
    def __init__(self, np=1, script="net_runner.py", env={}):
        self.np = np
        self.cmdstr = "mpiexec -n {} nrniv -python -mpi {}".format(np, script).split()
        # need to copy environ or else cannot find necessary paths.
        self.__osenv = os.environ.copy()
        self.__osenv.update(env)
        self.env = env
        filevar = env['NETM_SAV'].split('=')[-1].strip()
        self.filename = "{}_data.json".format(filevar)

    def get_command(self):
        return self.cmdstr

    # def add_env(self, env):
    #     self.env.update(env)


    def run(self):
        self.proc = subprocess.run(self.cmdstr, env=self.__osenv, text=True, stdout=subprocess.PIPE, \
            stderr=subprocess.PIPE)
        self.stdout = self.proc.stdout
        self.stderr = self.proc.stderr
        return self.stdout, self.stderr

    def gather_data(self):
        self.data = json.load( open(self.filename) )
        return self.data
