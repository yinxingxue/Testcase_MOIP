# -*- coding: utf-8 -*-
"""
Created on Sat Jan  5 09:38:24 2019

@author: allen
"""
import numpy as np
import shutil,os
import sys
import math
from probReader import ProbReader
import pygmo as pg

def calculateHV(rstRaw, allowPerc):
    points=[]
    
    f = open(rstRaw,'r')
    for line in open(rstRaw):
        point=[]
        line = f.readline()
        values = line.split()
        point.append(int(values[0]))
        point.append(int(values[1]))
        point.append(int(values[2]))
        points.append(point)
    dimension1=  ProbReader.stmtSetSize
    dimension2=  ProbReader.fauktSetSize
    allowNum = int(math.floor(allowPerc* ProbReader.testSuiteSize+0.5))
    dimension3=  ProbReader.testSuiteSize - allowNum  
    referencePoint = []
    referencePoint.append(dimension1)
    referencePoint.append(dimension2)
    referencePoint.append(dimension3)
    hv = pg.hypervolume(points = points)
    
    result = hv.compute(referencePoint, hv_algo= pg.hv3d())
    return result
        
        
if __name__ == "__main__":
   
    if len(sys.argv)!=3: 
        os._exit(0) 
    para = sys.argv[1]
    allowPerc=float(sys.argv[2])

    projectName = para
    projectPath = '../../../Nemo/subject_programs/{name}_v5'.format(name=projectName)
    reader = ProbReader(projectPath)
    
    rst1Path = '../../result/moea/nsga2/'+ str(allowPerc)+'/'+projectName+'/'
    rst2Path = '../../result/moea/moeaD/'+ str(allowPerc)+'/'+projectName+'/'
    
    outputPath = '../../result/moea/comp/'+ str(allowPerc)+'/'+projectName+'/'
    if not os.path.isdir(outputPath):
        os.makedirs(outputPath)
    for i in range(0,30):
        rst1_raw= rst1Path+'FUN_'+str(i)+'.tsv'
        rst2_raw= rst2Path+'FUN_'+str(i)+'.tsv'
        hv1 = calculateHV(rst1_raw,allowPerc)
        hv2 = calculateHV(rst2_raw,allowPerc)
        print (str(hv1),str(hv2))
else:
    print("RQ3_RstComparator.py is being imported into another module")
    