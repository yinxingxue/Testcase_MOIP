# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 11:30:04 2018

@author: Yinxing Xue
"""
import re

class MOIPProblem:
    'define the problem of a MOBIP'
    
    def __init__(self, objCount, varCount, attrCount):
        
        self.objectiveCount = 0 
        self.featureCount = 0 
        self.attributeCount = 0
    
        self.objectNames = {}
        self.featureNames = {}
        self.attributeNames = {}
        """
        each sparse map is to represent one objectives, and use the list to store all the objectives maps
        """
        self.objectiveSparseMapList = [] 
    
        """
        each sparse map is to represent one constraint in inequation, and use the list to store all the inequation constraints
        """
        self.sparseInequationsMapList = [] 
    
        """
        each sparse map is to represent one constraint in equation, and use the list to store all the equation constraints
        """
        self.sparseEquationsMapList = []
    
        self.attributeMatrix = [[]]
        self.objectiveCount = objCount
        self.featureCount = varCount
        self.attributeCount = attrCount
    
    def displayObjectiveCount(self):
        print ("Total Objectives Num: %d" % self.objectiveCount)
    
    def displayFeatureCount(self):
        print ("Total Variables Num: %d" % self.featureCount) 
     
    def displayAttributeCount(self):
        print ("Total Attributes Num: %d" % self.attributeCount) 
        
    def displayObjectives(self):
        print ("Objectives : %s" % self.objectNames)
    
    def displayVariableNames(self):
        print ("Variables : %s" % self.featureNames)
    
    def displayObjectiveSparseMapList(self):
        print ("Objectives in sparse map: %s" % self.objectiveSparseMapList)
        
    def displaySparseInequationsMapList(self):
        print ("Inequality constraints in sparse map: %s" % self.sparseInequationsMapList)
        
    def displaySparseEquationsMapList(self):
        print ("Equality constraints in sparse map: %s" % self.sparseEquationsMapList)
        
    def displayAttributeMatrix(self):
        print ("Attribute objs in matrix: %s" % self.attributeMatrix)     
        
    def load(self,objectives, sparseInequations, sparseEquations, deriveObjective = False, attributeMatrix = None): 
        if isinstance(objectives, list) : 
            if isinstance(objectives[0], dict) : 
                #the input file objectives is sparse
                self.objectiveSparseMapList = objectives
        if isinstance(sparseInequations, list) : 
            if isinstance(sparseInequations[0], dict) : 
                #the input file sparseInequations is sparse
                self.sparseInequationsMapList = sparseInequations
        if isinstance(sparseEquations, list) : 
            if isinstance(sparseEquations[0], dict) : 
                #the input file sparseEquations is sparse
                self.sparseEquationsMapList = sparseEquations
        if deriveObjective == True:                 
            self.attributeMatrix= [[ 0 for i in range(self.attributeCount) ] for j in range(self.featureCount)]
        
    def exetractFromFile(self,path):
        mode = "";
        objCount=0;
        varCount=0;
        trim= lambda x: x.replace(' ','')
        with open(path) as f:
            line = f.readline()
            while line:
                if line.startswith("objectives =="):
                    mode = "obj"
                elif  line.startswith("variables =="):
                    mode = "var"
                elif  line.startswith("Inequations =="):
                    mode = "ineql"
                elif  line.startswith("Equations =="):
                    mode = "eql"
                elif  line.startswith("Conditional Equation =="):
                    mode = "bigM_ineql"
                elif line == "" or line == "\n":
                    mode = ""
                else:
                    if mode == "obj":
                        #read the objective names
                        strText= line.replace("\n", "")
                        results = strText.split(';')
                        self.objectNames = [trim(x) for x in results]
                        objCount = len(self.objectNames)
                        self.objectiveSparseMapList = []
                        for i in range(0,objCount):
                            line = f.readline()
                            valueString = line.replace("\n", "")
                            valueString = valueString.replace("[", "")
                            valueString = valueString.replace("]", "")
                            values = valueString.split(';')
                            trimvalues = [trim(x) for x in values]
                            newDict={}
                            for j in range(0,len(trimvalues)): 
                                newDict[j] = float(trimvalues[j]) 
                            self.objectiveSparseMapList.append(newDict)
                    elif mode == "var":
                        #read variable or feature names
                        self.featureNames={}
                        feaString = line.replace("\n", "")
                        feaString = feaString.replace("{", "")
                        feaString = feaString.replace("}", "")
                        features = feaString.split(',')
                        trimFeatures = [trim(x) for x in features]
                        for feature in trimFeatures:
                            varKey = feature.split('=')
                            key = int(varKey[1])
                            self.featureNames[key] = varKey[0]
                        varCount=len(trimFeatures)
                    elif mode == "ineql":
                        #read Inequations constraints in sparse maps
                        self.sparseInequationsMapList=[]
                        reGroupTestStr = line 
                        ineqls = re.findall("{(.+?)}", reGroupTestStr)
                        for ineql in ineqls: 
                            pairs = ineql.split(',')
                            trimPairs = [trim(x) for x in pairs]
                            ineqlDict={}
                            for trimPair in trimPairs:
                                varKey = trimPair.split('=')
                                key = int(varKey[0])
                                ineqlDict[key] = float(varKey[1])
                            self.sparseInequationsMapList.append(ineqlDict)
                    elif mode == "eql":
                        #read Equations constraints in sparse maps
                        self.sparseEquationsMapList=[]
                        reGroupTestStr = line 
                        eqls = re.findall("{(.+?)}", reGroupTestStr)
                        for eql in eqls: 
                            pairs = eql.split(',')
                            trimPairs = [trim(x) for x in pairs]
                            eqlDict={}
                            for trimPair in trimPairs:
                                varKey = trimPair.split('=')
                                key = int(varKey[0])
                                eqlDict[key] = float(varKey[1])
                            self.sparseEquationsMapList.append(eqlDict)
                    elif mode == "bigM_ineql":
                        #read Inequations constraints for big M in sparse maps
                        reGroupTestStr = line 
                        bigM_ineqls = re.findall("\((.+?)\)", reGroupTestStr)
                        for ineql in bigM_ineqls: 
                            branches = ineql.split(';')
                            if_branch = branches[0]
                            else_branch = branches[1]
                            print (if_branch,else_branch)
                line = f.readline()
                
        self.attributeMatrix =self.__private_convertDenseLise__(self.objectiveSparseMapList)
        if  objCount != self.objectiveCount or varCount!= self.featureCount:
            raise Exception('input not consistent', 'eggs')
        self.reOrderObjsByRange()
        return      
    
    def reOrderObjsByRange(self):
        objRangeMap = {}
        for k in range(0,len(self.attributeMatrix)):
            kthObj= self.attributeMatrix[k]
            ub,lb = self.__private_calculteUBLB__(kthObj)
            objRange = ub - lb 
            objRangeMap[k] = objRange
        #find the objective with the largest range
        maxRange =  max(zip(objRangeMap.values(),objRangeMap.keys()))
        #debug purpose
        #print (maxRange)
        #the objective with the largest range is at index targetPos
        targetPos = maxRange[1]
        #now need to swap the first and targetPos-th element 
        temp = self.objectNames[0]
        self.objectNames[0] = self.objectNames[targetPos]
        self.objectNames[targetPos] = temp 
        temp = self.objectiveSparseMapList[0]
        self.objectiveSparseMapList[0] = self.objectiveSparseMapList[targetPos]
        self.objectiveSparseMapList[targetPos] = temp 
        temp = self.attributeMatrix[0]
        self.attributeMatrix[0] = self.attributeMatrix[targetPos]
        self.attributeMatrix[targetPos] = temp             
        
    def __private_calculteUBLB__(self,obj):
        ub = 0.0
        lb = 0.0
        for value in obj:
            if value > 0:
                ub = ub+ value
            else:
                lb = lb + value
        return ub, lb    
        
    def __private_convertDenseLise__(self,objectiveSparseMapList):
        listLength = len(objectiveSparseMapList)
        matrix =  [[] for i in range(listLength)]
        for i in range(listLength):
            dictionary = objectiveSparseMapList[i]
            matrix[i] = [0.0]* len(dictionary)
            for key in dictionary:
                matrix[i][key]=dictionary[key]
        return matrix
    
if __name__ == "__main__":
    prob = MOIPProblem(2,7,1)  
    prob.displayObjectiveCount()
    prob.displayFeatureCount()
    prob.exetractFromFile("../test/parameter_example_bigM.txt")
    prob.displayObjectives()
    prob.displayVariableNames()
    prob.displayObjectiveSparseMapList()
    prob.displaySparseInequationsMapList()
    prob.displaySparseEquationsMapList()
    prob.displayAttributeMatrix()
else:
    print("moipProb.py is being imported into another module")