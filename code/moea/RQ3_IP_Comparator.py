# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 00:08:20 2019

@author: allen
"""
import sys
import os
from probReader import ProbReader


def readTrueFront(rstRaw):
    'filter the points with the third objective != 0'
    points=[]
    trueDistrMap = {}
    dimension1=  ProbReader.stmtSetSize
    dimension2=  ProbReader.fauktSetSize
    
    f = open(rstRaw,'r')
    for line in open(rstRaw):
        point=[]
        line = f.readline()
        values = line.split()
        point.append(int(values[0]))
        point.append(int(values[1]))
        point.append(int(values[2]))
        if (int(values[2]))==0:
            points.append(point)
            stmtSize = dimension1 - point[0]
            faultSize = dimension2 - point[1]
            key= str(stmtSize)+'_'+str(faultSize) 
            trueDistrMap[key]=1
    return points,trueDistrMap

def readCorrectFront(rstRaw):
    'filter the points with the third objective != 0'
    points=[]
    
    f = open(rstRaw,'r')
    for line in open(rstRaw):
        point=[]
        line = f.readline()
        values = line.split()
        point.append(int(values[0]))
        point.append(int(values[1]))
        point.append(int(values[2]))
        if (int(values[2]))==0:
            points.append(point)
    return points

def filterByTrueFront(trueDistrMap,distrMap):
    trueInDistrMap = {}    
    for key in distrMap:
        if key in trueDistrMap:
            trueInDistrMap[key] = distrMap[key]
    return trueInDistrMap

    
def getTestsizeAndFaults(frontList1,frontList2):
    
    'get the base point'
    dimension1=  ProbReader.stmtSetSize
    dimension2=  ProbReader.fauktSetSize
   
    distrMap1 = {}
    distrMap2 = {}
    
    for front in frontList1:
        countedMap={}
        for point in front: 
            stmtSize = dimension1 - point[0]
            faultSize = dimension2 - point[1]
            key= str(stmtSize)+'_'+str(faultSize) 
            
            if key in distrMap1 and key not in countedMap: 
                countedMap[key] = True
                distrMap1[key]= distrMap1[key]+1
                continue
            elif key in distrMap1 and key in countedMap: 
                continue
            elif key not in distrMap1 and key not in countedMap: 
                countedMap[key] = True
                distrMap1[key]= 1
                continue
            elif key not in distrMap1 and key in countedMap:
                print('error')
                os._exit(0) 
        countedMap.clear()
            
    for front in frontList2:
        countedMap={}
        for point in front: 
            stmtSize = dimension1 - point[0]
            faultSize = dimension2 - point[1]
            key= str(stmtSize)+'_'+str(faultSize) 
            
            if key in distrMap2 and key not in countedMap: 
                countedMap[key] = True
                distrMap2[key]= distrMap2[key]+1
                continue
            elif key in distrMap2 and key in countedMap: 
                continue
            elif key not in distrMap2 and key not in countedMap: 
                countedMap[key] = True
                distrMap2[key]= 1
                continue
            elif key not in distrMap2 and key in countedMap:
                print('error')
                os._exit(0) 
        countedMap.clear()
   
    return distrMap1, distrMap2

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
    refPath =  '../../result/moea/refPnts/'+ str(allowPerc)+'/'+projectName+'/'
    refFilePath = refPath+'ref.pf'     
    
    outputPath = '../../result/moea/comp/'+ str(allowPerc)+'/'+projectName+'/'
    if not os.path.isdir(outputPath):
        os.makedirs(outputPath)
    
    'get the true Pareto Front'
    trueFront,trueDistrMap = readTrueFront(refFilePath)
    
    frontList1 = []
    frontList2 = []
    for i in range(0,30):
        rst1_raw= rst1Path+'FUN_'+str(i)+'.tsv'
        rst2_raw= rst2Path+'FUN_'+str(i)+'.tsv'
        front1 = readCorrectFront(rst1_raw)
        front2 = readCorrectFront(rst2_raw)
        #print (front1)
        #print (front2)
        frontList1.append(front1)
        frontList2.append(front2)
    distrMap1, distrMap2 = getTestsizeAndFaults(frontList1,frontList2)  
    
    trueInDistrMap1 = filterByTrueFront(trueDistrMap,distrMap1)
    trueInDistrMap2 = filterByTrueFront(trueDistrMap,distrMap2)
    
    with open(outputPath+'compIP_'+str(allowPerc)+'_'+projectName+'.txt','w') as f:
        f.write('True Pareto in Front 1:\n')
        f.write(str(trueInDistrMap1)+'\n')
        f.write('True Pareto in Front 2:\n')
        f.write(str(trueInDistrMap2)+'\n')
        f.write('Correct Solution in Front 1:\n')
        f.write(str(distrMap1)+'\n')
        f.write('Correct Solution in Front 2:\n')
        f.write(str(distrMap2)+'\n')
        f.close( )
else:
    print("RQ3_IP_Comparator.py is being imported into another module")
    