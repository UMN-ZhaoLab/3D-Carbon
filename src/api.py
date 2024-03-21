# %%
from models.die import die
from models.carbon_compute import MCM,InFO_chipfirst,InFO_chiplast,Si_int,Micro_bumping,Hybrid_bonding,Monolithic3D,EMIB
from models.die import die
import yaml
import json
import numpy as np
import matplotlib.pyplot as plt
#import pandas as pd

class api:
    def __init__(self,method,die_dict,Manufacturing_location="world",stacking="D2W",name="None",packagearea=0,test=0,F2F_F2B="F2B"):
        if name == "None":
            print("Here is overall embodied carbon breakdown: ")
        else :print("Here is ",name,"overall embodied carbon breakdown: ")
        if method=="MCM":
            if stacking=="D2W":
                ic=MCM(die_dict,Manufacturing_location=Manufacturing_location,packagearea=packagearea)
                self.carbon=ic.carbon
                print(ic)
            else: raise ValueError("the stacking of MCM must be D2W")
        elif method=="InFO_chip_first":
            if stacking=="D2W":
                ic=InFO_chipfirst(die_dict,Manufacturing_location=Manufacturing_location,packagearea=packagearea)
                self.carbon=ic.carbon
                print(ic)
                
            else: raise ValueError("the stacking of InFO chip-first must be D2W")
        elif method=="InFO_chip_last":
            if stacking=="D2W":
                ic=InFO_chiplast(die_dict,Manufacturing_location=Manufacturing_location,packagearea=packagearea)
                self.carbon=ic.carbon
                print(ic)
                
            else: raise ValueError("the stacking of InFO chip-last must be D2W")
        elif method=="Si_int":
            if stacking=="D2W":
                ic=Si_int(die_dict,Manufacturing_location=Manufacturing_location,packagearea=packagearea)
                self.carbon=ic.carbon
                print(ic)
            else: raise ValueError("the stacking of Si interposer must be D2W")
        elif method=="Micro_bumping":
            if stacking=="D2W":
                ic=Micro_bumping(die_dict,method="D2W",Manufacturing_location=Manufacturing_location,packagearea=packagearea,F2F_F2B=F2F_F2B)
                self.carbon=ic.carbon
                print(ic)
        
            elif stacking=="W2W":
                ic=Micro_bumping(die_dict,method="W2W",Manufacturing_location=Manufacturing_location,packagearea=packagearea,F2F_F2B=F2F_F2B)
                self.carbon=ic.carbon
                print(ic)
                
            else: raise ValueError("the stacking of Micro-bumping must be D2W or W2W")
        elif method=="Hybrid_bonding":
            if stacking=="D2W":
                ic=Hybrid_bonding(die_dict,method="D2W",Manufacturing_location=Manufacturing_location,packagearea=packagearea,test=test,F2F_F2B=F2F_F2B)
                self.carbon=ic.carbon
                print(ic)
                
            elif stacking=="W2W":
                ic=Hybrid_bonding(die_dict,method="W2W",Manufacturing_location=Manufacturing_location,packagearea=packagearea,test=test,F2F_F2B=F2F_F2B)
                self.carbon=ic.carbon
                print(ic)
                
            else: raise ValueError("the stacking of Hybrid bonding must be D2W or W2W")
        elif method=="Monolithic_3D":
            ic=Monolithic3D(die_dict,Manufacturing_location=Manufacturing_location,packagearea=packagearea)
            self.carbon=ic.carbon
            print(ic)
        
        else: print("No such Integration method!Please choose Integration method in MCM/InFO_chip_first/InFO_chip_last/Si_int/Micro_bumping/Hybrid_bonding/Monolithic_3D")
        
def performance(x):
    return 1-0.2*np.log2(x)-0.2    

