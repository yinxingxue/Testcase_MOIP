# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 11:48:10 2018

@author: Yinxing Xue
"""
from collections import Counter
import math

class TriCriteriaProbReaderBigM():  
    'the class to read the raw data of the test case data, including the test case coverage, fault information, etc.'
    AllowPerc = 0.05
    
    def __init__(self,path):  
        self.covFile = open(path+"/cov.info", "r")
        self.faultFile = open(path+"/fault.info", "r")
        self.rtimeFile = open(path+"/rtime.info", "r")
        
        self.objectNames = {}
        self.featureNames = {}
        
        self.testCaseNames=[]
        self.faultNames=[]
        self.timeofTestcase={}
   
        """
        each list is to represent one objectives, and use the objectivesList to store all the objectives maps
        """
        self.objectivesList = [] 
    
        """
        each sparse map is to represent one constraint in inequation, and use the list to store all the inequation constraints
        """
        self.sparseInequationsMapList = [] 
    
        """
        each sparse map is to represent one constraint in equation, and use the list to store all the equation constraints
        """
        self.sparseEquationsMapList = []
        
        """
        This map stores the relation between a fault and the set of test cases that cover this fault. The key is the fault, and the value is the test cases
        """
        self.faultToTestcaseMap={}
        
        """
        This map stores the relation between a stmt and the set of test cases that cover this stmt. The key is the fault, and the value is the test cases
        """
        self.stmtsofTestcaseMap={}
             
        """
        Each sparse map is the if-and-else condition for the fault and the test cases 
        """
        self.bigMConditionalEquationsMapList = []
        return 
    
    def displayFeatureNum(self):
        print ("Total feature size: ",len(self.featureNames))
        
    def displayTestCaseNum(self):
        print ("Total testcase size: ",len(self.testCaseNames))
        
    def displayStmtNum(self):
        print ("Total statement size: ",len(self.stmtsofTestcaseMap))
    
    def displayFaultNum(self):
        print ("Total fault size: ",len(self.faultToTestcaseMap))
    
    def displayConstraintInequationNum(self):
        print ("Total constrained inequations size: ",len(self.sparseInequationsMapList))
        
    def displayConstraintEquationNum(self):
        print ("Total constrained equations size: ",len(self.sparseEquationsMapList))
    
    def load(self):
        'first read all the test case names'
        self.loadRtimeFile()
        self.loadCovFile()
        self.loadFaultFile()
        
        self.buildFeatures()
        
        print (self.timeofTestcase)
        print (self.stmtsofTestcaseMap)
        print (self.faultToTestcaseMap)
        return 
    
    def buildFeatures(self):
        'the first part is test case, the second part is stmt, the third part is fault'
        faultIDs = map(lambda x: int(x[1:]), self.faultToTestcaseMap.keys())
        sortedFaultIDs = sorted(faultIDs)
        stmtIDs = map(lambda x: int(x[1:]), self.stmtsofTestcaseMap.keys())
        sortStmtIDs = sorted(stmtIDs)
        totalFeatures= len(self.testCaseNames) + len(sortStmtIDs)+ len(sortedFaultIDs)
        for i in range(0,totalFeatures):
            if i < len(self.testCaseNames) :
                key = self.testCaseNames[i]
                self.featureNames[key] = i
            elif i >= len(self.testCaseNames) and i<  len(self.testCaseNames) + len(sortStmtIDs):
                key = 's'+str(sortStmtIDs[i-len(self.testCaseNames)])
                self.featureNames[key] = i
            else:
                key = 'f'+str(sortedFaultIDs[i-len(self.testCaseNames)-len(sortStmtIDs)])
                self.featureNames[key] = i 
        return
    
    def loadFaultFile(self):
        line = self.faultFile.readline()             # 调用文件的 readline()方法
        while line:
            #for testing purpose
            #print(line, end = '')
            parts = line.split(':')
            #example: t2:2 3
            testCaseName= parts[0].strip()
            faults = parts[1].split(' ')
            'bug fixed here, for case: ["t329", "\n"]'
            if( parts[1].strip() == '\n' or  parts[1].strip() == '' ):
                line = self.faultFile.readline()
                continue
            for fault in faults:
                faultName= 'f'+fault.strip()
                if faultName in self.faultToTestcaseMap:
                    testcaseList= self.faultToTestcaseMap[faultName]
                    testcaseList.append(testCaseName)
                else: 
                    testcaseList = []
                    testcaseList.append(testCaseName)
                    self.faultToTestcaseMap[faultName]=testcaseList
            line = self.faultFile.readline()
        self.faultFile.close()
        'check there exist no duplication in the map'
        for faultName in self.faultToTestcaseMap:
            testcaseList= self.faultToTestcaseMap[faultName]
            cou=Counter(testcaseList)
            first=cou.most_common(1)
            if first[0][1]>1:
                print ('input have duplicates!!!')
                exit(-1) 
        return 
    
    def loadCovFile(self):
        line = self.covFile.readline()             # 调用文件的 readline()方法
        while line:
            #for testing purpose
            #print(line, end = '')
            parts = line.split(':')
            #example: t2:2 3
            testCaseName= parts[0].strip()
            stmts = parts[1].split(' ')
            if( parts[1].strip() == '\n' or  parts[1].strip() == '' ):
                line = self.covFile.readline()
                continue
            
            for stmt in stmts:
                stmtName= 's'+stmt.strip()
                if stmtName in self.stmtsofTestcaseMap:
                    testcaseList= self.stmtsofTestcaseMap[stmtName]
                    testcaseList.append(testCaseName)
                else: 
                    testcaseList = []
                    testcaseList.append(testCaseName)
                    self.stmtsofTestcaseMap[stmtName]=testcaseList
            line = self.covFile.readline()
        self.covFile.close()
        'check there exist no duplication in the map'
        for stmtName in self.stmtsofTestcaseMap:
            testcaseList= self.stmtsofTestcaseMap[stmtName]
            cou=Counter(testcaseList)
            first=cou.most_common(1)
            if first[0][1]>1:
                print ('input have duplicates!!!')
                exit(-1) 
        return 
    
    def loadRtimeFile(self):
        line = self.rtimeFile.readline()             # 调用文件的 readline()方法
        while line:
            #for testing purpose
            #print(line, end = '')
            parts = line.split(':')
            testCaseName= parts[0].strip()
            time= float(parts[1].strip())
            self.testCaseNames.append(testCaseName)
            self.timeofTestcase[testCaseName] = time
            line = self.rtimeFile.readline()
        self.rtimeFile.close()
        return 
    
    def save(self,outputPath):   
        output = open(outputPath,'w')
        'write objectives content'
        output.write("objectives ==\n")
        output.write("totalStmt; totalFault\n")
        totalStmt= []
        totalFeatures= len(self.featureNames)
        #example: [1.0;1.0;1.0;0.0;0.0;0.0;0.0]
        #         [0.0;0.0;0.0;-1.0;-1.0;-1.0;-1.0]   
        for i in range(0,totalFeatures):
            if i < len(self.testCaseNames) :
                 totalStmt.append(0.0)
            elif i >= len(self.testCaseNames) and i<  len(self.testCaseNames) + len(self.stmtsofTestcaseMap): 
                 totalStmt.append(-1.0)
            else:
                 totalStmt.append(0.0)
        obj1String = str(totalStmt).replace(',', ';')
        output.write(obj1String+'\n')
        totalFault =[]
        for j in range(0,totalFeatures):
            if j < len(self.testCaseNames) :
                 totalFault.append(0.0)
            elif j >= len(self.testCaseNames) and j<  len(self.testCaseNames) + len(self.stmtsofTestcaseMap): 
                 totalFault.append(0.0)
            else:
                 totalFault.append(-1.0)
        obj2String = str(totalFault).replace(',', ';')
        output.write(obj2String+'\n')
        output.write('\n')
        
        'write variable content'
        #example:{t1=0, t2=1, t3=2, g1=3, g2=4, g3=5, g4=6}
        sortedFeatureItems= sorted(self.featureNames.items(), key = lambda k: k[1])
        variableContStr ='{'
        for item in sortedFeatureItems:
            if item[1]!=totalFeatures-1:
                variableContStr += item[0]+'='+str(item[1])+', '
            else:
                variableContStr += item[0]+'='+str(item[1])
        variableContStr +='}'
        output.write('variables ==\n')
        output.write(variableContStr+'\n')
        output.write('\n')
        
        'write inequation content for all stmts'
        #example: 
        self.sparseInequationsMapList=[]
        for stmtName in self.stmtsofTestcaseMap:
            #example: 
            conditionalEquation =''
            conditionMap={}
            ifCodeMap={}
            elseCodeMap={}
            testcaseList= self.stmtsofTestcaseMap[stmtName]
            for testcase in testcaseList:
                pos = self.featureNames[testcase]
                if pos >=0 :
                    conditionMap[pos] = 1.0
                else:
                    print ('input have duplicates!!!')
                    exit(-1) 
            conditionMap[totalFeatures]= 1.0
            conditionMapStr= str(conditionMap).replace(': ', '=')
            lastPos = conditionMapStr.rfind('=')
            conditionMapStr= conditionMapStr[:lastPos] + '>' + conditionMapStr[lastPos:]
            ifCodeMap[self.featureNames[stmtName]]=1.0
            ifCodeMap[totalFeatures]=1.0
            ifCodeMapStr= str(ifCodeMap).replace(': ', '=')
            elseCodeMap[self.featureNames[stmtName]]=1.0
            elseCodeMap[totalFeatures]=0.0
            elseCodeMapStr= str(elseCodeMap).replace(': ', '=')
            conditionalEquation='(if '+conditionMapStr+': '+ ifCodeMapStr+'; else : '+elseCodeMapStr+')'
            self.sparseInequationsMapList.append(conditionalEquation)
        
        #sparseInequationMapStr= str(self.sparseInequationsMapList).replace(': ', '=')
        #output.write(sparseInequationMapStr+'\n')
        #output.write('\n')
        
        'write the fault detection content for all faults'
        for fault in self.faultToTestcaseMap:
            #example: (if {1=1.0,2=1.0,7>=1.0}: {3=1.0, 7=1.0}; else : {3=1.0, 7=0.0})
            conditionalEquation =''
            conditionMap={}
            ifCodeMap={}
            elseCodeMap={}
            testcaseList= self.faultToTestcaseMap[fault]
            for testcase in testcaseList:
                pos = self.featureNames[testcase]
                if pos >=0 :
                    conditionMap[pos] = 1.0
                else:
                    print ('input have duplicates!!!')
                    exit(-1) 
            conditionMap[totalFeatures]= 1.0
            conditionMapStr= str(conditionMap).replace(': ', '=')
            lastPos = conditionMapStr.rfind('=')
            conditionMapStr= conditionMapStr[:lastPos] + '>' + conditionMapStr[lastPos:]
            ifCodeMap[self.featureNames[fault]]=1.0
            ifCodeMap[totalFeatures]=1.0
            ifCodeMapStr= str(ifCodeMap).replace(': ', '=')
            elseCodeMap[self.featureNames[fault]]=1.0
            elseCodeMap[totalFeatures]=0.0
            elseCodeMapStr= str(elseCodeMap).replace(': ', '=')
            conditionalEquation='(if '+conditionMapStr+': '+ ifCodeMapStr+'; else : '+elseCodeMapStr+')'
            self.sparseInequationsMapList.append(conditionalEquation)
        conditionalEquationStrs = '['+';'.join(self.sparseInequationsMapList)+']'
        output.write('Conditional Equation ==\n')
        output.write(conditionalEquationStrs+'\n')
        output.write('\n')
        
        self.sparseEquationsMapList=[]
        'the constraint of the fixed percent of total cost'
        sparseEquation= {}
        for i in range(0,len(self.testCaseNames)):
            if i < len(self.testCaseNames) :
                  sparseEquation[self.featureNames[self.testCaseNames[i]]] = (self.timeofTestcase[self.testCaseNames[i]])
        totalCost = sum(self.timeofTestcase.values())
        allowCost = int(math.floor(totalCost * TriCriteriaProbReaderBigM.AllowPerc+0.5))
        sparseEquation[totalFeatures] = allowCost
        self.sparseEquationsMapList.append(sparseEquation)
        output.write('Equations ==\n')
        sparseEquationMapStr= str(self.sparseEquationsMapList).replace(': ', '=')
        output.write(sparseEquationMapStr+'\n')
        output.close()
        return 
    
    
if __name__ == "__main__":
    reader = TriCriteriaProbReaderBigM('../../Nemo/subject_programs/make_v5')
    #reader = TriCriteriaProbReaderBigM('../../Nemo/example')
    reader.load()
    reader.save('../test/tri_input_make_bigM.txt')
    reader.displayFeatureNum()
    reader.displayTestCaseNum()
    reader.displayStmtNum()
    reader.displayFaultNum()
    reader.displayConstraintInequationNum()
    reader.displayConstraintEquationNum()
else:
    print("triCriteriaProbReaderBigM.py is being imported into another module")