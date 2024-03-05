#import site
#site.addsitedir('/content/drive/MyDrive/venv/lib/python3.10/site-packages')
import json
from pubtk.runtk import NetpyneRunner

specs = NetpyneRunner()

cfg = specs.get_SimConfig()

cfg.duration = 1*1e3
cfg.dt = 0.025

specs.set_mappings('cfg')

timesteps = json.dumps({'timesteps': cfg.duration / cfg.dt})

#specs.connect()
#specs.send(timesteps)
print(timesteps)
#specs.close()