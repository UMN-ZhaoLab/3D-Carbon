import numpy as np
import json
import sys

with open("../parameters/configs/die_yield.json", 'r') as f:
    yield_config = json.load(f)



def L_average(N_g,p):
    return 2/9*(1-np.power(4,p-1))/(1-np.power(N_g,p-1))*\
        ((7*np.power(N_g,p-0.5)-1)/(np.power(4,p-0.5))-(1-np.power(N_g,p-1.5))/(1-np.power(4,p-1.5)))


def N_metal(n_g,p,area,feature_size,fan_out=4,eta=0.3):
    wire_pitch=3.6*feature_size
    return fan_out*n_g*L_average(n_g,p)*wire_pitch/(eta*area)




class die:
    def __init__(self,tech:int,name='None',beta=400*1e6,area=0,p1=0.525,feature_size=0,gnumber=0,wafer_diam=300,layer=0,layer_sensitive=1,TSVexsist=0,neighborgnumber=0,IO=0):
        with open("../parameters/configs/layer_config.json", 'r') as f:
            layer_config= json.load(f)
        key=str(tech)+'nm'
        self.areaestimate=0
        self.name=name
        IO_pitch=0.014
        TSV_pitch=0.0001
        
        if tech not in [3,5,7,8,10,12,14,20,28]:
            raise ValueError("technode(nm) is out of range")
        key=str(tech)+'nm'
        alpha=yield_config[key][1]
        D0=yield_config[key][0]
        self.gnumber=gnumber
        self.layer_sensitive=layer_sensitive
        self.IO=IO
        self.TSVexist=TSVexsist
        if not feature_size :
                self.feature_size=tech*1e-9
        # gnumber and area must need one
        if not gnumber and not area:
            raise ValueError("At least one of parameter 'gate number' or 'area' must be provided")
        else:
            
            if not gnumber :
               
                self.gnumber=area/(self.feature_size**2*beta)
            
            
            
            if not area :
                self.areaestimate=1
                if not IO: # If no IO value is given, the default area occupied by IO is 10%
                    self.area=gnumber*beta*self.feature_size**2*1.1 #mm*2
                else: self.area=gnumber*beta*self.feature_size**2+IO*IO_pitch
                if TSVexsist:
                    connect=4/(4+1)
                    k=4
                    p2=0.61
                    X_TSV=connect*k*(gnumber+neighborgnumber)*(1-(gnumber+neighborgnumber)**(p2-1))-connect*k*gnumber*(1-gnumber**(p2-1))-connect*k*neighborgnumber*(1-neighborgnumber**(p2-1))
                    self.area+=X_TSV*TSV_pitch
            else: self.area=area

            self.p=p1
            self.beta=beta
            # Calculate area by gnumber area+IO area+TSV area
            self.metallength=L_average(self.gnumber,p1)
            if not layer:
               self.layer=min(layer_config[key]+3,int(N_metal(self.gnumber,p1,self.area,self.feature_size)+1))
            else: self.layer=layer
            self.Yield=(1+self.area*D0/alpha)**(-alpha) ## compute yield
            self.tech=tech
            self.alpha=alpha
            self.waferdiam=wafer_diam
            self.D0=D0
            self.DPW=int(((np.pi*wafer_diam**2/4/self.area)-np.pi*wafer_diam/(np.sqrt(2*self.area))))
            self.neighborgnumber=neighborgnumber
    
    def setarea(self):
        IO_pitch=0.014
        TSV_pitch=0.0001
        if  self.areaestimate :
                if not self.IO: # If no IO value is given, the default area occupied by IO is 10%
                    self.area=self.gnumber*self.beta*self.feature_size**2*1.1 #mm*2
                else: self.area=self.gnumber*self.beta*self.feature_size**2+self.IO*IO_pitch
                if self.TSVexsist:
                    connect=4/(4+1)
                    k=4
                    p2=0.61
                    X_TSV=connect*k*(self.gnumber+self.neighborgnumber)*(1-(self.gnumber+self.neighborgnumber)**(p2-1))-connect*k*self.gnumber*(1-self.gnumber**(p2-1))-connect*k*self.neighborgnumber*(1-self.neighborgnumber**(p2-1))
                    self.area+=X_TSV*TSV_pitch
                    self.Yield=(1+self.area*self.D0/self.alpha)**(-self.alpha) ## compute yield
                    self.DPW=int(((np.pi*self.waferdiam**2/4/self.area)-np.pi*self.waferdiam/(np.sqrt(2*self.area))))



    def __str__(self) -> str:
        return f"tech:{self.feature_size},tech:{self.tech},area:{self.area},die num:{self.DPW},yield{self.Yield},layer{self.layer},gnumber{self.gnumber*1e-9}B,{self.neighborgnumber}"


