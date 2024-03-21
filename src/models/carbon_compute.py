# %%
import numpy as np
import json
import sys
from models.die import die
from models.substrate import Si,RDL

with open("../parameters/configs/bonding_yield.json", 'r') as f:
            bonding_yield = json.load(f)
with open("../parameters/configs/scaling_factors.json", 'r') as f:
            scaling = json.load(f)
with open("../parameters/packaging/epa_package.json", 'r') as f:
            Package_EPA = json.load(f)
with open("../parameters/packaging/epa_bonding.json", 'r') as f:
            Bonding_EPA = json.load(f)
with open("../parameters/packaging/epa_substrate.json", 'r') as f:
            substrate_EPA = json.load(f)
with open("../parameters/logic/epa.json", 'r') as f:
            EPA = json.load(f)
with open("../parameters/logic/gpa.json", 'r') as f:
            GPA = json.load(f)
with open("../parameters/logic/mpa.json", 'r') as f:
            MPA = json.load(f)
with open("../parameters/logic/epa_BEOL_perlayer.json", 'r') as f:
            BEPL_EPA = json.load(f)
with open("../parameters/configs/die_yield.json", 'r') as f:
            yield_config= json.load(f)
with open("../parameters/configs/layer_config.json", 'r') as f:
            layer_config= json.load(f)
with open("../parameters/carbon_intensity/manufacturing_location.json", 'r') as f:
            carbon_intensity_config= json.load(f)  
wafer_area=900*np.pi/4


# %%
def die_carbon(dies,number,carbon_intensity,TSV_sensitive=0):
    if not TSV_sensitive:TSV_carbon=0
    else:TSV_carbon=Bonding_EPA["TSV"]*carbon_intensity*dies.area*(number+TSV_sensitive-2)
    key=str(dies.tech)+'nm'
    if dies.layer_sensitive:
        layer_delta=dies.layer-layer_config[key]
        gamma=(EPA[key]+layer_delta*BEPL_EPA[key])/EPA[key]
        diecarbon=((((EPA[key]+layer_delta*BEPL_EPA[key])*carbon_intensity+gamma*GPA[key]+MPA[key])*wafer_area/dies.DPW/dies.Yield))*number+TSV_carbon
    else: diecarbon=((((EPA[key])*carbon_intensity+GPA[key]+MPA[key])*wafer_area/dies.DPW/dies.Yield))*number+TSV_carbon
    return(diecarbon)

def die_carbon_without_yield(dies,number,carbon_intensity,TSV_sensitive=0):
    key=str(dies.tech)+'nm'
    if not TSV_sensitive:TSV_carbon=0
    else:TSV_carbon=Bonding_EPA["TSV"]*carbon_intensity*dies.area*(number+TSV_sensitive-2)
    if dies.layer_sensitive:
        layer_delta=dies.layer-layer_config[key]
        gamma=(EPA[key]+layer_delta*BEPL_EPA[key])/EPA[key]
        diecarbon=(((EPA[key]+layer_delta*BEPL_EPA[key])*carbon_intensity+gamma*GPA[key]+gamma*MPA[key])*wafer_area/dies.DPW)*number+TSV_carbon
    else: diecarbon=(((EPA[key])*carbon_intensity+GPA[key]+MPA[key])*wafer_area/dies.DPW)*number+TSV_carbon
    return(diecarbon)

def interposer_carbon(interposer,carbon_intensity):
    
    diecarbon=(((EPA["interposer"])*carbon_intensity+MPA["interposer"])*wafer_area/interposer.DPW/interposer.Yield)
    return(diecarbon)
