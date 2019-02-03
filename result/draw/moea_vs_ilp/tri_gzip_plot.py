# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 20:53:57 2018

@author: allen
"""

import matplotlib.pyplot as plt
import numpy as np 

def NSGA2_Label(a,b):
    if	a == 1352 and b == 54:  
        return r'$h=1$'
    
def MOEAD_Label(a,b):
    return ''
    

NSGA2_x = [1352]
NSGA2_y = [54]
MOEAD_x = []
MOEAD_y = []
Ours_x= [1343,1348,1352, 1354,1355,1356,1357,1358]
Ours_y= [56,55,54,53,52,51,49,48]

my_x_ticks = np.arange(1342,1359,4) #显示范围为-5至5，每0.5显示一刻度
my_y_ticks = np.arange(48,58,2) #显示范围为-2至2，每0.2显示一刻度
plt.xticks(my_x_ticks)
plt.yticks(my_y_ticks)
  
params = {'figure.figsize': '12, 8','font.size':'30', 'axes.titlesize':'40',  'lines.markersize': '32','axes.labelsize': '36','xtick.labelsize': '32','ytick.labelsize': '32', 'lines.linewidth': '4',
'legend.fontsize': '28'}  # set figure size }
plt.rcParams.update(params)
plt.plot(Ours_x,Ours_y,linestyle='--', marker='x', color='r')
#plt.scatter(LFLS_x,LFLS_y, marker='s', color='orange')
#plt.scatter(NFNS_x,NFNS_y, marker='^', color='g')
plt.scatter(NSGA2_x,NSGA2_y, marker='^', color='b')
plt.scatter(MOEAD_x,MOEAD_y, marker='v', color='g')
#for a,b in zip(Ours_x, Ours_y): 
#    plt.annotate('('+str(a)+','+str(b)+')',xy=(a,b))
for a,b in zip(NSGA2_x,NSGA2_y): 
    plt.annotate(NSGA2_Label(a,b),xy=(a-0.45,b+0.5),color='b')
for a,b in zip(MOEAD_x,MOEAD_y): 
    plt.annotate(MOEAD_Label(a,b),xy=(a-0.45,b-0.2),color='g')
    
plt.legend(['Ours', 'NSGA2','MOEA/D'], loc='lower left')
plt.title("Pareto front of Gzip")
plt.xlabel("#Statement")
plt.ylabel("#Fault")
           
fig = plt.gcf()
plt.show()
fig.set_size_inches(7,5)
fig.savefig('tri_gzip_plot.png')
