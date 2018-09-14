# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 16:46:37 2018

@author: Yinxing Xue
"""
from moipProb import MOIPProblem 
from moipSol import BaseSol
from moipSol import CplexSolResult
from mooUtility import MOOUtility 
import math

class NaiveSol(BaseSol):  
    'define the epsilon-constraint solution of a MOBIP'
    def __init__(self, moipProblem):  
        #调用父类的构函  
        BaseSol.__init__(self,moipProblem)  
        self.solveCounter = 0
        self.objConstrIndexList = []
        self.boundsDict = {}
       
    #覆写父类的方法  
    def execute(self):  
        print("%s" % ("Starting solving the problem with epsilon-constraint!")) 
        constCounter = self.solver.linear_constraints.get_num()
        self.objConstrIndexList =[]
        
        #dictionary for the UB and LB of each objective
        self.boundsDict = {}
        for k in range(1,len(self.moipProblem.attributeMatrix)):
            kthObj= self.moipProblem.attributeMatrix[k]
            ub,lb = self.calculteUBLB(kthObj)
            self.boundsDict[k]= (ub,lb)
            
        #convert the k-th objective as constraint 
        for k in range(1,len(self.moipProblem.attributeMatrix)):
            kthObj= self.moipProblem.attributeMatrix[k]
            #add the constraint
            if  len(kthObj)!=  self.moipProblem.featureCount:
                 raise Exception('input not consistent', 'eggs')
            rows = []
            (ub,lb)=  self.boundsDict[k]
            rs1 = lb
            rs2 = ub
            variables = []
            coefficient = []
            for index in range(0,len(kthObj)): 
                variables.append('x'+str(index))
                coefficient.append(kthObj[index])
            row=[]
            row.append(variables)
            row.append(coefficient)
            rows.append(row)       
            #constCounter= constCounter+1
            #one objective constraint  has two parts, need to be added seperately
            constName= 'o'+str(k)+'_R'
            indices = self.solver.linear_constraints.add(lin_expr = rows, senses = 'L', rhs = [rs2], names = [constName])
            self.objConstrIndexList.append(constName)
            self.constrIndexList.append(indices)
            #add the left part
            constName= 'o'+str(k)+'_L'
            indices = self.solver.linear_constraints.add(lin_expr = rows, senses = 'G', rhs = [rs1], names = [constName])
            self.objConstrIndexList.append(constName)
            self.constrIndexList.append(indices)
        
        #start to solving
        print ("Before the epsilon constraint, the adjusted UBs of the objective 2 to k: ", self.getSolverObjConstraintUBs())
        self.travelAllObjConstr(1)
        print ("After the epsilon constraint, the adjusted UBs of the objective 2 to k: ", self.getSolverObjConstraintUBs())
        #debugging purpose
        #print (self.solveCounter)
        self.buildCplexPareto()
        
        
    """
    level:
    passDict: the dictionary to travese, the key is the k-th objective, the value is the adjusted UB
    """
    def travelAllObjConstr(self, level = 1, passDict={}):
        if level == self.moipProblem.objectiveCount-1:
            #no need to go deep
            (ub,lb)=  self.boundsDict[level]
            ub_relaxed= math.ceil(ub)
            lb_relaxed= math.floor(lb)
            for value in range(ub_relaxed,lb_relaxed-1,-1):
                passDict['o'+str(level)+'_R']=value
                self.updateSolver(passDict)
                self.solveCounter += 1
                #continue
                self.solver.solve()
                #debugging purpose
                #print ("Solution value  = ", self.solver.solution.get_objective_value())
                #debugging purpose
                #xsol = self.solver.solution.get_values()
                #debugging purpose
                #print ('xsol = ',  xsol )
                if(self.solver.solution.get_status_string().find("optimal")==-1):
                    continue
                cplexResults = CplexSolResult(self.solver.solution.get_values(),self.solver.solution.get_status_string(),self.moipProblem)
                self.addTocplexSolutionSetMap(cplexResults)
        else: 
            (ub,lb)=  self.boundsDict[level]
            ub_relaxed= math.ceil(ub)
            lb_relaxed= math.floor(lb)
            for value in range(ub_relaxed,lb_relaxed-1,-1):
                passDict['o'+str(level)+'_R']=value
                self.travelAllObjConstr(level+1,passDict) 
                
    def updateSolver(self,passDict):
        for constrName in passDict:
            self.solver.linear_constraints.set_rhs(constrName, passDict[constrName])
            
    def getSolverObjConstraintUBs(self):
        objUBs = []
        for k in range(1,len(self.moipProblem.attributeMatrix)):
            constrName= 'o'+str(k)+'_R'
            objUB = self.solver.linear_constraints.get_rhs(constrName)
            objUBs.append(objUB)
        return objUBs
        
    def calculteUBLB(self,obj):
        ub = 0.0
        lb = 0.0
        for value in obj:
            if value > 0:
                ub = ub+ value
            else:
                lb = lb + value
        return ub, lb
    
    def displaySolvingAttempts(self):
        print ("Total Sovling Attempts: %s" % self.solveCounter) 
      
    def displayObjsBoundsDictionary(self):
        print ("Objectives' Bound Dictionary: %s" % self.boundsDict) 
    
if __name__ == "__main__":
    prob = MOIPProblem(2,173,1)  
    prob.displayObjectiveCount()
    prob.displayFeatureCount()
    prob.exetractFromFile("../test/variant_bi_input_make_bigM.txt")
    prob.displayObjectives()
    prob.displayVariableNames()
    prob.displayObjectiveSparseMapList()
    prob.displaySparseInequationsMapList()
    prob.displaySparseEquationsMapList()
    prob.displayAttributeMatrix()
    
    sol= NaiveSol(prob)
    sol.prepare()
    sol.execute()
    sol.outputCplexParetoMap("../result/variant_bi-obj/Pareto_variant_bi_make.txt")
    sol.outputFullCplexResultMap("../result/variant_bi-obj/FullResult_variant_bi_make.txt")
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
    print("naiveSol.py is being imported into another module")