class MCM:
    def __init__(self,die_dict:dict,Manufacturing_location="world",packagearea=0):
        self.diedict=die_dict
        carbon_intensity=carbon_intensity_config[Manufacturing_location]
        diecarbon=[]
        self.diefootprint=0
        for dies in die_dict:
            key=str(dies.tech)+'nm'
            diedata=die_carbon(dies,die_dict[dies],carbon_intensity)
            diecarbon.append(diedata)
            self.diefootprint+=dies.area*die_dict[dies]
        self.diecarbon=diecarbon
        if not packagearea:
            self.packagearea=self.diefootprint*scaling["package"]
        else:self.packagearea=packagearea
        self.packagecarbon=self.packagearea*Package_EPA['FCBGA']*carbon_intensity
        self.carbon=np.sum(self.diecarbon)+self.packagecarbon
        self.carbonbreak=[np.sum(self.diecarbon),0,0,self.packagecarbon]
        
    def __str__(self) -> str:
        str1=""
        i=0
        
        for dies in self.diedict:
            str1=str1+dies.name+": {:.2f} kg, ".format(self.diecarbon[i]/1000)
            i+=1
        return str1+"package: {:.2f} kg, ".format(self.packagecarbon/1000)+"overall embodied carbon: {:.2f} kg ".format((np.sum(self.diecarbon)+self.packagecarbon)/1000)


class InFO_chipfirst:
    def __init__(self,die_dict:dict,Manufacturing_location="world",substratearea=0,packagearea=0):
        self.diedict=die_dict
        carbon_intensity=carbon_intensity_config[Manufacturing_location]
        diecarbon=[]
        self.dienumber=0
        self.diefootprint=0
        for dies in die_dict:
            self.diefootprint+=dies.area*die_dict[dies]
            self.dienumber+=die_dict[dies]
        if not substratearea:
            self.substratearea=self.diefootprint*scaling["RDL"]
        self.substrate=RDL(self.substratearea)
        for dies in die_dict:
            key=str(dies.tech)+'nm'
            diedata=die_carbon(dies,die_dict[dies],carbon_intensity)/self.substrate.Yield
            diecarbon.append(diedata)
        self.diecarbon=diecarbon
        self.substratecarbon=self.substratearea*carbon_intensity*substrate_EPA['RDL']/self.substrate.Yield
        if not packagearea:
            self.packagearea=self.diefootprint*scaling["package"]
        else:self.packagearea=packagearea
        self.packagecarbon=self.packagearea*Package_EPA['FCBGA']*carbon_intensity
        self.carbonbreak=[np.sum(self.diecarbon),0,self.substratecarbon,self.packagecarbon]
        self.carbon=np.sum(self.diecarbon)+self.packagecarbon+self.substratecarbon
        
    def __str__(self) -> str:
        str1=""
        i=0
        for dies in self.diedict:
            str1=str1+dies.name+":{:.2f} kg, ".format(self.diecarbon[i]/1000)
            i+=1
        return str1+"substrate: {:.2f} kg, ".format(self.substratecarbon/1000)+"package: {:.2f} kg, ".format(self.packagecarbon/1000)+"overall embodied carbon: {:.2f} kg".format((np.sum(self.diecarbon)+self.packagecarbon+self.substratecarbon)/1000)



class InFO_chiplast:
    def __init__(self,die_dict:dict,Manufacturing_location="world",substratearea=0,packagearea=0):
        self.diedict=die_dict
        carbon_intensity=carbon_intensity_config[Manufacturing_location]
        diecarbon=[]
        self.dienumber=0
        self.diefootprint=0
        for dies in die_dict:
            self.diefootprint+=dies.area*die_dict[dies]
            self.dienumber+=die_dict[dies]
        if not substratearea:
            self.substratearea=self.diefootprint*scaling["RDL"]
        self.substrate=RDL(self.substratearea)
        self.bondingyield=bonding_yield["Bumping_D2W"]**(self.dienumber)
        for dies in die_dict:
            key=str(dies.tech)+'nm'
            diedata=die_carbon(dies,die_dict[dies],carbon_intensity)/self.bondingyield
            diecarbon.append(diedata)

        self.diecarbon=diecarbon
        self.bondingcarbon=self.substratearea*Bonding_EPA["TCB"]/self.bondingyield
        self.substratecarbon=self.substratearea*carbon_intensity*substrate_EPA['RDL']/self.substrate.Yield/self.bondingyield
        if not packagearea:
            self.packagearea=self.diefootprint*scaling["package"]
        else:self.packagearea=packagearea
        self.packagecarbon=self.packagearea*Package_EPA['FCBGA']*carbon_intensity
        self.carbonbreak=[np.sum(self.diecarbon),self.bondingcarbon,self.substratecarbon,self.packagecarbon]
        self.carbon=(np.sum(self.diecarbon)+self.bondingcarbon+self.packagecarbon+self.substratecarbon)
        
    def __str__(self) -> str:
        str1=""
        i=0
        for dies in self.diedict:
            str1=str1+dies.name+":{:.2f} kg, ".format(self.diecarbon[i]/1000)
            i+=1
        return str1+"substrate: {:.2f} kg, ".format(self.substratecarbon/1000)+"bonding {:.2f} kg, ".format(self.bondingcarbon/1000)+"package: {:.2f} kg, ".format(self.packagecarbon/1000)+"overall embodied carbon: {:.2f} kg".format((np.sum(self.diecarbon)+self.bondingcarbon+self.packagecarbon+self.substratecarbon)/1000)

