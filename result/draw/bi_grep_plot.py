# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 20:53:57 2018

@author: allen
"""

import matplotlib.pyplot as plt
import numpy as np 

LFLS_x = [59]
LFLS_y = [29]
NFLS_x = [59]
NFLS_y = [36]
Ours_x= [59,60,61,62,63,64,65,66,67,68,69,70,71,72]
Ours_y= [36,39,41,43,44,46,47,48,49,50,51,52,53,54]

my_x_ticks = np.arange(59, 73, 2) #显示范围为-5至5，每0.5显示一刻度
#my_y_ticks = np.arange(-2, 2, 0.2)      #显示范围为-2至2，每0.2显示一刻度
plt.xticks(my_x_ticks)
#plt.yticks(my_y_ticks)
  
params = {'font.size':'25', 'axes.titlesize':'40',  'lines.markersize': '32','axes.labelsize': '36','xtick.labelsize': '32','ytick.labelsize': '32', 'lines.linewidth': '4',
'legend.fontsize': '28', 'figure.figsize': '12, 8'}  # set figure size }
plt.rcParams.update(params)
plt.plot(Ours_x,Ours_y,linestyle='--', marker='x', color='r')
plt.scatter(LFLS_x,LFLS_y, marker='s', color='orange')
plt.scatter(NFLS_x,NFLS_y, marker='.', color='b')

for a,b in zip(Ours_x, Ours_y): 
    plt.annotate('('+str(a)+','+str(b)+')',xy=(a-0.1,b-0.3))
for a,b in zip(LFLS_x, LFLS_y): 
    plt.annotate('('+str(a)+','+str(b)+')',xy=(a,b))
plt.legend(['Ours','LF_LS', 'NF_LS'], loc='lower right')
plt.title("Pareto front of Grep")
plt.xlabel("#Test")
plt.ylabel("#Fault")
           
fig = plt.gcf()
plt.show()
fig.set_size_inches(7,5)
fig.savefig('bi_grep_plot.png')
