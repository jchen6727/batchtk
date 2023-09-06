from pubtk.runtk import NetpyneRunner
#from pubtk.runtk.runners import NetpyneRunner
from netpyne import sim

from utils import get_freq
from ca3 import ca3
import json

SO = '/ddn/jchen/dev/optimization/batchdir/mod/x86_64/libnrnmech.so'
MECH = '/ddn/jchen/dev/optimization/batchdir/mod'
#DLL = 'mod/x86_64/libnrnmech.so'
#define parameter strings
"""
class NR(NetpyneRunner):
    "inherit the process_runner"
    sim = sim
    netParams = netParams
    cfg = cfg

    def get_freq(self):
        freq_data = {}
        data = self.sim.analysis.prepareSpikeData()['legendLabels']
        for datm in data:
            pop = datm.split('\n')[0]
            freq = datm.split(' ')[-2]
            freq_data[pop] = freq
        return freq_data
"""
if __name__ == "__main__":
    try:
        sim.h.hcurrent
    except:
        #neuron.load_mechanisms(MECH)
        sim.h.nrn_load_dll(SO)
    #json_out = r.get_mappings()
    #print("DELIM{}".format(json_out))
    sim.create(ca3.netParams, ca3.cfg)
    sim.simulate()
    sim.pc.barrier()
    if sim.rank == 0: # data out (print, and then file I/O if writefile specified)
        inputs = ca3.get_mappings()
        spikes = sim.analysis.popAvgRates(show=False)
        out_json = json.dumps({**inputs, **spikes})
        print("===FREQUENCIES===\n")
        print(out_json)
        if ca3.writefile:
            print("writing to {}".format(ca3.writefile))
            ca3.write(out_json)
            ca3.signal()