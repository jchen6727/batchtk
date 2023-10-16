from netParams import ca3
from netpyne import sim
import json

cfg = ca3.get_cfg()
netParams = ca3.get_netParams()

cfg.duration = 1000
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
    if ca3.writefile:
        print("writing to {}".format(ca3.writefile))
        ca3.write(out_json)
        ca3.signal()
    if ca3.socketfile:
        print("sending to {}".format(ca3.socketfile))
        ca3.send(out_json)
        ca3.close()
    if ca3.socketip:
        print("sending to {}:{}".format(ca3.socketip,
                                        ca3.socketport))
        ca3.send(out_json)
        ca3.close()