class EMIB:
    def __init__(self,die_dict:dict,Manufacturing_location="world",substratearea=0,packagearea=0):
        self.diedict=die_dict
        L_embi=4
        carbon_intensity=carbon_intensity_config[Manufacturing_location]
        diecarbon=[]
        self.dienumber=0
        self.diefootprint=0
        for dies in die_dict:
            self.diefootprint+=dies.area*die_dict[dies]
            self.dienumber+=die_dict[dies]
        if not substratearea:
            self.substratearea=4*4
        self.substrate=Si(self.substratearea)
        self.bondingyield=bonding_yield["Bumping_D2W"]**(self.dienumber)
        for dies in die_dict:
            key=str(dies.tech)+'nm'
            diedata=die_carbon(dies,die_dict[dies],carbon_intensity)/self.bondingyield
            diecarbon.append(diedata)
        self.diecarbon=diecarbon
        self.bondingcarbon=self.substratearea*Bonding_EPA["TCB"]/self.bondingyield
        self.substratecarbon=interposer_carbon(self.substrate,carbon_intensity)*L_embi*self.dienumber
        if not packagearea:
            self.packagearea=self.diefootprint*scaling["package"]
        else:self.packagearea=packagearea
        self.packagecarbon=self.packagearea*Package_EPA['FCBGA']*carbon_intensity
        self.carbonbreak=[np.sum(self.diecarbon),0,self.substratecarbon,self.packagecarbon]

        self.carbon=np.sum(self.diecarbon)+self.packagecarbon+self.substratecarbon
        
    def __str__(self) -> str:
        str1=""
        i=0
        for dies in self.diedict:
            str1=str1+dies.name+": {:.2f} kg, ".format(self.diecarbon[i]/1000)
            i+=1
        return str1+"substrate: {:.2f} kg, ".format(self.substratecarbon/1000)+"package: {:.2f} kg, ".format(self.packagecarbon/1000)+"overall embodied carbon: {:.2f} kg ".format((np.sum(self.diecarbon)+self.packagecarbon+self.substratecarbon)/1000)

class Si_int:
    def __init__(self,die_dict:dict,Manufacturing_location="world",substratearea=0,packagearea=0):
        self.diedict=die_dict
        carbon_intensity=carbon_intensity_config[Manufacturing_location]
        diecarbon=[]
        self.dienumber=0
        self.diefootprint=0
        for dies in die_dict:
            self.diefootprint+=dies.area*die_dict[dies]
            self.dienumber+=die_dict[dies]
        if not substratearea:
            self.substratearea=self.diefootprint*scaling["Si"]
        self.substrate=Si(self.substratearea)
        self.bondingyield=bonding_yield["Bumping_D2W"]**(self.dienumber)
        for dies in die_dict:
            key=str(dies.tech)+'nm'
            diedata=die_carbon(dies,die_dict[dies],carbon_intensity)/self.bondingyield
            diecarbon.append(diedata)
        self.diecarbon=diecarbon
        self.bondingcarbon=self.substratearea*Bonding_EPA["TCB"]/self.bondingyield
        self.substratecarbon=interposer_carbon(self.substrate,carbon_intensity)
        if not packagearea:
            self.packagearea=self.diefootprint*scaling["package"]
        else:self.packagearea=packagearea
        self.packagecarbon=self.packagearea*Package_EPA['FCBGA']*carbon_intensity
        self.carbonbreak=[np.sum(self.diecarbon),0,self.substratecarbon,self.packagecarbon]

        self.carbon=np.sum(self.diecarbon)+self.packagecarbon+self.substratecarbon
        
    def __str__(self) -> str:
        str1=""
        i=0
        for dies in self.diedict:
            str1=str1+dies.name+": {:.2f} kg, ".format(self.diecarbon[i]/1000)
            i+=1
        return str1+"substrate: {:.2f} kg, ".format(self.substratecarbon/1000)+"package: {:.2f} kg, ".format(self.packagecarbon/1000)+"overall embodied carbon: {:.2f} kg ".format((np.sum(self.diecarbon)+self.packagecarbon+self.substratecarbon)/1000)

