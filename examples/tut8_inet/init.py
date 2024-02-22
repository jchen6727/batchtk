from params import main
from netpyne import sim
import json

cfg, params = main.get_SimConfig(), main.get_NetParams(set_cfg=False)

sim.createSimulateAnalyze(netParams=params,
                          simConfig=cfg)

rates = sim.analysis.popAvgRates(show=False)
inputs = main.get_mappings()
out_json = json.dumps({**inputs, **rates})
if cfg.send == 'INET': #TODO default option is to hide all of this
    print("sending to host {}".format(main.socketname))
    try:
        main.connect()
        main.send(out_json)
        main.close()
    except Exception as e:
        print("error sending to host due to:\n{}".format(e))
        main.close()
