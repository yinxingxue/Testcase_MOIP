# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 16:49:14 2018

@author: Yinxing Xue
"""
from moipProb import MOIPProblem 
from mooUtility import MOOUtility 
import numpy as np
import cplex
from cplex import Cplex
from cplex.exceptions import CplexError

class BaseSol:
    'define the basic solution of a MOBIP'
    TimeOut = 5000
    DeterTimeOut = 5000
    
    def __init__(self, moipProblem):
        #instance variable: the solver instance
        self.solver = None
        #instance variable: the problem instance 
        self.moipProblem = None 
        #instance variable: the solution set found by solver 
        self.cplexSolutionSet = [] 
        #instance variable: the solution map, the key is the solution obj values, the value is the solution 
        self.cplexResultMap= {}
        #instance variable: the map of the solutions in the pareto front  
        self.cplexParetoSet= {}
        #instance variable: the list of the lower bounds of variables 
        self.lb=[] 
        #instance variable: the list of the upper bounds of variables
        self.ub=[]
        #instance variable: the list of types of variables 
        self.types=[]
        #instance variable: the variable values of the solution found by the solver 
        self.xvar=[]
        #instance variable: the index lists of the constraints of the inequation and equation 
        self.constrIndexList =[]
        self.moipProblem = moipProblem
        
        
    def execute(self):
        print("%s" % ("Starting solving the problem with BaseSol execution!"))
        self.solver.solve()
        #debugging purpose
        #print ("Solution value  = ", self.solver.solution.get_objective_value())
        #debugging purpose
        #xsol = self.solver.solution.get_values()
        #debugging purpose
        #print ('xsol = ',  xsol )
        if(self.solver.solution.get_status_string().find("optimal")==-1):
            return
        cplexResults = CplexSolResult(self.solver.solution.get_values(),self.solver.solution.get_status_string(),self.moipProblem)
        self.addTocplexSolutionSetMap(cplexResults)
        self.buildCplexPareto()
        
    def buildCplexPareto(self):
        inputPoints = [list(map(float,resultID.split('_'))) for resultID in self.cplexResultMap.keys()]
        #debugging purpose
        #print (inputPoints)
        paretoPoints, dominatedPoints = MOOUtility.simple_cull(inputPoints,MOOUtility.dominates)
        #print ("Pareto size: ", len(paretoPoints), " Pareto front: ",  paretoPoints)
        self.cplexParetoSet= paretoPoints
    
    """
    model the problem as a single objective problem, and preparation solver for this
    """
    def prepare(self):
        self.solver = cplex.Cplex()
        self.solver.set_results_stream(None)
        self.solver.set_warning_stream(None)
        self.solver.set_error_stream(None)
        #self.solver.parameters.timelimit.set(BaseSol.TimeOut)
        #self.solver.parameters.dettimelimit.set(BaseSol.DeterTimeOut)
        self.solver.parameters.threads.set(4)
        self.solver.parameters.parallel.set(-1)
        self.solver.objective.set_sense(self.solver.objective.sense.minimize)
        self.ub = [1]*self.moipProblem.featureCount
        self.lb = [0]*self.moipProblem.featureCount
        self.types = 'B'* self.moipProblem.featureCount
        self.xvar = ['x'+str(i) for i in range(0,self.moipProblem.featureCount) ]
        firstObj=self.moipProblem.attributeMatrix[0]
        #add the objective and variables to the solver
        self.solver.variables.add(obj = firstObj, lb = self.lb, ub = self.ub, types = self.types, names = self.xvar )
        self.solver.objective.set_name("ori_Obj")
        variableCount = self.moipProblem.featureCount
        constCounter =0 
        self.constrIndexList =[]
        #add the inequation constraints to the solver
        ineqlDic=None
        for ineqlDic in self.moipProblem.sparseInequationsMapList:
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
            constName= 'c'+str(constCounter)
            indices = self.solver.linear_constraints.add(lin_expr = rows, senses = 'L', rhs = [rs], names = [constName] )
            self.constrIndexList.append(indices)
        if ineqlDic!=None:
            del(ineqlDic)
        #add the equation constraints to the solver
        eqlDic=None
        for eqlDic in self.moipProblem.sparseEquationsMapList:
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
            constName= 'c'+str(constCounter)
            indices = self.solver.linear_constraints.add(lin_expr = rows, senses = 'E', rhs = [rs], names = [constName] )
            self.constrIndexList.append(indices)
        if eqlDic!=None:
            del(eqlDic)
        #for debugging purpose
        #print (self.constrIndexList)
        #for debugging purpose
        #self.__private_testConstraints__()
    
    def addTocplexSolutionSetMap(self,cplexResults):
        if(cplexResults.getResultID() in self.cplexResultMap.keys()): 
            return
        self.cplexSolutionSet.append(cplexResults)
        self.cplexResultMap[cplexResults.getResultID()] = cplexResults 
        print ("BestObj: %f 1stObj: %f" % (cplexResults.getThisObj(), cplexResults.getKthObj(0))) 
        
    def displayVariableLowerBound(self):
        print ("Variable Loweer Bounds: %s" % self.lb) 
    
    def displayVariableUpperBound(self):
        print ("Variable Upper Bounds: %s" % self.ub) 
        
    def displayVariableTypes(self):
        print ("Variable Types: %s" % self.types) 
        
    def displayVariableNames(self):
        print ("Variable Names: %s" % self.xvar) 
        
    def displayCplexSolutionSet(self):
        print ("Total Solution Set: %s" % self.cplexSolutionSet) 
    
    def displayCplexSolutionSetSize(self):
        print ("Total Solution Set Size: %s" % len(self.cplexSolutionSet)) 
        
    def displayCplexResultMap(self):
        print ("Cplex Results Map: %s" % self.cplexResultMap.keys()) 
        
    def displayFullCplexResultMap(self):
        print ("Cplex Results Map: ")
        for key in self.cplexResultMap.keys():
            cplexResult = self.cplexResultMap[key]
            print(key,": ", cplexResult.xvar)
        
    def displayCplexParetoSet(self):
        print ("Total Pareto size: ", len(self.cplexParetoSet))
        print ("Cplex Pareto front: ",  self.cplexParetoSet) 
        
    def outputCplexParetoMap(self,file):
        file = open(file,"w") 
        file.write(';'.join(list(map(str,self.cplexParetoSet)))) 
        file.close() 
        
    def __private_testConstraints__(self):
        for i in range(self.solver.linear_constraints.get_num()):
            print (self.solver.linear_constraints.get_rows(i), self.solver.linear_constraints.get_senses(i), self.solver.linear_constraints.get_rhs(i))

class CplexSolResult:
    'define the basic solution of a MOBIP'   
#    def __init__(self, solverSolution, moipProblem):
#        self.xvar = []
#        self.objs = []
#        self.solveStatus = ""
#        self.ResultID = ""
#        self.xvar = solverSolution.get_values()
#        objMatrix = moipProblem.attributeMatrix
#        self.objs = self.getAllObjs(self.xvar,objMatrix)
#        self.thisObj = solverSolution.get_objective_value()
#        self.solveStatus = solverSolution.get_status_string()
#        for i in range(0,len(self.objs)):
#            value = self.objs[i]
#            valueString = "%.2f" % value
#            self.ResultID += valueString
#            if i != len(self.objs) -1:
#                self.ResultID += '_'
    
    def __init__(self,rsltXvar,rsltSolString, moipProblem):
        self.xvar = []
        self.objs = []
        self.solveStatus = ""
        self.ResultID = ""
        self.xvar = rsltXvar
        objMatrix = moipProblem.attributeMatrix
        self.objs = self.getAllObjs(self.xvar,objMatrix)
        self.thisObj = self.objs[0]
        self.solveStatus = rsltSolString
        for i in range(0,len(self.objs)):
            value = self.objs[i]
            valueString = "%.2f" % value
            self.ResultID += valueString
            if i != len(self.objs) -1:
                self.ResultID += '_'
    
    def getAllObjs(self,xval,objMatrix):
        # dimension: k* variableCount
        matA = np.array(objMatrix)
        twoDArray= []
        twoDArray.append(xval)
        # dimension: variableCount * 1
        matB = np.array(twoDArray).transpose()
        allObjs= np.dot(matA, matB)
        allObjs = allObjs.transpose()
        allObjsList = allObjs.tolist()
        return allObjsList[0]
    
    def getResultID(self):
        return self.ResultID
    
    def getThisObj(self):
        return self.thisObj
    
    def getKthObj(self,k):
        if k >= len(self.objs) :
            return None
        elif k< len(self.objs) or k> -len(self.objs): 
            return self.objs[k]
        else: 
            return None
    
if __name__ == "__main__":
    prob = MOIPProblem(4,43,3)  
    prob.displayObjectiveCount()
    prob.displayFeatureCount()
    prob.exetractFromFile("../test/parameter_wp1.txt")
    prob.displayObjectives()
    prob.displayVariableNames()
    prob.displayObjectiveSparseMapList()
    prob.displaySparseInequationsMapList()
    prob.displaySparseEquationsMapList()
    prob.displayAttributeMatrix()
    
    sol= BaseSol(prob)
    sol.prepare()
    sol.execute()
    sol.outputCplexParetoMap("../result/Pareto.txt")
    sol.displayCplexSolutionSetSize()
    sol.displayCplexResultMap()
    sol.displayVariableLowerBound()
    sol.displayVariableUpperBound()
    sol.displayVariableTypes()
    sol.displayVariableNames()
else:
    print("moipSol.py is being imported into another module")
