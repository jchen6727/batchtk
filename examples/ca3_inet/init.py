from netParams import ca3
from netpyne import sim
import json

cfg = ca3.get_cfg()
netParams = ca3.get_netParams()

sim.create(netParams, cfg)
sim.simulate()
sim.pc.barrier()

if sim.rank == 0:
    inputs = ca3.get_mappings()
    weights = { param: sim.net.params.connParams[param]['weight'] for param in sim.net.params.connParams}
    rates = sim.analysis.popAvgRates(show=False)
    print("===debug===")
    print(ca3.env)
    print("===mappings===")
    print(inputs)
    print("===weights===")
    print(weights)
    print("===rate===")
    print(rates)
    out_json = json.dumps({**inputs, **weights, **rates})
    if cfg.send == 'INET':
        print("sending to host {}".format(ca3.socketname))
        ca3.connect()
        ca3.send(out_json)
        ca3.close()
    else:
        print('dumping to file ca3.json')
        with open('ca3.json', 'w') as fptr:
            fptr.write(out_json)
        
