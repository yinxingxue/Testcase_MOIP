# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 22:41:12 2018

@author: allen
"""

from collections import Counter

class ProbReader():  
    'the class to read the raw data of the test case data, including the test case coverage, fault information, etc.'
    
    testToFaultcaseMap={}
    testToStmtcaseMap={}
    testSuiteSize = 0
    fauktSetSize = 0
    stmtSetSize = 0
    testCaseNameList=[]
    
    def __init__(self,path):  
        self.covFile = open(path+"/cov.info", "r")
        self.faultFile = open(path+"/fault.info", "r")
        self.rtimeFile = open(path+"/rtime.info", "r")
        
        self.featureNames = {}
        
        self.testCaseNames=[]
        self.faultNames=[]
        self.timeofTestcase={}
    
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
        
        ProbReader.testToFaultcaseMap.clear()
        ProbReader.testToStmtcaseMap.clear()
        ProbReader.testCaseNameList.clear()      
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
        ProbReader.testSuiteSize = len(self.testCaseNames) 
        ProbReader.stmtSetSize = len(self.stmtsofTestcaseMap)
        ProbReader.fauktSetSize = len(self.faultToTestcaseMap)
        ProbReader.testCaseNameList.extend(self.testCaseNames)
        assert len(ProbReader.testToFaultcaseMap) ==  len(ProbReader.testCaseNameList)
        assert len(ProbReader.testToStmtcaseMap) ==  len(ProbReader.testCaseNameList)
        #print (self.timeofTestcase)
        #print (self.stmtsofTestcaseMap)
        #print (self.faultToTestcaseMap)
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
                faultList = []
                ProbReader.testToFaultcaseMap[testCaseName]=faultList      
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
            'adding again for the test to fault map'
            for fault in faults:
                faultName= 'f'+fault.strip()
                if testCaseName in ProbReader.testToFaultcaseMap:
                    faultList= ProbReader.testToFaultcaseMap[testCaseName]
                    faultList.append(faultName)
                else: 
                    faultList = []
                    faultList.append(faultName)
                    ProbReader.testToFaultcaseMap[testCaseName]=faultList         
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
                stmtList = []
                ProbReader.testToStmtcaseMap[testCaseName]=stmtList 
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
            'adding again for the test to stmt map'
            for stmt in stmts:
                stmtName= 's'+stmt.strip()
                if testCaseName in ProbReader.testToStmtcaseMap:
                    stmtList= ProbReader.testToStmtcaseMap[testCaseName]
                    stmtList.append(stmtName)
                else: 
                    stmtList = []
                    stmtList.append(stmtName)
                    ProbReader.testToStmtcaseMap[testCaseName]=stmtList 
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
    
if __name__ == "__main__":
    #reader = ProbReader('../../../Nemo/subject_programs/make_v5')
    reader = ProbReader('../../../Nemo/example')
    reader.load()
    reader.displayFeatureNum()
    reader.displayTestCaseNum()
    reader.displayStmtNum()
    reader.displayFaultNum()
    print (reader.testCaseNames)
    print (ProbReader.testToFaultcaseMap)
    print (ProbReader.testToStmtcaseMap)
else:
    print("probReader.py is being imported into another module")