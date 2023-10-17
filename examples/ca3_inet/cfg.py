from pubtk.runtk import NetpyneRunner

ca3 = NetpyneRunner()

cfg = ca3.get_cfg()

cfg.duration = 100
cfg.dt = 0.1
cfg.hparams = {'v_init': -65.0}
cfg.verbose = False
cfg.recordTraces = {}  # don't save this
cfg.recordStim = False
cfg.recordStep = 0.1            # Step size in ms to save data (eg. V traces, LFP, etc)
cfg.filename = '00'         # Set file output name
cfg.savePickle = False        # Save params, network and sim output to pickle file
cfg.saveDat = False
cfg.printRunTime = 0.1
cfg.recordLFP = None # don't save this

cfg.analysis['plotRaster'] = {'saveFig': True} # raster ok
cfg.analysis['plotTraces'] = { } # don't save this
cfg.analysis['plotLFPTimeSeries'] = { }  # don't save this

cfg.cache_efficient = True # better with MPI?
""" remove all of the unecessary data """
cfg.saveCellSecs = False
cfg.saveCellConns = False
cfg.flag = False

cfg.AMPA = 1
cfg.GABA = 1
cfg.NMDA = 1

ca3.set_mappings('cfg')