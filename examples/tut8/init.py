from pubtk.netpyne import specs
from netpyne import sim
from cfg import cfg
from netParams import netParams

import json

sim.createSimulateAnalyze(netParams=netParams,
                          simConfig=cfg)

rates = sim.analysis.popAvgRates(show=False)
inputs = specs.get_mappings()
out_json = json.dumps({**inputs, **rates})
if cfg.send == 'INET':
    print("sending to host {}".format(specs.socketname))
    try:
        specs.connect()
        specs.send(out_json)
        specs.close()
    except Exception as e:
        print("error sending to host due to:\n{}".format(e))
        specs.close()
