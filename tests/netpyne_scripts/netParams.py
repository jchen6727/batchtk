from pubtk.netpyne import specs
from cfg import cfg

cfg.update_cfg()

netParams = specs.NetParams()

netParams['dt'] = cfg.dt
netParams['duration'] = cfg.duration
