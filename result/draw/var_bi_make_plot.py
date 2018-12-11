# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 20:53:57 2018

@author: allen
"""

import matplotlib.pyplot as plt
import numpy as np 

LFLS_x = [17]
LFLS_y = [13]
NFNS_x = [17]
NFNS_y = [15]
NFLS_x = [17]
NFLS_y = [15]
Ours_x= [17]
Ours_y= [15]

params = {'figure.figsize': '12, 8','font.size':'28', 'axes.titlesize':'40',  'lines.markersize': '32','axes.labelsize': '36','xtick.labelsize': '32','ytick.labelsize': '32', 'lines.linewidth': '4',
'legend.fontsize': '28'}  # set figure size }
plt.rcParams.update(params)
plt.plot(Ours_x,Ours_y,linestyle='--', marker='x', color='r')
plt.scatter(LFLS_x,LFLS_y, marker='s', color='orange')
plt.scatter(NFNS_x,NFNS_y, marker='^', color='g')
plt.scatter(NFLS_x,NFLS_y, marker='.', color='b')

for a,b in zip(Ours_x, Ours_y): 
    plt.annotate('('+str(a)+','+str(b)+')',xy=(a,b))
for a,b in zip(LFLS_x, LFLS_y): 
    plt.annotate('('+str(a)+','+str(b)+')',xy=(a,b))
plt.legend(['Ours','LF_LS','NF_NS', 'NF_LS'], loc='lower right')
plt.title("Pareto front of Make")
plt.xlabel("#Test")
plt.ylabel("#Fault")
my_x_ticks = np.arange(16, 19, 1) #显示范围为-5至5，每0.5显示一刻度
my_y_ticks = np.arange(10, 18, 2) #显示范围为-2至2，每0.2显示一刻度
plt.xticks(my_x_ticks)
plt.yticks(my_y_ticks)
           
fig = plt.gcf()
plt.show()
fig.set_size_inches(7,5)
fig.savefig('var_bi_make_plot.png')
