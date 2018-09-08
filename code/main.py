# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 10:03:21 2018

@author: Yinxing Xue
"""
from moipProb import MOIPProblem
from naiveSol import NaiveSol

if __name__ == "__main__":
    prob = MOIPProblem(2,7,1)  
    prob.displayObjectiveCount()
    prob.displayFeatureCount()
    prob.exetractFromFile("../test/test_case/parameter_example.txt")
    prob.displayObjectives()
    prob.displayVariableNames()
    prob.displayObjectiveSparseMapList()
    prob.displaySparseInequationsMapList()
    prob.displaySparseEquationsMapList()
    prob.displayAttributeMatrix()
    
    sol= NaiveSol(prob)
    sol.prepare()
    sol.execute()
    sol.outputCplexParetoMap("../result/test_case/parameter_example.txt")
    sol.displaySolvingAttempts()
    sol.displayObjsBoundsDictionary()
    sol.displayCplexSolutionSetSize()
    sol.displayCplexResultMap()
    sol.displayFullCplexResultMap()
    sol.displayCplexParetoSet()
    sol.displayVariableLowerBound()
    sol.displayVariableUpperBound()
    sol.displayVariableTypes()
    sol.displayVariableNames()
else:
    print("main.py is being imported into another module")