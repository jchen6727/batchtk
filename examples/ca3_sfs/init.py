from netParams import ca3
from netpyne import sim
import json

cfg = ca3.get_cfg()
netParams = ca3.get_netParams()

reports = []

"""
def interval_function():
    report = sim.analysis.popAvgRates(show=False)
    print(report)
    report.append(reports)
"""

#cfg.duration = 1000
cfg.duration = 1000
sim.create(netParams, cfg)
sim.simulate()
sim.pc.barrier()






if sim.rank == 0:
    inputs = ca3.get_mappings()
    weights = { param: sim.net.params.connParams[param]['weight'] for param in sim.net.params.connParams}
    rates = sim.analysis.popAvgRates(show=False)
    interval_rates = sim.analysis.popAvgRates(tranges=[[   0,  250],
                                                        [250,  500],
                                                        [500,  750],
                                                        [750, 1000]],
                                              show=False)
    print("===debug===")
    print(ca3.env)
    print("===mappings===")
    print(inputs)
    print("===weights===")
    print(weights)
    print("===rate===")
    print(rates)
    out_json = json.dumps({**inputs, **weights, **rates, **interval_rates})
    try:
        print("writing to {}".format(ca3.writefile))
        ca3.write(out_json)
        ca3.signal()
    except:
        print("writing to ca3_data.json")
        with open('ca3_data.json', 'w') as fptr:
            json.dump({**inputs, **weights, **rates, **interval_rates}, fptr)