class AV:
    def __init__(self,firedirection,option='homo',memorynode=28):
       
        avg_hrs_all_cars=0.79
        std_dev_mean_hrs_driven=0.03
        carbon_intensity_mean=310
        carbon_intensity_std_dev =25
        mu_Q = avg_hrs_all_cars # hrs per day
        sigma_Q = std_dev_mean_hrs_driven # mean_hrs_driven_norm_scale_fit # hrs per day
        # Parameters for I ~ Gaussian(mu_I, sigma_I)
        mu_I = carbon_intensity_mean # avg carbon intensity
        sigma_I = carbon_intensity_std_dev 
        mu_Ts=10
        mu_F=30
        bandwidth = np.zeros((9),dtype=float)
        self.option=option
        
        with open("../parameters/carbon_intensity/manufacturing_location.json", 'r') as f:
            carbon_intensity_config= json.load(f)  
        with open("../parameters/Delay/delay_scaling_factors.json", 'r') as f:
            delay_package= json.load(f) 
        with open("../parameters/Delay/delay_node_factors.json", 'r') as f:
            delay_node= json.load(f)  
        with open("../parameters/power_intensity/power_intensity.json", 'r') as f:
            powerintensity= json.load(f)  
        with open("../parameters/power_intensity/power_intensity.json", 'r') as f:
            powerscaling= json.load(f)
        with open("../parameters/delay/bandwidth.json", 'r') as f:
            bandwidth_file= json.load(f)  
        with open(firedirection, 'r') as file:
            datas = yaml.safe_load(file)
        int_band=[bandwidth_file["2D"],bandwidth_file["MCM"],bandwidth_file["InFO_chipfirst"],bandwidth_file["InFO_chiplast"],bandwidth_file["EMIB"],bandwidth_file["Si_int"],bandwidth_file["Micro_bumping"],bandwidth_file["Hybrid_bonding"],bandwidth_file["Monolithic3D"]]

        if option=='homo':
            for data in datas:
                self.name=data.get("Product","None")
                die_2d={}
                die_2_5d={}
                die_3d={}
                eta=data["energy_efficiency"]
                baseline=data["bandwidth-requirement"]
                self.baseline=baseline
                die_2d1=die(data["technode(nm)"],name=data.get("name","die"),gnumber=data.get("gatenumber",0),area=data.get("area(mm2)",0),feature_size=data.get("feature_size",0),layer=data.get("layer",0),layer_sensitive=data.get("layer_sensitive",1),IO=data.get("IO_number",0))
                die_2_5d1=die(tech=die_2d1.tech,area=die_2d1.area*1.1/2,gnumber=die_2d1.gnumber)
                die_3d1=die(tech=die_2d1.tech,area=die_2d1.area/2,gnumber=die_2d1.gnumber)
                die_2d.update({die_2d1:1})
                die_2_5d.update({die_2_5d1:2})
                die_3d.update({die_3d1:2})
                mono2d=MCM(die_2d,Manufacturing_location='Taiwan')
                mcm=MCM(die_2_5d,Manufacturing_location='Taiwan')
                si=Si_int(die_2_5d,Manufacturing_location='Taiwan')
                emib=EMIB(die_2_5d,Manufacturing_location='Taiwan')
                info_first=InFO_chipfirst(die_2_5d,Manufacturing_location='Taiwan')
                info_last=InFO_chiplast(die_2_5d,Manufacturing_location='Taiwan')
                microbump=Micro_bumping(die_2_5d,Manufacturing_location='Taiwan')
                hybrid=Hybrid_bonding(die_3d,Manufacturing_location='Taiwan')
                monolithic=Monolithic3D(die_3d,Manufacturing_location='Taiwan')
                
                
                length=3*np.sqrt(die_2_5d1.area)
                energy=[1,0.5,0.25,0.25,0.15,0.12]
               
                data = np.zeros((9,5),dtype=float)

                
                power_target=0.78/1000*mu_I*mu_Ts*mu_F*0.006*200*365*10*0.34/eta*8

                data[0][:-1]=mono2d.carbonbreak
                data[1][:-1]=mcm.carbonbreak
                data[2][:-1]=info_first.carbonbreak
                data[3][:-1]=info_last.carbonbreak
                data[4][:-1]=emib.carbonbreak
                data[5][:-1]=si.carbonbreak
                data[6][:-1]=microbump.carbonbreak
                data[7][:-1]=hybrid.carbonbreak
                data[8][:-1]=monolithic.carbonbreak
                MCM_interband=49
                for j in range(1,6):
                    data[j][-1]=power_target
                    bandwidth[j]=min(10,length*int_band[j]/(int_band[1]*MCM_interband))
                data[0][-1]=power_target
                bandwidth[0]=10
                for j in range(6,9):
                    data[j][-1]=power_target
                    bandwidth[j]=10
                for j in range(1,6):

                    
                    rp=min(1,performance(baseline/bandwidth[j]))
                    #print(rp)
                    data[j][-1]*=1.1*(power_target+energy[j]*8*8*bandwidth[j]/rp)/power_target
                data[6][-1]*=1.1
                data[7][-1]/=1.09
                data[8][-1]/=1.21
                

                
        elif  option=='heter':
            for data in datas:
                die_2d={}
                die_2_5d={}
                die_3d={}
                self.name=data.get("Product","None")
                eta=data["energy_efficiency"]
                baseline=data["bandwidth-requirement"]
                self.baseline=baseline
                die_2d1=die(data["technode(nm)"],name=data.get("name","die"),gnumber=data.get("gatenumber",0),area=data.get("area(mm2)",0),feature_size=data.get("feature_size",0),layer=data.get("layer",0),layer_sensitive=data.get("layer_sensitive",1),IO=data.get("IO_number",0))
                die_2_5d1=die(tech=die_2d1.tech,area=die_2d1.area*0.88,gnumber=die_2d1.gnumber*0.9)
                die_2_5d2=die(tech=memorynode,area=die_2d1.area*0.22,gnumber=die_2d1.gnumber*0.1)
                die_3d1=die(tech=die_2d1.tech,area=die_2d1.area*0.8,gnumber=die_2d1.gnumber)
                die_3d2=die(tech=memorynode,area=die_2d1.area*0.2,gnumber=die_2d1.gnumber)
                die_2d.update({die_2d1:1,})
                die_2_5d.update({die_2_5d1:1,die_2_5d2:1})
                die_3d.update({die_3d1:1,die_3d2:1})
                mono2d=MCM(die_2d,Manufacturing_location='Taiwan')
                mcm=MCM(die_2_5d,Manufacturing_location='Taiwan')
                si=Si_int(die_2_5d,Manufacturing_location='Taiwan')
                emib=EMIB(die_2_5d,Manufacturing_location='Taiwan')
                info_first=InFO_chipfirst(die_2_5d,Manufacturing_location='Taiwan')
                info_last=InFO_chiplast(die_2_5d,Manufacturing_location='Taiwan')
                microbump=Micro_bumping(die_2_5d,Manufacturing_location='Taiwan')
                hybrid=Hybrid_bonding(die_3d,Manufacturing_location='Taiwan')
                monolithic=Monolithic3D(die_3d,Manufacturing_location='Taiwan')
                
                
                length=3*np.sqrt(die_3d1.area)
                energy=[1,0.5,0.25,0.25,0.15,0.12]
               
                data = np.zeros((9,5),dtype=float)

                
                power_target=0.78/1000*mu_I*mu_Ts*mu_F*0.006*200*365*10*0.34/eta*8
                #print(0.78/1000*mu_I*mu_Ts*mu_F*0.006*200*365*10*0.34*8)

                data[0][:-1]=mono2d.carbonbreak
                data[1][:-1]=mcm.carbonbreak
                data[2][:-1]=info_first.carbonbreak
                data[3][:-1]=info_last.carbonbreak
                data[4][:-1]=emib.carbonbreak
                data[5][:-1]=si.carbonbreak
                data[6][:-1]=microbump.carbonbreak
                data[7][:-1]=hybrid.carbonbreak
                data[8][:-1]=monolithic.carbonbreak
                MCM_interband=52
                for j in range(1,6):
                    data[j][-1]=power_target
                    bandwidth[j]=min(10,length*int_band[j]/(int_band[1]*MCM_interband))
                data[0][-1]=power_target
                bandwidth[0]=10
                for j in range(6,9):
                    data[j][-1]=power_target
                    bandwidth[j]=10
                    
                for j in range(1,6):

                    
                    rp=min(1,performance(baseline/bandwidth[j]))
                    #print(rp)
                    data[j][-1]*=1.1*(power_target+energy[j]*8*8*bandwidth[j]/rp)/power_target
                data[6][-1]*=1.1
                data[7][-1]/=1.09
                data[8][-1]/=1.21
                

        self.data=data
        self.bandwidth=bandwidth
    def print_name(self):
        print("Here is design exploration result of "+self.name+" ==> ")
        

    def print_result(self):
            labels=[ 'Integration','MCM', 'InFO_1', 'InFO_2', 'EMIB','Si_ini', 'Micro', 'Hybrid', 'M3D']
            
            #if self.option=="homo":
                #print("In homogeneous architecture:")
            #if self.option=="heter":
               # print("In  heterogeneous architecture:")
                
            for i in range(1,9):
                #print("For "+labels[i]+" method: ","die: {:.2f} kg,".format(self.data[i][0]/1000)+"bonding: {:.2f} kg,".format(self.data[i][1]/1000)+"substrate: {:.2f} kg,".format(self.data[i][2]/1000)+"packaging: {:.2f} kg, ".format(self.data[i][3]/1000)+"overall embodied carbon: {:.2f} kg, ".format((np.sum(self.data[i][:-1])/1000))+"operational carbon: {:.2f} kg.".format(self.data[i][-1]/1000))
                #if self.bandwidth[i]>self.baseline:
                #    print("Bandwidth is: {:.2} TB/s".format(self.bandwidth[i])+", meet the bandwidth requirement.")
               # if self.bandwidth[i]<self.baseline:
                '''
                    print("Bandwidth is: {:.2} TB/s".format(self.bandwidth[i])+", don't meet the bandwidth requirement!!!")
                    print("Embodied carbon save ratio is : {:.1} years".format(sum(self.data[i][:-1])-sum(self.data[0][:-1])/sum(self.data[0][:-1])))
                    print("Overall carbon save ratio is : {:.1} years".format((self.data[i][-1]-self.data[0][-1])/(self.data[0][-1])))
                    print("Choosing metric is : {:.1} years".format(sum(self.data[i][:-1])-sum(self.data[0][:-1])/sum(self.data[0][:-1])-sum(self.data[i][:-1])))
                    print("Replacing metric is : {:.1} years".format(sum(self.data[i][:-1])/(self.data[0][-1]-self.data[i][-1])))
                '''
            #columns = ["2D", "MCM", "InFO_chipfirst", "InFO_chiplast", "EMIB", "Si_int", "Micro_bumping", "Hybrid_bonding", "Monolithic3D"]
            rows = ["Embodied carbon save ratio", "", "Overall carbon save ratio", "Choosing metric(years)", "Replacing metric(years)"]

            # 创建一个空的数据列表，用于填充表格。这里我们使用空字符串作为占位符
            data = [["" for _ in range(len(labels))] for _ in range(len(rows))]

            # 在指定的单元格中填入文本
            data[0][0] = "Embodied carbon save ratio(%)"
            data[1][0] = "Overall carbon save ratio(%)"
            data[2][0] = "Choosing metric(years)"
            data[3][0] = "Replacing metric(years)"
            data[4][0]=" Bandwidth requirement"
            for i in range(1,9):
                data[0][i]=int((sum(self.data[0][:-1])-sum(self.data[i][:-1]))/sum(self.data[0][:-1])*10000)/100
                
                data[1][i]=int((sum(self.data[0])-sum(self.data[i]))/sum(self.data[0])*10000)/100
                data[2][i]=int((sum(self.data[0][:-1])-sum(self.data[i][:-1]))/((self.data[i][-1]-self.data[0][-1]))*10)
                if data[2][i]<0:
                    if sum(self.data[0][:-1])<sum(self.data[i][:-1]):
                         data[2][i]='∞'
                    else: data[2][i]=">0"

                elif sum(self.data[0][:-1])>sum(self.data[i][:-1]):
                    data[2][i]="<"+str(data[2][i])
                else: data[2][i]=">"+str(data[2][i])
                data[3][i]=int(sum(self.data[i][:-1])/(self.data[0][-1]-self.data[i][-1])*10)
                if data[3][i]<0:
                    data[3][i]='∞'

                
                else: data[3][i]=">"+str(data[3][i])
                if self.bandwidth[i]>self.baseline:
                    data[4][i]='\u2713'
                else: data[4][i]='\u2717'
            
            
            fig, ax = plt.subplots(figsize=(7, 1.8))  
            ax.axis('off')  
            table = ax.table(cellText=data, colLabels=labels, loc='center', cellLoc='center')
                       
            table.auto_set_font_size(False)
            table.set_fontsize(10)

            # 调整单元格大小
            table.auto_set_column_width(col=list(range(len(labels))))  # 对所有列进行自动列宽设置
            plt.show()
            if self.option=="homo":
                fig.savefig("../result/table5_1.jpg")
            else: fig.savefig("../result/table5_2.jpg")
            

           
            


                
    
                

            
        
