import pandas
import itertools
def batchify( batch_dict = {}, bin_size = 1, filename = "batch" ):
    """
    batch_dict = {string: generator values}
    """
    bin_num = 0
    curr_size = 0
    curr_batch = []
    for batch in dcx(**batch_dict):
        batch.update()
        curr_batch.append()



def dcx(**kwargs):
    """
    Dictionary preserving Cartesian (x) product
    https://stackoverflow.com/questions/5228158/cartesian-product-of-a-dictionary-of-lists
    """
    for instance in itertools.product(*kwargs.values()):
        yield dict(zip(kwargs.keys(), instance))



class batcher(object): # from a netParams create a pandas series of values (based on iterators?)
    netParams = object()
    cfg = object()
    grepfunc = staticmethod(lambda map_string: 'NETM' in map_string)
    def __init__(self):
        self.map_strings = [os.environ[map_string] for map_string in os.environ if self.grepfunc(map_string)]
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
        assign_path, value = [s.strip() for s in map_string.split('=')]
        assigns = assign_path.split('.')
        try:
            value = float(value)
        except:
            pass
        # crawl assigns array
        crawler = self.__getitem__(assigns[0])
        for gi in assigns[1:-1]:
            crawler = crawler.__getitem__(gi)
        
        crawler.__setitem__(assigns[-1], value)
        self.maps[assign_path] = value # json does not accept tuple() as keys. 
        
    def get_maps(self):
        return self.maps
    
    def create(self):
        self.sim.create(self.netParams, self.cfg)

    def simulate(self):
        self.sim.simulate()
    
    def save(self):
        self.sim.saveData()


