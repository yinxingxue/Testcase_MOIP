# -*- coding: utf-8 -*-
"""
Created on Sat Jun 30 13:44:12 2018

@author: Yinxing Xue
"""
import random
import numpy as np
from moipSol import CplexSolResult
from moipSol import BaseSol 
import cplex
from cplex import Cplex
from cplex.exceptions import CplexError


class UtopiaPlane():
    
    TOL = 1e-5
    
    'define the calculation and implementation of Utopia Plane'
    def __init__(self, moipProblem, cplex):
        #input
        self.cplex = None
        self.attributeMatrix_in  = [[]]
        self.extraInequationsMapList = [] 
        self.extraEquationsMapList = []
        #output
        self.x_up = [[]]
        self.y_up = [[]]
        self.y_ub=  []
        self.y_lb=  []
        self.xVar = []
        self.__private_initialize__(moipProblem,cplex)
        
    def __private_initialize__(self,moipProblem,cplex):
        self.cplex = cplex
        self.moipProblem = moipProblem
        self.attributeMatrix_in= moipProblem.attributeMatrix
        self.extraInequationsMapList = []
        self.extraEquationsMapList = []
        self.x_up = np.empty([len(self.attributeMatrix_in),len(self.attributeMatrix_in[0])])
        self.y_up = np.empty([len(self.attributeMatrix_in),len(self.attributeMatrix_in)])
        self.y_ub = np.empty(len(self.attributeMatrix_in))
        self.y_lb = np.empty(len(self.attributeMatrix_in))
        self.xVar = cplex.variables
        
    def calculate(self):
        utopiaSols = {}
        for i in range(0,len(self.attributeMatrix_in)):
            target = np.array(self.attributeMatrix_in[i])
            solutions = UtopiaPlane.intlinprog(self.cplex, self.xVar, target, self.extraInequationsMapList, self.extraEquationsMapList, None, None)
            solution = solutions[0]
            optSolution = None
            cplexResult = CplexSolResult(solution[1],"optimal",self.moipProblem)
            if len(solutions)==1:
                optSolution = cplexResult
                utopiaSols[optSolution.getResultID()] = optSolution
            elif cplexResult.getResultID() not in utopiaSols and len(solutions)> 1:
                optSolution = cplexResult
                for j in range(0,len(solutions)):
                    solution = solutions[j]
                    cplexResult2 = CplexSolResult(solution[1],"optimal",self.moipProblem)
                    if j == 0:     
                        optSolution = cplexResult2                        
                utopiaSols[optSolution.getResultID()] = optSolution    
            elif cplexResult.getResultID() in utopiaSols and len(solutions)>1:            
                best = float("+inf")
                for j in range(1,len(solutions)):
                    """
                    debug purpose
                    """
                    if i == 2 and j == 1:
                        solution = solutions[j]
                        cplexResult2 = CplexSolResult(solution[1],"optimal",self.moipProblem)
                        optSolution = cplexResult2
                        break
                    """
                    end of debugging purpose
                    """
                    solution = solutions[j]
                    cplexResult2 = CplexSolResult(solution[1],"optimal",self.moipProblem)
                    if cplexResult2.getResultID() not in utopiaSols and cplexResult2.getThisObj() < best:
                        best = cplexResult2.getThisObj() 
                        optSolution = cplexResult2
                    #end of if
                #end of for
                utopiaSols[optSolution.getResultID()] = optSolution
            #end of if-elif
            X = np.array(optSolution.xvar)
            self.x_up[i] = X
            self.y_up[i] = UtopiaPlane.calculateObjs(optSolution.xvar,self.attributeMatrix_in)
            y1 = optSolution.getKthObj(i)
            self.y_lb[i] = y1
            
            negTarget = target * (-1.0)
            negSolutions = UtopiaPlane.intlinprog(self.cplex, self.xVar, negTarget, self.extraInequationsMapList, self.extraEquationsMapList, None, None)
            negSolution = negSolutions[0]
            X2 = negSolution[1]
            y2 = negSolution[0]* (-1.0)
            self.y_ub[i] = y2;
        #end of for
        return
    
    @classmethod
    def calculateObjs(cls,xval,objMatrix):
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
    
    @classmethod
    def intlinprog(cls, cplex, xVar, target, sparseInequationsMapList, sparseEquationsMapList, lb, up):
        variableCount =  xVar.get_num()
        constCounter = 0 
        tempConstrList = []
        #add the temp inequation constraints to the solver
        ineqlRS = []
        rows = []
        for ineqlDic in sparseInequationsMapList:
           
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
            ineqlRS.append(rs)
        #indices: test purpose 
        indices = cplex.linear_constraints.add(lin_expr = rows, senses = 'L'*len(rows), rhs = ineqlRS)
        #print (indices)
        
        #add the temp equation constraints to the solver
        eqlRS = []
        rows = []
        for eqlDic in sparseEquationsMapList:
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
            eqlRS.append(rs)
        #indices: test purpose 
        indices = cplex.linear_constraints.add(lin_expr = rows, senses = 'E'*len(rows), rhs = eqlRS)
        #print (indices)   
            
        #reset the objective
        cplex.objective.set_name("tempObj")
        coff= target.tolist()
        indics= list(range(0,variableCount))
        cplex.objective.set_linear(zip(indics,coff))
        cplex.objective.set_sense(cplex.objective.sense.minimize)
        #reset the parameters 
        cplex.parameters.mip.pool.absgap.set(0.5)
        cplex.parameters.mip.pool.intensity.set(4)
        cplex.parameters.mip.pool.capacity.set(5)
        cplex.parameters.mip.limits.populate.set(10)
        cplex.parameters.mip.pool.replace.set(1)
        cplex.populate_solution_pool()
        
        solutionsNames = cplex.solution.pool.get_names()
        solutions = []
        opt = []
        #Create a container for the indices of optimal solutions.
        best = float("-inf")
        """
	     * Check which pool solutions are truly optimal; if the pool capacity
	     * exceeds the number of optimal solutions, there may be suboptimal
	     * solutions lingering in the pool.
        """
        for i in range(0,len(solutionsNames)):
            z = cplex.solution.pool.get_objective_value(i)
            # If this solution is better than the previous best, the previous
            # solutions must have been suboptimal; drop them all and count this one.
            if(z > best + UtopiaPlane.TOL):
                best = z 
                opt.clear()
                opt.append(i)
            #If this solution is within rounding tolerance of optimal, count it.
            elif z > best - UtopiaPlane.TOL: 
                opt.append(i)
                
        for i in opt:
            rsltObj = cplex.solution.pool.get_objective_value(i)
            rsltXvar =  cplex.solution.pool.get_values(i)
            solution = (rsltObj,rsltXvar)
            solutions.append(solution)
        
        cplex.linear_constraints.delete(tempConstrList)
        return solutions