def print_design(firedirection):
   
   chip=AV(firedirection)
   #chip.print_name()
   chip.print_result()
   chip=AV(firedirection,option='heter')
   chip.print_result()



def draw_AV(data,bandwidth,design):
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.figure(figsize=(8, 3))
    fig, ax1 = plt.subplots(figsize=(8, 3))
    m=np.arange(36)
    baseline=[0.74*2,0.9*2,1.6*2,3*2]

    wid=0.14
    length=0.16
    width = 1.6 
    # labels=['soc','MCM','InFO-Chipfirst','InFO-Chiplast','Si','Microbump','Hybridbonding','monolithic']
    labels=[ '2D','MCM', 'InFO_1', 'InFO_2', 'EMIB','Si_ini', 'Micro', 'Hybrid', 'M3D']
    llabels=labels+labels+labels+labels
    xlabel=['DRIVE PX','DRIVE XAVIER',"DRIVE ORIN","DRIVE THOR"]

    
    colors = [ 'orange','purple', 'royalblue', 'peru','seagreen']
    #colors = ['yellow','dodgerblue', 'deepskyblue', 'steelblue', 'green',]

    hatchs = [ 'xxxx','|||', 'ooo', '///','---',]
    plt.bar(0, 0, width=wid,color='white',edgecolor=colors[0],hatch=hatchs[0])
    plt.bar(0, 0, width=wid, color='white',edgecolor=colors[1],hatch=hatchs[1])
    plt.bar(0, 0, width=wid, color='white',edgecolor=colors[2],hatch=hatchs[2])
    plt.bar(0, 0, width=wid,color='white',edgecolor=colors[3],hatch=hatchs[3])
    plt.bar(0, 0, width=wid, color='white',edgecolor=colors[4],hatch=hatchs[4])


    for  k in range(4):   
        for l in range(9):
            heights=[t for t in data[k][l] ]
            bar_container = plt.bar(k*width+l*length, [np.sum(heights)/1000, np.sum(heights[:4])/1000, np.sum(heights[:3])/1000, np.sum(heights[:2])/1000, np.sum(heights[:1])/1000], width=wid, color='white',edgecolor=colors,hatch=hatchs, linewidth=1)
    plt.xticks((m-m%9)/9*width+(m%9)*length,llabels,fontsize=8,fontweight=800,rotation=90)      
    #plt.scatter((k)*width+l*length,2500,marker='x',color="white",edgecolors='white',s=40)       
    text_bbox_props = dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='white', alpha=0)
    plt.yscale('log',base=10)
    
    font_props = {'weight': 'bold', 'size': 12}
    font_props = {'weight': 'bold', 'size': 12}
    ax2 = ax1.twinx()

    LengthBlackDashLine = 0.16
    WidthBalckDashLine = 1.5
    biasl = [0, 0.1, 0.19, 0.28]
    biasr = [-0.06, 0., 0.12, 0.22]
    for  k in range(4):   
        ax2.plot([(k-1)*WidthBalckDashLine+9*LengthBlackDashLine + biasl[k], (k)*WidthBalckDashLine+9*LengthBlackDashLine + biasr[k]],[baseline[k]*2, baseline[k]*2],color='black',linestyle='dashed',label='Energy efficiency')
        for l in range(9):
            # ax2.plot((k)*width+1.1*q*length,[baseline[k]]*9,color='black',linestyle='dashed',label='Energy efficiency')
            # ax2.plot((k)*width+1.1*q*length,[baseline[k]]*9,color='black',linestyle='dashed',label='Energy efficiency')
            #ax2.plot((k)*width+1*q*length,bandwidth[k],color='black',linestyle='dashed',label='Energy efficiency')
            ax2.scatter((k)*width+l*length,bandwidth[k][l]*2,marker='x',color="red",edgecolors='black',s=15)
    # ax2.scatter((k)*width+l*length,-80,marker='x',color="white",edgecolors='white',s=60)
    #ax2.legend(' ',bbox_to_anchor=(0.91, 1.09),prop=font_props,handlelength=2, framealpha=0)
    plt.text(6.75,-30,'Bandwidth (TB/s)',fontsize=12,fontweight=800,rotation=90)
    plt.text(-0.85,-30,'Overall Carbon (kg)',fontsize=12,fontweight=800,rotation=90)
    # plt.yticks(yticks_values)
    plt.yticks([0,20], ['0','10'])
    ax2.set_ylim(-40,30)
    plt.tight_layout()
    for tick in ax1.get_xticklabels():
        tick.set_rotation(50)
    if design=="hoto":  
        plt.savefig("../result/fig5a.jpg")
    else:  plt.savefig("../result/fig5b.jpg")
    plt.show()
    




