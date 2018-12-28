# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 21:02:40 2018

@author: allen
"""
import pygmo as pg
from probReader import ProbReader
import numpy as np
import math
import os
import sys
from subprocess import Popen, PIPE

class NSGA2_triCriteria:
    
    AllowPerc = 0.05
    
#    def __init__(self, probReader):
#        self.reader = probReader
#        self.reader.displayFeatureNum()
#        self.reader.displayTestCaseNum()
#        self.reader.displayStmtNum()
#        self.reader.displayFaultNum()
        
    # Define objectives
    def fitness(self, x):
        f_stmtNum = 10000
        f_faultNum = 10000
        f_testNum = 10000
        
        coveredStmtSet = set() 
        coveredFaultSet = set() 
       
        for i in range(0,ProbReader.testSuiteSize):
            if x[i] == 0.0 or x[i] < 0.00000001:
                continue
            testCaseName = ProbReader.testCaseNameList[i]
            coveredStmtSet.update(ProbReader.testToStmtcaseMap[testCaseName])
            'bug fixed here, need to add the if in check, because it is not necessary that each test will find some fault'
            coveredFaultSet.update(ProbReader.testToFaultcaseMap[testCaseName])
        coveredStmtSetPerc =   len(coveredStmtSet) #/ ProbReader.stmtSetSize
        coveredFaultSetPerc =  len(coveredFaultSet) #/ ProbReader.fauktSetSize
        f_stmtNum = ProbReader.stmtSetSize -1 * coveredStmtSetPerc 
        f_faultNum =ProbReader.fauktSetSize -1 * coveredFaultSetPerc
        
        allowNum = int(math.floor(NSGA2_triCriteria.AllowPerc* ProbReader.testSuiteSize+0.5))
        f_testNum = abs(sum(x) - allowNum) 
        #ci1 = x[0]-1
        return [f_stmtNum, f_faultNum,f_testNum]#, ci1]

    # Return number of objectives
    def get_nobj(self):
        return 3

    # Return bounds of decision variables
    def get_bounds(self):
        return ([0]*ProbReader.testSuiteSize, [1]*ProbReader.testSuiteSize )

    # Return function name
    def get_name(self):
        return "NSGA II for the tri-criteria problem of test-suite minimization!"

    #def get_nic(self):
    #    return 1
    
    # return the number of integer 
    def get_nix(self):
        return ProbReader.testSuiteSize 


if __name__ == "__main__":
   
    if len(sys.argv)!=3: 
        os._exit(0) 
    para = sys.argv[1]
    NSGA2_triCriteria.AllowPerc=float(sys.argv[2])

    projectName = para
    inputPath = '../../../Nemo/subject_programs/{name}_v5'.format(name=projectName)
    reader = ProbReader(inputPath)
    #reader = ProbReader('../../../Nemo/example')
    reader.load()
      
    outputPath='../../result/moea/nsga2/'+ str(NSGA2_triCriteria.AllowPerc)+'/'+para+'/'
    if not os.path.isdir(outputPath):
        os.makedirs(outputPath)
    
    for i in range(0,2):      
        # create UDP
        prob = pg.problem(NSGA2_triCriteria())
        print (prob)
        # create population
        pop = pg.population(prob, size=104)
        # select algorithm
        algo = pg.algorithm(pg.nsga2(gen=2000))
        # run optimization
        pop = algo.evolve(pop)
        # extract results
        fits, vectors = pop.get_f(), pop.get_x()
        # extract and print non-dominated fronts
        ndf, dl, dc, ndr = pg.fast_non_dominated_sorting(fits)
        np.around(fits,6)
        frontStr=''
        for fit in fits:
            for data in fit:
                frontStr+= str(int(data))+'\t' 
            frontStr+='\n' 
        print (frontStr)
        print (type(fits))
        print (ndf) 
        
        outputFilePath= outputPath+'FUN_'+str(i)+'.tsv'
        file_object = open(outputFilePath, "w") 
        try: 
            file_object.writelines(frontStr) 
        finally: 
            file_object.close( )
        
        refPath='../../result/moea/refPnts/'+ str(NSGA2_triCriteria.AllowPerc)+'/'+para+'/'
        refFilePath = refPath+'ref.pf'
    
        cmds='java -jar CMDIndicatorRunner.jar ALL '+ refFilePath + ' '+ outputFilePath+' TRUE'
        p = Popen(cmds, shell=True, stdout=PIPE, stderr=PIPE)  
        p.wait()  
        if p.returncode != 0: 
            print ("Error.")
            os._exit(0) 
else:
    print("nsga2_triCriteria.py is being imported into another module")
    
    
