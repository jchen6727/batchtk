import os

class net_runner(object): # has to run within an mpi by parsing environ
    sim = object()
    netParams = object()
    cfg = object()
    def __init__(self):
        self.map_strings = [os.environ[map_string] for map_string in os.environ if 'NETM' in map_string]
        self.set_maps()

    def __getitem__(self, k):
        try:
            return object.__getattribute__(self, k)
        except:
            raise KeyError(k)

    def set_maps(self):
        for map_string in self.map_strings:
            self.set_map(map_string)

    def set_map(self, map_string):
        # split the map_string based on delimiters
        assign_path, value = map_string.split('=')
        assigns = assign_path.strip().split('.')
        try:
            value = float(value)
        except:
            value = value.strip()
        # crawl assigns array
        crawler = self.__getitem__(assigns[0])
        for gi in assigns[1:-1]:
            crawler = crawler.__getitem__(gi)
        
        crawler.__setitem__(assigns[-1], value)
        return value
    
    def create(self):
        self.sim.create(self.netParams, self.cfg)

    def simulate(self):
        self.sim.simulate()
    
    def save(self):
        self.sim.saveData()


