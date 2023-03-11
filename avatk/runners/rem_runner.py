import ray
import subprocess
import os
import json
import itertools

@ray.remote
class rem_runner(object):
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


if __name__ == "__main__":
    ray.init()
    vars = ['PYR', 'OLM']
    envstr = {
        'RATE'  : "netParams.stimSourceParams.bkg.rate = {}",
        'WEIGHT': "netParams.stimTargetParams.bkg->PYR.amp = {}"
    }
    envval = {
        'RATE'  : [ 5   , 10 , 15  ],
        'WEIGHT': [ 0.05, 0.1, 0.15]
    }
    runners = []
    envs = []
    for i, j in itertools.product(range(3), range(3)):
        env = {
            "NETM_SAV"   : "cfg.filename = batch/RATE_{}_WEIGHT_{}".format(i, j),
            "NETM_RATE"  : envstr['RATE'  ].format(envval['RATE'  ][i]),
            "NETM_WEIGHT": envstr['WEIGHT'].format(envval['WEIGHT'][i]),
        }
        envs.append(env)
        runner = rem_runner.remote(np=2, script="net_runner.py", env=env)
        runners.append(runner)
    stdouts = ray.get([runner.run.remote() for runner in runners])
    simdata = ray.get([runner.gather_data.remote() for runner in runners])
    
    
    