class Micro_bumping:
    def __init__(self,die_dict:dict,Manufacturing_location="world",packagearea=0,method="D2W",F2F_F2B="F2B"):
        
        self.diedict=die_dict
        carbon_intensity=carbon_intensity_config[Manufacturing_location]
        diecarbon=[]
        self.dienumber=0
        self.diefootprint=list(die_dict.keys())[0].area
        i=0
        keys=list(die_dict.keys())
        if F2F_F2B=="F2F":
            
            for dies in die_dict:
                #if die_dict[dies]>1 :raise ValueError("In 3D integration please write each die clearly in order from bottom to top (even if the nature of the die is the same), the method of die number cannot be used ")
                if i==0:
                    dies.TSVexsist=1
                    dies.neighborgnumber=keys[i+1].gnumber
                    dies.setarea()
                elif i!=1:
                    dies.TSVexsist=1
                    dies.neighborgnumber=keys[i-1].gnumber
                    dies.setarea()
               

        elif F2F_F2B=="F2B":
            
            for dies in die_dict:
                
                #if die_dict[dies]>1 :raise ValueError("In 3D integration please write each die clearly in order from bottom to top (even if the nature of the die is the same), the method of die number cannot be used ")
                if i!=len(keys)-1:
                    dies.TSVexsist=1
                    dies.neighborgnumber=keys[i-1].gnumber
                    dies.setarea()
                i+=1
                

        else: raise ValueError("F2F/F2B methods must in F2F or F2B!")
        
        if method=="W2W":
            self.dieyield=1
            for dies in die_dict:
                
                self.dieyield*=dies.Yield**die_dict[dies]
                self.dienumber+=die_dict[dies]

            self.bondingyield=bonding_yield["Bumping_W2W"]**(self.dienumber)
            i=0
            for dies in die_dict:
                if i==0:
                     diedata=die_carbon_without_yield(dies,die_dict[dies],carbon_intensity,TSV_sensitive=1)/self.bondingyield/self.dieyield
                else:diedata=die_carbon_without_yield(dies,die_dict[dies],carbon_intensity,TSV_sensitive=2)/self.bondingyield/self.dieyield
                diecarbon.append(diedata)
                i+=1

            self.diecarbon=diecarbon
            self.bondingcarbon=self.diefootprint*Bonding_EPA["TCB"]*carbon_intensity/self.bondingyield/self.dieyield
            if not packagearea:
                self.packagearea=self.diefootprint*scaling["package"]
            else:self.packagearea=packagearea
            self.packagecarbon=self.packagearea*Package_EPA['WLCSP']*carbon_intensity
        elif method=="D2W":
            self.dieyield=1
            for dies in die_dict:
                
                self.dieyield*=dies.Yield**die_dict[dies]
            self.bondingyield=bonding_yield["Bumping_D2W"]**(self.dienumber)
            i=0
            self.bondingcarbon=0
            for dies in die_dict:
                
                if i==0:
                     # if first die group,the first one no need TSV
                     diedata=die_carbon(dies,die_dict[dies],carbon_intensity,TSV_sensitive=1)/self.bondingyield
                # else all need TSV
                else:diedata=die_carbon(dies,die_dict[dies],carbon_intensity,TSV_sensitive=2)/self.bondingyield
                self.bondingcarbon+=dies.area*Bonding_EPA["TCB"]*carbon_intensity/self.bondingyield/dies.Yield
                diecarbon.append(diedata)
                i+=1
                
            self.diecarbon=diecarbon
            if not packagearea:
                self.packagearea=self.diefootprint*scaling["package"]
            else:self.packagearea=packagearea
            self.packagecarbon=self.packagearea*Package_EPA['WLCSP']*carbon_intensity
        else: raise ValueError("The bonding method must be D2W or W2W")
        self.carbonbreak=[np.sum(self.diecarbon),self.bondingcarbon,0,self.packagecarbon]
        self.carbon=np.sum(self.diecarbon)+self.packagecarbon+self.bondingcarbon
    def __str__(self) -> str:
        str1=""
        i=0
        for dies in self.diedict:
            str1=str1+dies.name+": {:.2f} kg,".format(self.diecarbon[i]/1000)
            i+=1
        return str1+"bonding: {:.2f} kg,".format(self.bondingcarbon/1000)+"package: {:.2f} kg, ".format(self.packagecarbon/1000)+"overall embodied carbon: {:.2f} kg".format((np.sum(self.diecarbon)+self.packagecarbon+self.bondingcarbon)/1000)
    
