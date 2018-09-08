# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 10:28:33 2018

@author: Yinxing Xue
"""
import math
import numpy as np
from moipProb import MOIPProblem 
from moipSol import BaseSol
from cwmoipSol import CwmoipSol
from normalConstraint import UtopiaPlane
from normalConstraint import SolRep
from moipSol import CplexSolResult
from mooUtility import MOOUtility 
from cplex import Cplex
from cplex.exceptions import CplexError



class NcgopSol(CwmoipSol):  
    'define the NC+H&R solution of a MOBIP'
    def __init__(self, moipProblem):  
        #override parent initializer  
        CwmoipSol.__init__(self,moipProblem)
        #represent the coefficient of the original inequation constraints
        self.origi_A = [] 
        #represent the right side value of the original inequation constraints
        self.origi_B = []
        #represent the coefficient of the original equation constraints
        self.origi_Aeq = [] 
        #represent the right side value of the original equation constraints
        self.origi_Beq = []
        #represent the coefficient of the extra inequation constraints
        self.extra_A = [] 
        #represent the right side value of the extra inequation constraints
        self.extra_B = []
        #represent the coefficient of the extra equation constraints
        self.extra_Aeq = [] 
         #represent the right side value of the extra equation constraints
        self.extra_Beq = []
        self.utopiaPlane = None
        self.pGenerator = None
        self.objNo = moipProblem.objectiveCount  
        self.varNv= moipProblem.featureCount
        self.builtEqualAndInequalMaps(moipProblem) 
    
    def builtEqualAndInequalMaps(self,moipProblem):
        for i in range(0, len(moipProblem.sparseInequationsMapList)):
            inequal = moipProblem.sparseInequationsMapList[i].copy()
            right = inequal[self.varNv]
            del inequal[self.varNv]
            #for testing purpose
            #print (inequal,moipProblem.sparseInequationsMapList[i])
            self.origi_A.append(inequal)
            self.origi_B.append(right)
        for i in range(0, len(moipProblem.sparseEquationsMapList)):
            equal = moipProblem.sparseEquationsMapList[i].copy()
            right = equal[self.varNv]
            del equal[self.varNv]
            #for testing purpose
            #print (equal,moipProblem.sparseEquationsMapList[i])
            self.origi_Aeq.append(equal)
            self.origi_Beq.append(right)
        assert len(self.origi_A)== len(self.origi_B)     
        assert len(self.origi_Aeq)== len(self.origi_Beq)     
        
    #override the parent method 
    def execute(self):
        temp = self.moipProblem.attributeMatrix[2]
        self.moipProblem.attributeMatrix[2] =  self.moipProblem.attributeMatrix[3] 
        self.moipProblem.attributeMatrix[3] = temp
        
        self.utopiaPlane = UtopiaPlane(self.moipProblem,self.solver);
        self.utopiaPlane.calculate();
        print("utopiaPlane done.");
        self.pGenerator= SolRep(self.utopiaPlane.y_up, self.varNv, 1000)
        objMatrix = np.array(self.moipProblem.attributeMatrix)
        self.pGenerator.setParas(objMatrix, self.origi_A , self.origi_B, self.origi_Aeq, self.origi_Beq)
        points = self.pGenerator.calculate()
        print("pGenerator done.")
        
        #for utopiaPlane calculation, to assure the completeness of resolving, we cannot set timeout for this.cplex. 
		 #then for NCPDG, we can give the timeout for intlinprog timeout for each execution 
		 #for non-Linux projects
        if self.varNv < 2000:
            self.solver.parameters.timelimit.set(BaseSol.TimeOut)
            self.solver.parameters.dettimelimit.set(BaseSol.DeterTimeOut)
        else :
            self.solver.parameters.workmem.set(SolRep.WorkMem)
            self.solver.parameters.dettimelimit.set(SolRep.DeterTimeOut) 
            
        counter = 0
        for p_k in points:
            counter += 1
            print ("using p_k: ", str(counter))
            self.calculate(p_k, self.utopiaPlane.y_up,self.utopiaPlane.y_ub, self.utopiaPlane.y_lb)
        print ("Find solution num: ", len(self.cplexSolutionSet))   
        self.buildCplexPareto()
        
    def  calculate(self, p_k, y_up, y_ub, y_lb):
        fCWMOIP = float('nan')
        No = self.objNo
        Nv = self.varNv
        
        extra_A1 = []
        objMatrix = np.array(self.moipProblem.attributeMatrix)
        SolRep.appendToSparseMapList(extra_A1,objMatrix[0:No-1])
        extra_B1 = p_k[0:No-1]
        
        ub = [1]*Nv
        lb = [0]*Nv
        
        ff = []
        for i in range(No-1,-1,-1):
            if i == No-1:
                ff = objMatrix[i]
            else:
                w = 1.0 /(y_ub[i]-y_lb[i]+1)
                ff = ff+ w*objMatrix[i]
        
        (rstObj, rstXvar, rstStatusString) = NcgopSol.intlinprog (self.solver, self.xvar, ff, extra_A1, extra_B1, [], [], lb, ub)
        if(rstStatusString.find("optimal")>=0): 
            newff = np.reshape(ff, (1, len(ff)))
            new_A1 = []
            SolRep.appendToSparseMapList(new_A1,newff)
            new_b1 = np.dot(rstXvar, ff)
        if(rstStatusString.find("optimal")>=0): 
            #newff = np.reshape(ff, (1, len(ff)))
            cplexResults = CplexSolResult(rstXvar,rstStatusString,self.moipProblem)
            self.addTocplexSolutionSetMap(cplexResults)
            fCWMOIP = np.dot(rstXvar, ff)
        return fCWMOIP
    
    @classmethod  
    def intlinprog (cls, cplex, xVar, ff, extra_A1, extra_B1, extra_Aeq1, extra_Beq1, lbs, ubs):
        origiCplex = cplex 
        if cplex == None:
            try:
                cplex = cplex.Cplex()
                cplex.set_results_stream(None)
                cplex.set_warning_stream(None)
                cplex.set_error_stream(None)
                cplex.parameters.timelimit.set(BaseSol.TimeOut)
                cplex.parameters.dettimelimit.set(BaseSol.DeterTimeOut)
            except CplexError as exc:
                print ("Concert exception caught: ", exc.args)
        if xVar == None:
            var_names = ['x'+str(i) for i in range(0,len(ff)) ]
            #important it is type Binary
            var_types = 'B'* (len(ff))
            cplex.variables.add(lb = lbs, ub = ubs, types = var_types, names = var_names) 
            
        # add ff as the coefficient for the objective
        cplex.objective.set_name("tempObj")
        coff= ff.tolist()
        indics= list(range(0,len(ff)))
        cplex.objective.set_linear(zip(indics,coff))
        cplex.objective.set_sense(cplex.objective.sense.minimize)
        
        #the list to store the temp constraints
        tempConstNames1 = []
        constCounter = 0 
        #add the temp extra inequation constraints to the solver
        inEquationRows = []
        for i in range(0,len(extra_A1)):
            ineqlDic= extra_A1[i]
            variables = []
            coefficient = []
            for key in ineqlDic: 
                variables.append('x'+str(key))
                coefficient.append(ineqlDic[key])
            row=[]
            row.append(variables)
            row.append(coefficient)
            inEquationRows.append(row)  
            constCounter= constCounter+1
            constName= 'new_ie'+str(constCounter)
            tempConstNames1.append(constName)
        indices = cplex.linear_constraints.add(lin_expr = inEquationRows, senses = 'L'*len(extra_A1), rhs =  extra_B1, names = tempConstNames1)
        #testing purpose
        #print (indices)
        
        tempConstNames2 = []
        constCounter = 0 
        #add the temp extra equation constraints to the solver
        equationRows = []
        for i in range(0,len(extra_Aeq1)):
            eqlDic= extra_Aeq1[i]
            variables = []
            coefficient = []
            for key in eqlDic: 
                variables.append('x'+str(key))
                coefficient.append(eqlDic[key])
            row=[]
            row.append(variables)
            row.append(coefficient)
            equationRows.append(row)   
            constCounter= constCounter+1
            constName= 'new_e'+str(constCounter)
            tempConstNames2.append(constName)
        indices = cplex.linear_constraints.add(lin_expr = equationRows, senses = 'E'*len(extra_Aeq1), rhs =  extra_Beq1, names = tempConstNames2)
        #testing purpose
        #print (indices)
        
        cplex.solve()
        
        rsltObj = float("inf")
        rsltSolString = cplex.solution.get_status_string()
        rsltXvar = []
        if(rsltSolString.find("optimal")>=0):
            #bug fixed here, rsltSol should not be returned as the constraints will be modified at the end of the method
            #rsltSol = self.solver.solution
            rsltXvar = cplex.solution.get_values()
            rsltObj =  cplex.solution.get_objective_value()
        
        if origiCplex == None:
            cplex.end()
        else:
            #remove the temp constraints    
            cplex.linear_constraints.delete(tempConstNames1)
            cplex.linear_constraints.delete(tempConstNames2)
        return (rsltObj, rsltXvar, rsltSolString)

if __name__ == "__main__":
    prob = MOIPProblem(4,1244,3)  
    prob.displayObjectiveCount()
    prob.displayFeatureCount()
    prob.exetractFromFile("../test/parameter_ecos1.txt")
    prob.displayObjectives()
    prob.displayVariableNames()
    #prob.displayObjectiveSparseMapList()
    #prob.displaySparseInequationsMapList()
    #prob.displaySparseEquationsMapList()
    #prob.displayAttributeMatrix()
    
    sol= NcgopSol(prob)
    sol.prepare()
    sol.execute()
    sol.outputCplexParetoMap("../result/parameter_ecos1.txt")
    sol.displaySolvingAttempts()
    sol.displayObjsBoundsDictionary()
    sol.displayCplexSolutionSetSize()
    sol.displayCplexResultMap()
    sol.displayCplexParetoSet()
    sol.displayVariableLowerBound()
    sol.displayVariableUpperBound()
    sol.displayVariableTypes()
    sol.displayVariableNames()
else:
    print("ncgopSol.py is being imported into another module")
        
        
        