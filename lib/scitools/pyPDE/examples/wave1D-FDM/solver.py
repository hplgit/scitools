
import py4cs.PrmDictBase
class Data(py4cs.PrmDictBase.PrmDictBase):
    def __init__(self, **kwargs):
        py4cs.PrmDictBase.PrmDictBase.__init__(self)

        # define our set of physical and numerical parameters:
        self.physical_prm = {'L': 1.0, 'c': 1.0}
        self.numerical_prm = {'n': 11, 'dt': 0, 'tstop': 3}

        # attach dictionaries to base class list (required):
        self._prm_list = [self.physical_prm, self.numerical_prm]

        # specify parameters to be type checked when set:
        self._type_check.update({'n': True, 'dt': (float,)})

        # disallow arbitrary meta data
        self.user_prm = None # set to {} if meta data are allowed

        # initialize parameters according to keyword arguments:
        self.set(**kwargs)
        
    