class Hybrid_bonding:
    def __init__(self,die_dict:dict,Manufacturing_location="world",packagearea=0,method="D2W",test=0,F2F_F2B="F2B"):
        self.test=test #Determine whether it is a test case
        self.diedict=die_dict
        i=0
        keys=list(die_dict.keys())
        if F2F_F2B=="F2F":
            
            for dies in die_dict:
                #if die_dict[dies]>1 :raise ValueError("In 3D integration please write each die clearly in order from bottom to top (even if the nature of the die is the same), the method of die number cannot be used ")
                if i==0:
                    dies.TSVexsist=1
                    dies.neighborgnumber=keys[i+1].gnumber
                    dies.setarea()
                elif i!=1:
                    dies.TSVexsist=1
                    dies.neighborgnumber=keys[i-1].gnumber
                    dies.setarea()
               

        elif F2F_F2B=="F2B":
            
            for dies in die_dict:
                
                #if die_dict[dies]>1 :raise ValueError("In 3D integration please write each die clearly in order from bottom to top (even if the nature of the die is the same), the method of die number cannot be used ")
                if i!=len(keys)-1:
                    dies.TSVexsist=1
                    dies.neighborgnumber=keys[i-1].gnumber
                    dies.setarea()
                i+=1
        
                
            
        else: raise ValueError("F2F/F2B methods must in F2F or F2B!")
                 
             
        carbon_intensity=carbon_intensity_config[Manufacturing_location]
        diecarbon=[]
        self.dienumber=0
        self.diefootprint=0
        self.diefootprint=list(die_dict.keys())[0].area
        
        if method=="W2W":
            self.dieyield=1
            for dies in die_dict:
                
                self.dieyield*=dies.Yield**die_dict[dies]
                self.dienumber+=die_dict[dies]
            self.bondingyield=bonding_yield["Hybridbonding_W2W"]**(self.dienumber)
            i=0
            for dies in die_dict:
                if i==0:
                     diedata=die_carbon_without_yield(dies,die_dict[dies],carbon_intensity,TSV_sensitive=1)/self.bondingyield/self.dieyield
                else:diedata=die_carbon_without_yield(dies,die_dict[dies],carbon_intensity,TSV_sensitive=2)/self.bondingyield/self.dieyield
                diecarbon.append(diedata)
                i+=1
                
            self.diecarbon=diecarbon
            self.bondingcarbon=self.diefootprint*carbon_intensity*Bonding_EPA["DBI"]*(self.dienumber-1)/self.bondingyield/self.dieyield
            if not packagearea:
                self.packagearea=self.diefootprint*scaling["package"]
            else:self.packagearea=packagearea
            self.packagecarbon=self.packagearea*Package_EPA['FCBGA']*carbon_intensity
        elif method=="D2W":
            self.dieyield=1
            self.bondingcarbon=0
            for dies in die_dict:
                
                self.dieyield*=dies.Yield**die_dict[dies]
            self.bondingyield=bonding_yield["Hybridbonding_D2W"]
            i=0
            for dies in die_dict:
                t=dies.layer
                
                if i==0:
                     # if first die group,the first one no need TSV
                     diedata=die_carbon(dies,die_dict[dies],carbon_intensity,TSV_sensitive=1)/self.bondingyield
                # else all need TSV
                else:
                     dies.layer=int(dies.layer*2/3)
                     diedata=die_carbon(dies,die_dict[dies],carbon_intensity,TSV_sensitive=2)/self.bondingyield
                self.bondingcarbon+=dies.area*Bonding_EPA["DBI"]*carbon_intensity/self.bondingyield/dies.Yield
                diecarbon.append(diedata)
                i+=1
                dies.layer=t
               
            self.diecarbon=diecarbon
            if not packagearea:
                self.packagearea=self.diefootprint*scaling["package"]
            else:self.packagearea=packagearea
            self.packagecarbon=self.packagearea*Package_EPA['FCBGA']*carbon_intensity
        else: raise ValueError("The bonding method must be D2W or W2W")
        if self.test: self.carbon=(np.sum(self.diecarbon)+self.packagecarbon+self.bondingcarbon)*1000
        
        else: self.carbon=np.sum(self.diecarbon)+self.packagecarbon+self.bondingcarbon
        self.carbonbreak=[np.sum(self.diecarbon),self.bondingcarbon,0,self.packagecarbon]
    def __str__(self) -> str:
        str1=""
        i=0
        
        if self.test:  
            for dies in self.diedict:
                str1=str1+dies.name+": {:.2f} kg, ".format(self.diecarbon[i])
                i+=1  
            return str1+"bonding: {:.1f} kg, ".format(self.bondingcarbon)+"package: {:.1f} kg, ".format(self.packagecarbon)+"overall embodied carbon: {:.1f} kg ".format((np.sum(self.diecarbon)+self.packagecarbon+self.bondingcarbon))
        else:
             for dies in self.diedict:
                str1=str1+dies.name+": {:.2f} kg, ".format(self.diecarbon[i]/1000)
                i+=1  
             return str1+"bonding: {:.2f} kg, ".format(self.bondingcarbon/1000)+"package: {:.2f} kg, ".format(self.packagecarbon/1000)+"overall embodied carbon: {:.2f} kg".format((np.sum(self.diecarbon)+self.packagecarbon+self.bondingcarbon)/1000)
   

