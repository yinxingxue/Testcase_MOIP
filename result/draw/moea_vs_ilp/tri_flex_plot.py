# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 20:53:57 2018

@author: allen
"""

import matplotlib.pyplot as plt
import numpy as np 

def NSGA2_Label(a,b):
    if	a == 3099 and b == 36:  
        return r'$h=7$'
    if	a == 3109 and b == 34:  
        return r'$h=3$'
    if	a == 3104 and b == 35:  
        return r'$h=5$'
    if	a == 3094 and b == 37:  
        return r'$h=3$'
    if	a == 3110 and b == 33:  
        return r'$h=2$'
    
def MOEAD_Label(a,b):
    return ''
    

NSGA2_x = [3099,3109,3104,3094,3110]
NSGA2_y = [36,34,35,37,33]
MOEAD_x = []
MOEAD_y = []
Ours_x= [3094,3099,3104, 3109,3110,3113,3114,3116,3118]
Ours_y= [37,36,35,34,33,32,31,30,26]

my_x_ticks = np.arange(3094,3119,6) #显示范围为-5至5，每0.5显示一刻度
my_y_ticks = np.arange(26,40,3) #显示范围为-2至2，每0.2显示一刻度
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

for a,b in zip(NSGA2_x,NSGA2_y): 
    plt.annotate(NSGA2_Label(a,b),xy=(a-0.45,b+0.5),color='b')
for a,b in zip(MOEAD_x,MOEAD_y): 
    plt.annotate(MOEAD_Label(a,b),xy=(a-0.45,b-0.2),color='g')
    
plt.legend(['Ours', 'NSGA2','MOEA/D'], loc='lower left')
plt.title("Pareto front of Flex")
plt.xlabel("#Statement")
plt.ylabel("#Fault")
           
fig = plt.gcf()
plt.show()
fig.set_size_inches(7,5)
fig.savefig('tri_flex_plot.png')
