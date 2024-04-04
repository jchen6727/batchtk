from netpyne.batchtools import specs
from netpyne.batchtools import comm
from netpyne import sim
from cfg import cfg
from netParams import netParams
import json

comm.initialize()

sim.createSimulateAnalyze(netParams=netParams,
                          simConfig=cfg)

results = sim.analysis.popAvgRates(show=False)

#inputs = specs.get_mappings()
#out_json = json.dumps({**inputs, **rates})

results['S_loss'] = (results['S'] - 10.2)**2
results['M_loss'] = (results['M'] - 12.9)**2
out_json = json.dumps(results)

#TODO put all of this in a single function.
comm.send(out_json)
comm.close()