class Monolithic3D:
    def __init__(self,die_dict:dict,Manufacturing_location="world",packagearea=0):
        
        self.diedict=die_dict
        carbon_intensity=carbon_intensity_config[Manufacturing_location]
        diecarbon=[]
        self.dienumber=0
        
        self.bondingcarbon=0
        self.dieyield=1
        self.diefootprint=list(die_dict.keys())[0].area*1.2
             
        if self.dienumber>2: 
             raise ValueError("The max size of monolithic 3D die is two!")
            
        self.bondingyield=bonding_yield["Monolithic"]**(self.dienumber)
        i=0
        for dies in die_dict:
            n=0.25
            d=1
            key=str(dies.tech)+'nm'
            alpha=yield_config[key][1]
            D0=yield_config[key][0]
            t1=dies.Yield
            if i==0: 
                dies.Yield=1/((1+n)*(1+dies.area*d*D0/alpha)**(n*alpha)*(1+dies.area*D0/alpha)**(alpha))
                t=dies.layer
                dies.layer=int(dies.layer*2/3)
                diedata=die_carbon(dies,1,carbon_intensity)
                #self.bondingcarbon+=dies.area*Bonding_EPA["TCB"]*carbon_intensity/self.bondingyield/self.dieyield
                diecarbon.append(diedata)
                dies.layer=t
            i+=1
            dies.Yield=t1
        self.bondingcarbon=0
            
        self.diecarbon=diecarbon
        if not packagearea:
            self.packagearea=self.diefootprint*scaling["package"]
        else:self.packagearea=packagearea
        self.packagecarbon=self.packagearea*Package_EPA['FCBGA']*carbon_intensity
        self.carbon=np.sum(self.diecarbon)+self.packagecarbon+self.bondingcarbon
        self.carbonbreak=[np.sum(self.diecarbon),self.bondingcarbon,0,self.packagecarbon]
    
        
    def __str__(self) -> str:
        str1=""
       
        for dies in self.diedict:
            str1=str1+dies.name+": {:.2f} kg, ".format(self.diecarbon[0]/1000)
        return str1+"bonding: {:.2f} kg, ".format(self.bondingcarbon/1000)+"package: {:.2f} kg, ".format(self.packagecarbon/1000)+"overall embodied carbon: {:.2f} kg".format((np.sum(self.diecarbon)+self.packagecarbon+self.bondingcarbon)/1000)