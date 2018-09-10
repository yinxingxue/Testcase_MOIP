# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 11:48:10 2018

@author: Yinxing Xue
"""
class TestcaseDataReader():  
    'the class to read the raw data of the test case data, including the test case coverage, fault information, etc.'
    
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
    
    def load(self):
        'first read all the test case names'
        self.loadRtimeFile()
        return 
    
    def loadRtimeFile(self):
        line = self.rtimeFile.readline()             # 调用文件的 readline()方法
        while line:
            #for testing purpose
            print(line, end = '')
            parts = line.split(':')
            testCaseName= parts[0].strip()
            time= float(parts[1].strip())
            self.testCaseNames.append(testCaseName)
            self.timeofTestcase[testCaseName] = time
            line = self.rtimeFile.readline()
        self.rtimeFile.close()
        return 
    
    
    
    def save(self,outputPath):
        
        return 
    
    
if __name__ == "__main__":
    reader = TestcaseDataReader('C:/Users/allen/Documents/GitHub/Nemo/example')
    reader.load()
else:
    print("testcaseDataReader.py is being imported into another module")