class SolRep():
    'define the calculation and implementation of Representative Solutions'
    WorkMem = 2000
    DeterTimeOut = 10000
    XvarNames = None
    
    #the precision of generating random double between 0 and 1
    PRE_RAND = 1e+6
    
    def __init__(self, y_up, varNo, n):
        #input
        self.attributeMatrix_in  = [[]]
        self.y_up = y_up
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
        self.varNo = varNo
        self.n = n
        #output
        self.P = []
        self.xVar = []
        
    def calculate(self):
        No = len(self.y_up)
        Nv = self.varNo
        #generate the constant matrix V
        ConstantMatrix.initialize(self.y_up, No)
        V = ConstantMatrix.V
        #generate constant upper bounds and lower bounds
        ub = [1]*(Nv+No+1)
        ub[Nv:] = [float("inf")] * (len(ub) - Nv) 
        lb = [0]*(Nv+No+1)
        lb[Nv:] = [float("-inf")] * (len(lb) - Nv)
        
        self.extra_A = self.origi_A.copy()
        self.extra_B = self.origi_B.copy()
        self.extra_Aeq = self.origi_Aeq.copy()
        self.extra_Beq = self.origi_Beq.copy()
        negEye = np.eye(No,dtype= float) * (-1)
        zeroMat = np.zeros((No,1))
        zeroRightSide = np.zeros((No,1))
        extraEquationsMat= np.column_stack((self.attributeMatrix_in,negEye,zeroMat))
        SolRep.appendToSparseMapList(self.extra_Aeq,extraEquationsMat)
        SolRep.appendToSparseList(self.extra_Beq,zeroRightSide)
        cplex = SolRep.initializeCplex(Nv, No, self.extra_A, self.extra_B, self.extra_Aeq, self.extra_Beq, lb, ub) 
        
        #do the initialization of X0
        ini = np.random.randint(0,1000,size=[1,No])
        ini = ini / np.sum(ini)
        #debugging purpose
        #ini = [0.27834687389614976, 0.2571529494878135, 0.2991875662310138, 0.16531261038502296]
        X0 = np.dot(ini,self.y_up)[0]
        p = X0 
        self.P.append(p)
        
        for i in range(0,self.n):
              mult = np.random.rand(1,No-1)
              mult = mult[0]
              #debugging purpose
              #mult = [0.39541754214685954, 0.6591278732474594, 0.33765164373495815]
              mult = mult / np.linalg.norm (mult,2)
              D = np.dot(mult,V)
              
              #Finding the limit of lambda
              lambda_l = 0.0;
              lambda_u = 0.0;
           
              tempAeq2_mat = np.column_stack((np.zeros((No,Nv)), np.eye(No,dtype= float), (-1*D).transpose()))
              tempAeq2 = []
              SolRep.appendToSparseMapList(tempAeq2,tempAeq2_mat)
              Beq2 = X0
              tempBeq2 = []
              tempBeq2 = Beq2.tolist().copy()
              ff = np.zeros((1, Nv+No+1)) 
              ff = ff[0]
              ff[Nv+No] = 1.0
              
              self.xVar = SolRep.XvarNames
              (positiveRstVal, positiveRstStatus) = SolRep.mixintlinprog (cplex, self.xVar, ff, [] , [], tempAeq2,tempBeq2, lb,ub) 
              (negativeRstVal, negativeRstStatus) = SolRep.mixintlinprog (cplex, self.xVar, ff * (-1), [] , [], tempAeq2,tempBeq2, lb,ub) 
              if positiveRstStatus.find("optimal")> -1:
                  lambda_l = positiveRstVal 
              if negativeRstStatus.find("optimal")> -1:
                  lambda_u = negativeRstVal * -1.0
              
              lambdaV = SolRep.unifrnd(lambda_l, lambda_u)
              X0 = X0 + lambdaV * D
              self.P.append(X0)
              print ("add i: ", X0 )
        return self.P
    
    @classmethod
    def unifrnd(cls,lambda_l, lambda_u): 
        rand= random.uniform(0, SolRep.PRE_RAND)*1.0 / SolRep.PRE_RAND
        range1= lambda_u- lambda_l
        value= rand*range1+lambda_l
        return value
    
    @classmethod  
    def mixintlinprog(cls, cplex, xvar, ff, A2, B2, Aeq2, Beq2, lbs, ubs):
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
        if xvar == None:
            var_names = ['x_'+str(i) for i in range(0,len(ff)) ]
            var_types = 'C'* (len(ff))
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
        for i in range(0,len(A2)):
            ineqlDic= A2[i]
            variables = []
            coefficient = []
            for key in ineqlDic: 
                variables.append('x_'+str(key))
                coefficient.append(ineqlDic[key])
            row=[]
            row.append(variables)
            row.append(coefficient)
            inEquationRows.append(row)  
            constCounter= constCounter+1
            constName= 'new_ie'+str(constCounter)
            tempConstNames1.append(constName)
        indices = cplex.linear_constraints.add(lin_expr = inEquationRows, senses = 'L'*len(A2), rhs =  B2, names = tempConstNames1)
        #testing purpose
        #print (indices)
        
        tempConstNames2 = []
        constCounter = 0 
        #add the temp extra equation constraints to the solver
        equationRows = []
        for i in range(0,len(Aeq2)):
            eqlDic= Aeq2[i]
            variables = []
            coefficient = []
            for key in eqlDic: 
                variables.append('x_'+str(key))
                coefficient.append(eqlDic[key])
            row=[]
            row.append(variables)
            row.append(coefficient)
            equationRows.append(row)   
            constCounter= constCounter+1
            constName= 'new_e'+str(constCounter)
            tempConstNames2.append(constName)
        indices = cplex.linear_constraints.add(lin_expr = equationRows, senses = 'E'*len(Aeq2), rhs =  Beq2, names = tempConstNames2)
        #testing purpose
        #print (indices)
        
        cplex.solve()
        
        rsltObj = float("inf")
        rsltSolString = cplex.solution.get_status_string()
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
        return (rsltObj,rsltSolString)
       
        
        
    def setParas(self, attributeMatrix, origi_A , origi_B, origi_Aeq, origi_Beq):
        self.attributeMatrix_in = attributeMatrix
        #need to clone
        self.origi_A = origi_A
        self.origi_B = origi_B
        self.origi_Aeq = origi_Aeq
        self.origi_Beq = origi_Beq
  
    @classmethod  
    def appendToSparseMapList(cls, mapList, matrix):
        for i in range(0, len(matrix)):
            equationArray = matrix[i]
            equationDict = {}
            for j in range(0,len(equationArray)):
                if equationArray[j]!=0:  
                    equationDict[j] = float(equationArray[j])
            mapList.append(equationDict)
        return 
       
    @classmethod  
    def appendToSparseList(cls, mapList, matArray):
        for i in range(0, len(matArray)):
            equation = matArray[i]
            mapList.append(equation[0])
        return        
    
    @classmethod    
    def initializeCplex(cls, Nv, No, a_in , b_in , aeq_in, beq_in, lbs, ubs):
        solver = cplex.Cplex()
        solver.set_results_stream(None)
        solver.set_warning_stream(None)
        solver.set_error_stream(None)
        if Nv < 2000:
            solver.parameters.timelimit.set(BaseSol.TimeOut)
            solver.parameters.dettimelimit.set(BaseSol.DeterTimeOut)
        else: 
            solver.parameters.workmem.set(SolRep.WorkMem)
            solver.parameters.dettimelimit.set(SolRep.DeterTimeOut)
        var_names = ['x_'+str(i) for i in range(0,Nv+No+1) ]
        SolRep.XvarNames = var_names
        var_types = 'C'* (Nv+No+1)
        solver.variables.add(lb = lbs, ub = ubs, types = var_types, names = var_names)    
        
        #add the inequation constraints to the solver
        inEquationRows = []
        for i in range(0,len(a_in)):
            ineqlDic= a_in[i]
            variables = []
            coefficient = []
            for key in ineqlDic: 
                variables.append('x_'+str(key))
                coefficient.append(ineqlDic[key])
            row=[]
            row.append(variables)
            row.append(coefficient)
            inEquationRows.append(row)       
        indices = solver.linear_constraints.add(lin_expr = inEquationRows, senses = 'L'*len(a_in), rhs =  b_in)
        #testing purpose
        #print (indices)
      
        #add the equation constraints to the solver
        equationRows = []
        for i in range(0,len(aeq_in)):
            eqlDic= aeq_in[i]
            variables = []
            coefficient = []
            for key in eqlDic: 
                variables.append('x_'+str(key))
                coefficient.append(eqlDic[key])
            row=[]
            row.append(variables)
            row.append(coefficient)
            equationRows.append(row)       
        indices = solver.linear_constraints.add(lin_expr = equationRows, senses = 'E'*len(aeq_in), rhs =  beq_in)
        #testing purpose
        #print (indices)
        #verify the number of total constraints
        assert indices[-1]+1 == len(b_in)+ len(beq_in) 
        return solver

class ConstantMatrix():
    'define the calculation and implementation of Constant Matrix'
    V = None
    
    @classmethod
    def initialize(cls, y_up, No):
        ConstantMatrix.V = np.zeros((No-1, No))
        for i in range(0,No-1):
            v_i = y_up[len(y_up)-1] - y_up[i]
            norm_2 = np.linalg.norm(v_i,ord=2,keepdims=True)
            if norm_2 != 0 :
                v_i = v_i  / norm_2
            ConstantMatrix.V[i] = v_i
    