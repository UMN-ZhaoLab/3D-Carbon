import numpy as np
import json
import sys

with open("../parameters/configs/die_yield.json", 'r') as f:
    yield_config = json.load(f)


class Si:
    def __init__(self,area=0,wafer_diam=300):
        
        alpha=yield_config['Si'][1]
        D0=yield_config['Si'][0]

        self.area=area
        self.Yield=(1+self.area*D0/alpha)**(-alpha) ## compute yield
        self.DPW=int(((np.pi*wafer_diam**2/4/self.area)-np.pi*wafer_diam/(np.sqrt(2*self.area))))




class RDL:
    def __init__(self,area=0):
        
        alpha=yield_config['RDL'][1]
        D0=yield_config['RDL'][0]

        self.area=area
        self.Yield=(1+self.area*D0/alpha)**(-alpha) ## compute yield
        