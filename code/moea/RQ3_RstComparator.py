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

def readFront(rstRaw):
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
    return points
 
def getDistribution(frontList1,frontList2):
    
    'get the base point'
    dimension1=  ProbReader.stmtSetSize
    dimension2=  ProbReader.fauktSetSize
    allowNum = int(math.floor(allowPerc* ProbReader.testSuiteSize+0.5))
    dimension3=  ProbReader.testSuiteSize - allowNum  
    basePoint = []
    basePoint.append(dimension1)
    basePoint.append(dimension2)
    basePoint.append(dimension3)
    
    distrMap = {}
    distanceMap = {} 
    for front in frontList1:
        for point in front: 
            key= str(point[0])+'_'+str(point[1])+'_'+str(point[2])
            
            if key in distrMap: 
                distrMap[key]= distrMap[key]+1
                continue
            distrMap[key]=1
            distance = calculateDistance(basePoint,point)
            distanceMap[key] = distance
            
    return distrMap, distanceMap

def findWorstPoint(distanceMap):
    worstKey = '' 
    worstValue = float('inf')
    for key in distanceMap:
        distance = distanceMap[key]
        if distance < worstValue:
            worstKey = key
            worstValue = distance
    dimensions = worstKey.split('_')
    worstPoint = [] 
    worstPoint.append(int(dimensions[0]))
    worstPoint.append(int(dimensions[1]))
    worstPoint.append(int(dimensions[2]))
    return worstPoint

def calculateDistance(referencePoint,point):
    distance  = 0.0
    for i in range(0,len(referencePoint)):
        distance+= math.pow(referencePoint[i]-point[i],2)
    distance =    math.sqrt(distance)
    return distance

def normalizedHV(hvList1,hvList2):
    normalizedHVList1 = []
    normalizedHVList2 = []
    bestHV = -1 
    for hv in hvList1:
        if hv > bestHV:
            bestHV= hv
    for hv in hvList2:
        if hv > bestHV:
            bestHV= hv
    
    normalizedHVList1 = list(map(lambda x:x*1.0/bestHV,hvList1))
    normalizedHVList2 = list(map(lambda x:x*1.0/bestHV,hvList2))
    return normalizedHVList1,normalizedHVList2

def readMetric(rstRaw):
    spread = 0
    execTime = -1
    try:
        pro_file = open(rstRaw, 'Ur')
        for line in pro_file.readlines():
            line = line.strip().replace('\n', '')
            if line.find("#")!=-1:
                line=line[0:line.find('#')]
            if line.find('=') > 0:
                strs = line.split('=')
                strs[1]= line[len(strs[0])+1:]
                if strs[0]== 'GSPREAD':
                    spread= float(strs[1])
                if strs[0]== 'TIME':
                    execTime= float(strs[1])
    except IOError:
        print ("error in read the metric file")
    else:
        pro_file.close()
    return  spread, execTime  

if __name__ == "__main__":
   
    if len(sys.argv)!=3: 
        os._exit(0) 
    para = sys.argv[1]
    allowPerc=float(sys.argv[2])

    projectName = para
    projectPath = '../../../Nemo/subject_programs/{name}_v5'.format(name=projectName)
    reader = ProbReader(projectPath)
    reader.load()
    
    rst1Path = '../../result/moea/nsga2/'+ str(allowPerc)+'/'+projectName+'/'
    rst2Path = '../../result/moea/moeaD/'+ str(allowPerc)+'/'+projectName+'/'
    
    outputPath = '../../result/moea/comp/'+ str(allowPerc)+'/'+projectName+'/'
    if not os.path.isdir(outputPath):
        os.makedirs(outputPath)
    
    frontList1 = []
    frontList2 = []
    for i in range(0,30):
        rst1_raw= rst1Path+'FUN_'+str(i)+'.tsv'
        rst2_raw= rst2Path+'FUN_'+str(i)+'.tsv'
        front1 = readFront(rst1_raw)
        front2 = readFront(rst2_raw)
        print (front1)
        print (front2)
        frontList1.append(front1)
        frontList2.append(front2)
    distrMap, distanceMap = getDistribution(frontList1,frontList2)
    worstPoint = findWorstPoint(distanceMap)
    
    hvList1=[]
    hvList2=[]
    for i in range(0,30):
        hv1 = pg.hypervolume(points = frontList1[i])
        result1 = hv1.compute(worstPoint, hv_algo= pg.hv3d())
        hvList1.append(result1)
        hv2 = pg.hypervolume(points = frontList2[i])
        result2 = hv2.compute(worstPoint, hv_algo= pg.hv3d())
        hvList2.append(result2)
    
    normalizedHVList1,normalizedHVList2 = normalizedHV(hvList1,hvList2)
    
    spreadList1 = []
    spreadList2 = []
    execTimeList1 = [] 
    execTimeList2 = [] 
    for i in range(0,30):
        rst1_metric = rst1Path+'FUN_'+str(i)+'_metric.txt'
        rst2_metric = rst2Path+'FUN_'+str(i)+'_metric.txt'
        spread1, execTime1 = readMetric(rst1_metric)
        spread2, execTime2 = readMetric(rst2_metric)
        spreadList1.append(spread1)
        spreadList2.append(spread2)
        execTimeList1.append(execTime1)
        execTimeList2.append(execTime2)
else:
    print("RQ3_RstComparator.py is being imported into another module")
    