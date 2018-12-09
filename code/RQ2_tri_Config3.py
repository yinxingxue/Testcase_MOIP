# -*- coding: utf-8 -*-
"""
Created on Oct 13 12:33:53 2018

@author: Yinxing Xue
"""

import os
import sys
import time
from moipProb import MOIPProblem 
from triCriteriaProbReaderOR import TriCriteriaProbReaderOR
from naiveSol import NaiveSol

if __name__ == "__main__":
    if len(sys.argv)!=3: 
        os._exit(0) 
    para = sys.argv[1]
    TriCriteriaProbReaderOR.AllowPerc=float(sys.argv[2])
    problemGoalNum ='tri'
    projectName = para
    modelingMode = 'OR'
    inputPath = '../../Nemo/subject_programs/{name}_v5'.format(name=projectName)
    moipInputFile = '../test/{goalNum}_input_{name}_{mode}.txt'.format(goalNum=problemGoalNum, name=projectName,mode=modelingMode)
    paretoOutputFile = '../result/{goalNum}-obj/Pareto_{goalNum}_{name}_{mode}.txt'.format(goalNum=problemGoalNum, name=projectName,mode=modelingMode)
    fullResultOutputFile = '../result/{goalNum}-obj/FullResult_{goalNum}_{name}_{mode}.txt'.format(goalNum=problemGoalNum, name=projectName,mode=modelingMode)
    
    reader = TriCriteriaProbReaderOR(inputPath)
    reader.load()
    reader.save(moipInputFile)
    reader.displayFeatureNum()
    reader.displayTestCaseNum()
    reader.displayStmtNum()
    reader.displayFaultNum()
    reader.displayConstraintInequationNum()
    reader.displayConstraintEquationNum()
    
    prob = MOIPProblem(len(reader.objectNames),len(reader.featureNames),len(reader.objectNames)-1)  
    prob.displayObjectiveCount()
    prob.displayFeatureCount()
    prob.exetractFromFile(moipInputFile)
    prob.displayObjectives()
    #prob.displayVariableNames()
    #prob.displayObjectiveSparseMapList()
    prob.displaySparseInequationsMapListCount()
    prob.displaySparseEquationsMapListCount()
    #prob.displayAttributeMatrix()
    
    time_start=time.time()
    sol= NaiveSol(prob)
    sol.prepare()
    sol.execute()
    time_end=time.time()
    exec_time = time_end-time_start
    sol.outputCplexParetoMap(paretoOutputFile)
    sol.outputFullCplexResultMap(fullResultOutputFile)
    sol.displaySolvingAttempts()
    sol.displayObjsBoundsDictionary()
    sol.displayCplexSolutionSetSize()
    sol.displayCplexResultMap()
    sol.displayFullCplexResultMap()
    sol.displayCplexParetoSet()
    print ("Solving time", exec_time)
    #sol.displayVariableLowerBound()
    #sol.displayVariableUpperBound()
    #sol.displayVariableTypes()
    #sol.displayVariableNames()
else:
    print("triCriteriaProbReaderOR.py is being imported into another module")
