# hack workaround to NetPyNE stuff.
class Sim_Wrapper(object): # basically the __init__.py from netpyne/sim ....
    # import loading functions
    from netpyne.sim import *

    def close(self):