file_route='./'

def print_carbon(firedirection):
    with open("../parameters/carbon_intensity/manufacturing_location.json", 'r') as f:
        carbon_intensity_config= json.load(f)  
    with open("../parameters/Delay/delay_scaling_factors.json", 'r') as f:
        delay_package= json.load(f) 
    with open("../parameters/Delay/delay_node_factors.json", 'r') as f:
        delay_node= json.load(f)  
    with open("../parameters/power_intensity/power_intensity.json", 'r') as f:
        powerintensity= json.load(f)  
    with open("../parameters/power_intensity/power_intensity.json", 'r') as f:
        powerscaling= json.load(f)  
    with open(file_route+firedirection, 'r') as file:
        datas = yaml.safe_load(file)
    for data in datas:
        name=data.get("Product","None")
        
        packagearea=data.get("packagearea(mm2)",0)
        Manufacturing_location=data.get("manufacturing_power_grid","world")
        Using_location=data.get("use_power_grid","world")
        stacking=data.get("stacking","D2W")
        method=data["method"]
        test=data.get("test",0)
        F2F_F2B=data.get("F2F_F2B","F2B")
        application=data.get("application","CPU(desktop)")
        dies={}
        name=data.get("Product","None")
        technode=data["die_list"][0]["technode(nm)"]
        
        area=0
        
        
        for i in data["die_list"]:
            if i["technode(nm)"]<technode:
                technode=i["technode(nm)"]
            

            
            die_key=die(i["technode(nm)"],name=i.get("name","die"),gnumber=i.get("gatenumber",0),area=i.get("area(mm2)",0),feature_size=i.get("feature_size",0),layer=i.get("layer",0),layer_sensitive=i.get("layer_sensitive",1),IO=i.get("IO_number",0))
            die_value=i.get("number",1)
            dies.update({die_key:die_value})
            area+=die_key.area*die_value
       
        power=data.get("power(W)",0)
        energy=data.get("energy(mJ)",0)
        delay=data.get("delay(s)",0)
        T_app=data.get("T_app(s)",delay)
        lifetime=data.get("T_exe(year)",0.25)*365*3600*24
        design_exploration=data.get("design_exploration",0)
        gamma=data.get("gamma",0.98)
        carbon=api(method,dies,Manufacturing_location=Manufacturing_location,packagearea=packagearea,stacking=stacking,name=name,test=test,F2F_F2B=F2F_F2B).carbon

        if not design_exploration:
            return


        if energy and delay:
            CEP=carbon*energy
            CDP=carbon*delay
            tCDP=(gamma*carbon*T_app/lifetime+energy/1000/3600/1000*carbon_intensity_config[Using_location])*delay
            print("Here is the total life cycle carbon footprint:")
            print("Embodied carbon: {:.2e} g,".format(carbon),"Operational carbon: {:.2e} g.".format(power*carbon_intensity_config[Manufacturing_location]*lifetime/10/1000/3600))



        elif energy:
            raise ValueError("the value of delay need!")


        elif power and delay:
            
            CDP=carbon*delay
            CEP=carbon*power*T_app
            tCDP=(gamma*carbon*T_app/lifetime+power*carbon_intensity_config[Manufacturing_location]*T_app/10/1000/3600)*delay
            print("Here is the total life cycle carbon footprint:")
            print("Embodied carbon: {:.2e} g,".format(carbon),"Operational carbon: {:.2e} g.".format(power*carbon_intensity_config[Manufacturing_location]*lifetime/10/1000/3600))
            #print("Design metrics: ")
            #print("CDP: {:.2e} g·s,".format(CDP),"CEP: {:.2e} g·J".format(CEP),"tCDP: {:.2e} g·s,".format(tCDP),"tCDP^-1: {:.2e} (g·s)^-1".format(1/tCDP))

        elif power:
           raise ValueError("the value of delay need!")

        else:
            power=area*powerintensity[application]
            CDP=carbon*delay
            CEP=carbon*power*T_app/1000
            tCDP=(gamma*carbon*T_app/lifetime+power*carbon_intensity_config[Manufacturing_location]*T_app/10/1000/3600)*delay
            print("Here is the total life cycle carbon footprint:")
            print("Embodied carbon: {:.2e} g,".format(carbon),"Operational carbon: {:.2e} g.".format(power*carbon_intensity_config[Manufacturing_location]*lifetime/10/1000/3600))
            #print("Design metrics: ")
            #print("CDP: {:.2e} g·s,".format(CDP),"CEP: {:.2e} g·J".format(CEP),"tCDP: {:.2e} g·s,".format(tCDP),"tCDP^-1: {:.2e} (g·s)^-1".format(1/tCDP))


        



   
        
        
