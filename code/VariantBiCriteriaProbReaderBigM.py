# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 11:48:10 2018

@author: Yinxing Xue
"""
import math
from collections import Counter

class VariantBiCriteriaProbReaderBigM():  
    'the class to read the raw data of the test case data, including the test case coverage, fault information, etc.'
    
    def __init__(self,path):  
        self.covFile = open(path+"/cov.info", "r")
        self.faultFile = open(path+"/fault.info", "r")
        self.rtimeFile = open(path+"/rtime.info", "r")
        
        self.objectNames = {'totalNumber','totalFault'}
        self.featureNames = {}
        
        self.testCaseNames=[]
        self.faultNames=[]
        self.timeofTestcase={}
        
        self.topStmts = {}
        
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
        faultIDs = map(lambda x: int(x[1:]), self.faultToTestcaseMap.keys())
        sortedFaultIDs = sorted(faultIDs)    
        totalFeatures= len(self.testCaseNames) + len(sortedFaultIDs)
        for i in range(0,totalFeatures):
            if i < len(self.testCaseNames) :
                key = self.testCaseNames[i]
                self.featureNames[key] = i
            else:
                key = 'f'+str(sortedFaultIDs[i-len(self.testCaseNames)])
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
        objNamesStr = ';'.join(self.objectNames)
        output.write(objNamesStr+'\n')
        totalCost= []
        totalFeatures= len(self.featureNames)
        #example: [1.0;1.0;1.0;0.0;0.0;0.0;0.0]
        #         [0.0;0.0;0.0;-1.0;-1.0;-1.0;-1.0]   
        for i in range(0,totalFeatures):
            if i < len(self.testCaseNames) :
                 totalCost.append(self.timeofTestcase[self.testCaseNames[i]])
            else:
                 totalCost.append(0.0)
        obj1String = str(totalCost).replace(',', ';')
        output.write(obj1String+'\n')
        totalFault =[]
        for j in range(0,totalFeatures):
            if j < len(self.testCaseNames) :
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
        #example: [{0=-1.0, 2=-1.0, 7=-1.0},{1=-1.0, 7=-1.0},{1=-1.0, 2=-1.0, 7=-1.0}]
        self.sparseInequationsMapList=[]
        stmtFrequency = {}
        'find the most top 10% of statements executed most frequently'
        for stmtName in self.stmtsofTestcaseMap:
             size= len(self.stmtsofTestcaseMap[stmtName])
             stmtFrequency[stmtName] = size
        self.topStmts = VariantBiCriteriaProbReaderBigM.calculateTopStmt(stmtFrequency,0.10)
        
        for stmtName in self.stmtsofTestcaseMap:
            inequationMap = {}
            testcaseList= self.stmtsofTestcaseMap[stmtName]
            for testcase in testcaseList:
                pos = self.featureNames[testcase]
                if pos >=0 :
                    inequationMap[pos] = -1.0
                else:
                    print ('input have duplicates!!!')
                    exit(-1) 
            'check whether it is the most top 10% of statements executed most frequently, if yes, set to ceiling() for 10% of the number of the execution times of the entire test suite'
            if(stmtName in  self.topStmts):
                inequationMap[totalFeatures]= -1.0 * (math.floor(float(0.1*self.topStmts[stmtName])))
            else :
                inequationMap[totalFeatures]= -1.0
            self.sparseInequationsMapList.append(inequationMap)
        output.write('Inequations ==\n')
        sparseInequationMapStr= str(self.sparseInequationsMapList).replace(': ', '=')
        output.write(sparseInequationMapStr+'\n')
        output.write('\n')
        
        'write the fault detection content for all faults'
        self.sparseEquationsMapList=[]
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
            self.sparseEquationsMapList.append(conditionalEquation)
        conditionalEquationStrs = '['+';'.join(self.sparseEquationsMapList)+']'
        output.write('Conditional Equation ==\n')
        output.write(conditionalEquationStrs+'\n')
        
        output.close()
        return 
    
    @classmethod
    def calculateTopStmt(cls, allStmtFrequency, percent):
        topStmt = {}
        sorted_Stmt =   sorted(allStmtFrequency, key=lambda x: allStmtFrequency[x], reverse= True)
        totalStmtsSize = len(allStmtFrequency)
        allowedStmtSize = math.ceil(float(percent * totalStmtsSize))
        counter = 0 
        miniFreq = -1
        for stmt in sorted_Stmt:
             counter = counter+1 
             if(allStmtFrequency[stmt] < miniFreq):
                 break
             if(allowedStmtSize == counter):
                 miniFreq= allStmtFrequency[stmt] 
             topStmt[stmt] = allStmtFrequency[stmt]
        #print ('top 10\% stmts and their freq: ', len(topStmt), topStmt)  
        return topStmt
    
if __name__ == "__main__":
    reader = VariantBiCriteriaProbReaderBigM('../../Nemo/subject_programs/grep_v5')
    reader.load()
    reader.save('../test/variant_bi_input_grep_bigM.txt')
    reader.displayFeatureNum()
    reader.displayTestCaseNum()
    reader.displayStmtNum()
    reader.displayFaultNum()
    reader.displayConstraintInequationNum()
    reader.displayConstraintEquationNum()
else:
    print("variantBiCriteriaProbReaderBigM.py is being imported into another module")