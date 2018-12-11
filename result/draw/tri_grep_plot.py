# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 20:53:57 2018

@author: allen
"""

import matplotlib.pyplot as plt
import numpy as np 

#LFLS_x = [44]
#LFLS_y = [28]
#NFNS_x = [44]
#NFNS_y = [32]
NFLS_x = [1635]
NFLS_y = [54]
Ours_x= [1635,1639,1643,1646,1649,1652,1654,1656,1658,1659,1660,1662,1663,1664,1666,1667,1668,1669,1670]
Ours_y= [54,53,52,51,50,49,48,47,46,45,44,43,42,41,39,37,36,34,32]

my_x_ticks = np.arange (1635,1671,7)#显示范围为-5至5，每0.5显示一刻度
my_y_ticks = np.arange(32,56,5) #显示范围为-2至2，每0.2显示一刻度
plt.xticks(my_x_ticks)
plt.yticks(my_y_ticks)
  
params = {'figure.figsize': '12, 8','font.size':'24', 'axes.titlesize':'40',  'lines.markersize': '32','axes.labelsize': '36','xtick.labelsize': '32','ytick.labelsize': '32', 'lines.linewidth': '4',
'legend.fontsize': '28'}  # set figure size }
plt.rcParams.update(params)
plt.plot(Ours_x,Ours_y,linestyle='--', marker='x', color='r')
#plt.scatter(LFLS_x,LFLS_y, marker='s', color='orange')
#plt.scatter(NFNS_x,NFNS_y, marker='^', color='g')
plt.scatter(NFLS_x,NFLS_y, marker='.', color='b')

for a,b in zip(Ours_x, Ours_y): 
    plt.annotate('('+str(a)+','+str(b)+')',xy=(a,b))
#for a,b in zip(LFLS_x, LFLS_y): 
#    plt.annotate('('+str(a)+','+str(b)+')',xy=(a,b))
plt.legend(['Ours', 'NF_LS'], loc='upper right')
plt.title("Pareto front of Grep")
plt.xlabel("#Statement")
plt.ylabel("#Fault")
           
fig = plt.gcf()
plt.show()
fig.set_size_inches(7,5)
fig.savefig('tri_grep_plot.png')
