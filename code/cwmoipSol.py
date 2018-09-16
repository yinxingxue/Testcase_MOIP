# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 15:42:17 2018

@author: Yinxing Xue
"""
import math
import numpy as np
from moipProb import MOIPProblem 
from moipSol import BaseSol
from naiveSol import NaiveSol
from moipSol import CplexSolResult
from mooUtility import MOOUtility 
from decimal import Decimal

class CwmoipSol(NaiveSol):  
    'define the CWMOIP solution of a MOBIP'
    def __init__(self, moipProblem):  
        #override parent initializer  
        NaiveSol.__init__(self,moipProblem)  
        #each sparse map is to represent extra constraints in inequation, and use the list to store all the inequation constraints
        self.sparseInequationsMapList = [] 
        #each sparse map is to represent extra constraints in inequation, and use the list to store all the equation constraints
        self.sparseEquationsMapList = [] 
        #the variable to record the original objective
        self.oriObj = None
       
        
    """
    model the problem as a single objective problem, and preparation solver for this
    override the parent method
    """
    def prepare(self):
        BaseSol.prepare(self)
        objName = self.solver.objective.get_name()
        linearCoeff = self.solver.objective.get_linear()
        objSense = self.solver.objective.get_sense()
        self.oriObj = (objName,linearCoeff,objSense)
        
    #override the parent method 
    def execute(self):    
        k = len(self.moipProblem.attributeMatrix)
        solutionMap={}
        #swap the 3rd and 4th obj for testing purpose
        #temp = self.moipProblem.attributeMatrix[2]
        #self.moipProblem.attributeMatrix[2] =  self.moipProblem.attributeMatrix[3] 
        #self.moipProblem.attributeMatrix[3] = temp
        objMatrix = np.array(self.moipProblem.attributeMatrix)
        solutionMap = self.solveBySingleObj(self.sparseInequationsMapList,self.sparseEquationsMapList, objMatrix, objMatrix,k, solutionMap, self.cplexResultMap)
        self.buildCplexPareto()
        
    def solveBySingleObj(self, inequationsMapList,equationsMapList,  objMatIn, objMatOut,k, solutionMap, resultMap):
        solutionMapOut = {}
        lbs= np.zeros((1,self.moipProblem.featureCount))
        ubs= np.ones((1,self.moipProblem.featureCount))
        feasibleFlag = False
        if k == 1 :
            # The single-objective problem
            (rsltObj,rsltXvar,rsltSolString)=  self.intlinprog (objMatOut[k-1],inequationsMapList,equationsMapList,lbs,ubs)
            #check whether it is optimal
            if(rsltSolString.find("optimal")>=0):
                cplexResults = CplexSolResult(rsltXvar,rsltSolString,self.moipProblem)
                self.addTocplexSolutionSetMap(cplexResults)
                solutionMapOut[cplexResults.getResultID()] = rsltXvar
        else: 
            fGUB=np.zeros(k)
            fGLB=np.zeros(k)
            fRange=np.zeros(k)
            w= Decimal(1.0)
            for i in range(0,k):
                feasibleFlag= True 
                (rsltObj,rsltXvar,rsltString) = self.intlinprog (objMatOut[i],inequationsMapList,equationsMapList,lbs,ubs)   
                if (rsltString.find("optimal")>=0):
                    fGLB[i] = 1.0* MOOUtility.round(rsltObj)
                    objOutNeg =  objMatOut[i] * (-1)
                    rslt2Obj,rslt2Xvar,rslt2String= self.intlinprog(objOutNeg,inequationsMapList,equationsMapList,lbs,ubs)
                    fGUB[i] = -1.0 * MOOUtility.round(rslt2Obj)
                    fRange[i] = fGUB[i]-fGLB[i] +1
                    w =  w*  MOOUtility.round(fRange[i])
                else:
                    feasibleFlag=False
                    break
                #end of if-esle
            #end of for
            if (feasibleFlag==True):
                w = Decimal(1)/ w
                w =float(w)
                l = fGUB[k-1]
                #shallow copy 
                new_inequationsMapList = list(inequationsMapList)
                new_equationsMapList= list(equationsMapList)
                while True:
                    # Step 1: Solve the CW(k-1)OIP problem with l  
                    solutions = []
                    objMat_out1 =np.zeros((k-1,self.moipProblem.featureCount))
                    for i in range(0,k-1):
                        objMat_out1[i]= objMatOut[i]+ w*objMatOut[k-1]
                    lastConstr = {}
                    if len(new_inequationsMapList) > 0:
                        lastConstr = new_inequationsMapList[len(new_inequationsMapList)-1]
                    if len(inequationsMapList)> 0 and MOOUtility.arrayEqual(lastConstr,objMatIn[k-1]):
                        lastConstr[self.moipProblem.featureCount]= l
                    else:
                        #add the new constraint to new_inequationsMapList
                        self.addNewConstrToInequationsMapList(new_inequationsMapList,objMatIn[k-1],l )
                    solutions = self.solveBySingleObj(new_inequationsMapList,new_equationsMapList, objMatIn, objMat_out1,k-1,solutionMap, resultMap)
                    if  len(solutions)  ==0:
                        break
                    else:
                        #Step 2: put ME into E, find the new l
                        solutionMap= {**solutionMap,**solutions}
                        solutionMapOut = {**solutionMapOut,**solutions}
                        l = self.getMaxForObjKonMe(objMatIn[k-1],solutions)
                        lastConstr = new_inequationsMapList[len(new_inequationsMapList)-1]
                        lastConstr[self.moipProblem.featureCount]= l
               #end of while
            #end of if
        return solutionMapOut
    
    
    def addNewConstrToInequationsMapList(self, inequationsMapList,objIn,l ):
        newInequation = {}
        for i in range(0,len(objIn)):
            newInequation[i] = objIn[i]
        newInequation[len(objIn)] = l
        inequationsMapList.append(newInequation)
        return 
    
    def getMaxForObjKonMe(self, objIn,solutions):
        maxVal = float("-inf")
        for key in solutions:
            newSol= solutions[key]
            #newSol= map(int,solutions[key])
            array1 = np.array(objIn)
            array2 = np.array(newSol)
            solSum = np.dot(array1,array2) 
            if(solSum> maxVal):
               maxVal = solSum;
        result = MOOUtility.round(maxVal)
        result = result -1
        return result
    
    """             
    May not use lbs and ubs
    """
    def intlinprog(self,obj,inequationsMapList,equationsMapList,lbs,ubs):
        variableCount = self.moipProblem.featureCount
        constCounter = 0 
        tempConstrList = []
        #add the temp inequation constraints to the solver
        for ineqlDic in inequationsMapList:
            rows = []
            rs = float("-inf")
            variables = []
            coefficient = []
            for key in ineqlDic: 
                if key != variableCount:
                    variables.append('x'+str(key))
                    coefficient.append(ineqlDic[key])
                else: 
                    rs = ineqlDic[key]
            row=[]
            row.append(variables)
            row.append(coefficient)
            rows.append(row)       
            constCounter= constCounter+1
            constName= 'new_c'+str(constCounter)
            indices = self.solver.linear_constraints.add(lin_expr = rows, senses = 'L', rhs = [rs], names = [constName] )
            tempConstrList.append(constName)
        #add the temp equation constraints to the solver
        for eqlDic in equationsMapList:
            rows = []
            rs = float("-inf")
            variables = []
            coefficient = []
            for key in eqlDic: 
                if key != variableCount:
                    variables.append('x'+str(key))
                    coefficient.append(eqlDic[key])
                else: 
                    rs = eqlDic[key]
            row=[]
            row.append(variables)
            row.append(coefficient)
            rows.append(row)       
            constCounter= constCounter+1
            constName= 'new_c'+str(constCounter)
            indices = self.solver.linear_constraints.add(lin_expr = rows, senses = 'E', rhs = [rs], names = [constName] )
            tempConstrList.append(constName)
        #reset the objective
        self.solver.objective.set_name("tempObj")
        coff= obj.tolist()
        indics= list(range(0,variableCount))
        self.solver.objective.set_linear(zip(indics,coff))
        self.solver.objective.set_sense(self.solver.objective.sense.minimize)
        #solve the problem
        self.solveCounter += 1
        self.solver.solve()
      
        rsltXvar = []
        rsltObj = float("+inf")
        rsltSolString = self.solver.solution.get_status_string()
        if(rsltSolString.find("optimal")>=0):
            #bug fixed here, rsltSol should not be returned as the constraints will be modified at the end of the method
            #rsltSol = self.solver.solution
            rsltXvar = self.solver.solution.get_values()
            rsltObj =  self.solver.solution.get_objective_value()
        #remove the temp constraints
        self.solver.linear_constraints.delete(tempConstrList)
        return (rsltObj,rsltXvar,rsltSolString)
 
if __name__ == "__main__":
    prob = MOIPProblem(2,3976,1)  
    prob.displayObjectiveCount()
    prob.displayFeatureCount()
    prob.exetractFromFile("../test/tri_input_make_bigM.txt")
    prob.displayObjectives()
    prob.displayVariableNames()
    prob.displayObjectiveSparseMapList()
    prob.displaySparseInequationsMapList()
    prob.displaySparseEquationsMapList()
    prob.displayAttributeMatrix()
    
    sol= CwmoipSol(prob)
    sol.prepare()
    sol.execute()
    sol.outputCplexParetoMap("../result/tri-obj/Pareto_tri_make_bigM.txt")
    sol.outputFullCplexResultMap("../result/tri-obj/FullResult_tri_make_bigM.txt")
    sol.displaySolvingAttempts()
    sol.displayObjsBoundsDictionary()
    sol.displayCplexSolutionSetSize()
    sol.displayCplexResultMap()
    sol.displayFullCplexResultMap()
    sol.displayCplexParetoSet()
    #sol.displayVariableLowerBound()
    #sol.displayVariableUpperBound()
    #sol.displayVariableTypes()
    #sol.displayVariableNames()
else:
    print("cwmoipSol.py is being imported into another module")