def exploration(firedirection): 
    with open("../parameters/carbon_intensity/manufacturing_location.json", 'r') as f:
        carbon_intensity_config= json.load(f)  
    with open("../parameters/Delay/delay_scaling_factors.json", 'r') as f:
        delay_package= json.load(f) 
    with open("../parameters/Delay/delay_node_factors.json", 'r') as f:
        delay_node= json.load(f)  
    with open("../parameters/power_intensity/power_intensity.json", 'r') as f:
        powerintensity= json.load(f)  
    with open("../parameters/power_intensity/power_intensity.json", 'r') as f:
        powerscaling= json.load(f)  
    with open(file_route+firedirection, 'r') as file:
        datas = yaml.safe_load(file)
    with open(file_route+firedirection, 'r') as file:
        
        datass = yaml.safe_load(file)
        for datas in datass:
                Manufacturing_location=datas.get("manufacturing_power_grid","world")
                Using_location=datas.get("use_power_grid","world")
                stacking=datas.get("stacking","D2W")
                test=datas.get("test",0)
                F2F_F2B=datas.get("F2F_F2B","F2B")
                application=datas.get("application","CPU(desktop)")
                areaset=[100]
                technode=datas["technode"]
                dienumber=datas["die_number"]
                method=datas.get("method",['MCM', 'InFO_chip_first', 'InFO_chip_last', 'Si_int', 'Micro_bumping', 'Hybrid_bonding', 'Monolithic_3D'])
                gammaset=[1]
                power=datas.get("power(W)",0)
                energy=datas.get("energy(mJ)",0)
                delay=datas.get("delay(s)",0)
                T_app=datas.get("T_app(s)",delay)
                l=datas.get("T_exe(year)",0.25)*365*3600*24
                for data in datas["Variables"]:
                    variable=data["Variable"]
                    if variable not in ["area","gamma"]:
                        raise ValueError("The exploration variable must be area, die_number or gamma!")
                    
                    if variable=="area":
                        if data["Model"]=="set":   
                            areaset=data["Variable_set"]
                        if data["Model"]=="range":   
                            areaset=list(range(data['begin'],data['end']+data['linspace'],data['linspace']))
                    if variable=="gamma":
                        if data["Model"]=="set":   
                            gammaset=data["Variable_set"]
                        if data["Model"]=="range":   
                            gammaset=list(range(data['begin'],data['end']+data['linspace'],data['linspace']))
                if(len(datas["Variables"])==1):
                    die_array2d=[]
                    die_array=[]
                    die_array_mono=[]
                    die_array_hy=[]
                    
                    
                    for i in areaset:
                        die_list_2d={}
                        die_list_3d={}
                        die_list_hy={}
                        die_list_mono={}
                        for t in range(dienumber):
                            diet=die(technode,area=i*1.1/dienumber)
                            die_list_2d[diet]=1
                        die_array2d.append(die_list_2d)
                        
                        for t in range(dienumber):
                            diet=die(technode,area=i/dienumber)
                            die_list_3d[diet]=1
                        die_array.append(die_list_3d)

                        for t in range(dienumber):
                            diet=die(technode,area=i/dienumber)
                            diet.layer-=3
                            die_list_hy[diet]=1
                        die_array_hy.append(die_list_hy)

                        for t in range(dienumber):
                            diet=die(technode,area=i*0.9/dienumber,layer=5)
                            die_list_mono[diet]=1
                        die_array_mono.append(die_list_mono)

                
                    data = np.zeros((len(areaset),7,4),dtype=float)
                    for d in range(len(areaset)):
                            t1=die_array2d[d]
                            t=die_array[d]

                            mcm=MCM(t1)
                            si=Si_int(t1)
                            info_first=InFO_chipfirst(t1)
                            info_last=InFO_chiplast(t1)
                            microbump=Micro_bumping(t,method=stacking,F2F_F2B=F2F_F2B)
                            hybrid=Hybrid_bonding(die_array_hy[d],method=stacking,F2F_F2B=F2F_F2B)
                            if dienumber==2:
                                monolithic=Monolithic3D(die_array_mono[d])
                            
                            data[d][0]=mcm.carbonbreak
                            data[d][1]=info_first.carbonbreak
                            data[d][2]=info_last.carbonbreak
                            data[d][3]=si.carbonbreak
                            data[d][4]=microbump.carbonbreak
                            data[d][5]=hybrid.carbonbreak
                            data[d][6]=monolithic.carbonbreak
                    
                        
                        
                    x = np.arange(4)
                    wid=0.096
                    length=0.114
                    width = 1.0  # 柱子宽度

                    # 创建数据
                    # labels=['soc','MCM','InFO-Chipfirst','InFO-Chiplast','Si','Microbump','Hybridbonding','monolithic']
                    labels=[ 'MCM', 'InFO_1', 'InFO_2', 'Si_ini', 'Micro', 'Hybrid', 'M3D']

                
                    # 设置子图布局
                    
                    colors = ['peru', 'mediumorchid', 'royalblue', 'seagreen']
                    
                    plt.bar(0, 0, width=wid,color=colors[0], edgecolor='black')
                    plt.bar(0, 0, width=wid,color=colors[1], edgecolor='black')
                    plt.bar(0, 0, width=wid,color=colors[2], edgecolor='black')
                    plt.bar(0, 0, width=wid,color=colors[3], edgecolor='black')
                    plt.legend(['Die', 'Bonding', '2.5D substrate', 'Packaging'])
                    
                    for  k in range(len(areaset)):   
                                for l in range(7):
                                    heights=[t/areaset[k]/np.sum(data[-1][1])*(800) for t in data[k][l] ]
                                    bar_container = plt.bar(k*width+l*length, [np.sum(heights), np.sum(heights[:3]), np.sum(heights[:2]), np.sum(heights[:1])], width=wid, color=colors[::-1], linewidth=1, edgecolor='black')
                                    plt.bar_label(bar_container, labels=[labels[l], '', '', ''], rotation=90, padding=2, fontsize=10)
                
                    plt.xticks(x*width + wid * 4,areaset)  # 设置横坐标刻度位置
                
                    plt.title(f'chiplet{dienumber}-{technode}nm')
                    plt.savefig("bar.jpg")

                        # 显示图形
                    plt.tight_layout()
                    plt.show()
                
                elif (len(datas["Variables"])==2):
                    if(method==["Micro_bumping", "Hybrid_bonding", "Monolithic_3D"]):
                        
                        power=[196.62,199.8,212.58]
                        tech=[14,7,3]
                        
                        
                        integ=['Micro_bump','Hybridbonding','Monolithic3D']
                        delay=[80,150,290]
                        
                        carbon=np.zeros((len(areaset),len(gammaset)),dtype=float)
                        carbon1=np.zeros((len(areaset),len(gammaset)),dtype=float)
                        carbon2=np.zeros((len(areaset),len(gammaset)),dtype=float)
                        
                       
                        
                        

                        import matplotlib

                        cmap=matplotlib.cm.get_cmap('jet', 11)

                        '''
                        cmap = plt.cm.jet  # define the colormap
                        # extract all colors from the .jet map
                        cmaplist = [cmap(i) for i in range(cmap.N)]
                        # force the first color entry to be grey
                        cmaplist[0] = (.5, .5, .5, 1.0)

                        # create the new map
                        cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
                            'Custom cmap', cmaplist, cmap.N)
                        '''

                        fig, axes = plt.subplots(3, 3, figsize=(12, 12))
                        for index in range(3):
                            
                            for j in range(len(areaset)):
                                for i in range(len(gammaset)):
                                    
                                    t={}
                                    t1={}
                                    for x in range(dienumber):
                                        d=die(tech[index],area=areaset[len(areaset)-1-j]/dienumber)
                                        d1=die(tech[index],area=areaset[len(areaset)-1-j]/dienumber)
                                        d.layer=10
                                        d1.layer=6
                                        t[d]=1
                                        t1[d1]=1

                                    carbon[j][i]=(gammaset[i]*Micro_bumping(t).carbon/carbon_intensity_config[Manufacturing_location]*3600*1000*1000+power[0]*areaset[len(areaset)-1-j]/0.7*l)/(1/301*3600*1000*1000)/1000*areaset[len(areaset)-1-j]/delay[index]*1e-3
                                    carbon1[j][i]=(gammaset[i]*Hybrid_bonding(t).carbon/carbon_intensity_config[Manufacturing_location]*3600*1000*1000+power[1]*areaset[len(areaset)-1-j]/0.7*l)/(1/carbon_intensity_config[Using_location]*3600*1000*1000)/1000*areaset[len(areaset)-1-j]/delay[index]*1e-3/1.215
                                    carbon2[j][i]=(gammaset[i]*Monolithic3D(t1).carbon/carbon_intensity_config[Manufacturing_location]*3600*1000*1000+power[2]*areaset[len(areaset)-1-j]/0.7*l)/(1/301*3600*1000*1000)/1000*areaset[len(areaset)-1-j]/delay[index]*1e-3/1.7
                            x=np.array(areaset)
                            y=np.array(gammaset)
                            dx = x[1] - x[0]
                            dy = y[1] - y[0]
                            ax=axes[0,index]
                            if index==0:
                                norm=carbon[int((len(areaset))*3/8)][1]
                            # 设置坐标轴范围和纵横比
                            extent = [x.min() - dx/2, x.max() + dx/2, y.min() - dy/2, y.max() + dy/2]
                            ax.set_title(str(tech[index])+'nm'+'for micro bump')
                            aspect_ratio = abs((extent[1] - extent[0]) / (extent[3] - extent[2]))
                            heat=ax.imshow(carbon/norm, cmap=cmap,extent=extent, aspect=aspect_ratio,vmin=0,vmax=20, interpolation='bilinear')
                            ax.set_xticks(np.linspace(x.min(), x.max(), 5))
                            ax.set_yticks(np.linspace(y.min(), y.max(), 5))
                            ax.set_xlabel('area')
                            ax.set_ylabel('gamma')
                            if index==2: fig.colorbar(heat, ax=ax, location='right')
                            

                            ax=axes[1,index]
                            ax.set_title(str(tech[index])+'nm for hybridbonding')
                            aspect_ratio = abs((extent[1] - extent[0]) / (extent[3] - extent[2]))
                            ax.imshow(carbon1/norm, cmap=cmap,extent=extent, aspect=aspect_ratio,vmin=0,vmax=20, interpolation='bilinear')
                            ax.set_xticks(np.linspace(x.min(), x.max(), 5))
                            ax.set_yticks(np.linspace(y.min(), y.max(), 5))
                            ax.set_xlabel('area')
                            ax.set_ylabel('gamma')
                            
                            
                            ax=axes[2,index]
                            ax.set_title(str(tech[index])+'nm for monolithic')
                            aspect_ratio = abs((extent[1] - extent[0]) / (extent[3] - extent[2]))
                            ax.imshow(carbon2/norm, cmap=cmap,extent=extent, aspect=aspect_ratio,vmin=0,vmax=20, interpolation='bilinear')
                            ax.set_xticks(np.linspace(x.min(), x.max(), 5))
                            ax.set_yticks(np.linspace(y.min(), y.max(), 5))
                            ax.set_xlabel('area')
                            ax.set_ylabel('gamma')
                           
                            

                            # 显示图像
                        fig.tight_layout()
                        plt.savefig("cmap.jpg")

                        # fig.colorbar(heat, ax=axes, location='right')
                        plt.show()
                        

                    

                else: raise ValueError("The number of variables must be 1 or 2")
                    






            # %%
