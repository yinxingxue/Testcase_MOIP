import pygmo as pg
from probReader import ProbReader
import numpy as np
import shutil,os
import sys
import time
from subprocess import Popen, PIPE
from moeaD_triCriteria import MOEAD_triCriteria

if __name__ == "__main__":
   
    if len(sys.argv)!=3: 
        os._exit(0) 
    para = sys.argv[1]
    MOEAD_triCriteria.AllowPerc=float(sys.argv[2])

    projectName = para
    inputPath = '../../../Nemo/subject_programs/{name}_v5'.format(name=projectName)
    reader = ProbReader(inputPath)
    #reader = ProbReader('../../../Nemo/example')
    reader.load()
      
    outputPath='../../result/moea/moeaD/'+ str(MOEAD_triCriteria.AllowPerc)+'/'+para+'/'
    if not os.path.isdir(outputPath):
        os.makedirs(outputPath)
    
    for i in range(0,30):
        time_start=time.time()
        # create UDP
        prob = pg.problem(MOEAD_triCriteria())
        print (prob)
        # create population
        pop = pg.population(prob, size=105)
        # select algorithm
        algo = pg.algorithm(pg.moead(gen=1981))
        # run optimization
        pop = algo.evolve(pop)
        # extract results
        fits, vectors = pop.get_f(), pop.get_x()
        # extract and print non-dominated fronts
        ndf, dl, dc, ndr = pg.fast_non_dominated_sorting(fits)
        time_end=time.time()
        exec_time= time_end- time_start
        np.around(fits,6)
        frontStr=''
        
        isOptimal = False 
        for fit in fits:
            if sum(fit) == 0:
                isOptimal = True
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
        
        refPath='../../result/moea/refPnts/'+ str(MOEAD_triCriteria.AllowPerc)+'/'+para+'/'
        refFilePath = refPath+'ref.pf'     
            
        #if it does not contain the optimal solution 
        if (isOptimal == False):
            cmds='java -jar CMDIndicatorRunner.jar ALL '+ refFilePath + ' '+ outputFilePath+' TRUE'
            p = Popen(cmds, shell=True, stdout=PIPE, stderr=PIPE)  
            p.wait()  
            if p.returncode != 0: 
                print ("Error.")
                os._exit(0) 
            outputMetricFile = 'FUN_'+str(i)+'_metric.txt'
            if os.path.exists(outputPath+outputMetricFile):
                os.remove(outputPath+outputMetricFile)
            shutil.move(outputMetricFile,outputPath)
            with open(outputPath+outputMetricFile,'a') as f:
                f.write('TIME='+str(exec_time)+'\n')
                f.close( )
        #else
        else:
            tmpOutputMetricFilePath = '../../result/moea/refPnts/'+ 'FUN_metric.txt'
            outputMetricFile = 'FUN_'+str(i)+'_metric.txt'
            if os.path.exists(outputPath+outputMetricFile):
                os.remove(outputPath+outputMetricFile)
            shutil.copy(tmpOutputMetricFilePath,outputPath+outputMetricFile)
            with open(outputPath+outputMetricFile,'a') as f:
                f.write('TIME='+str(exec_time)+'\n')
                f.close( )
else:
    print("RQ3_moeaD.py is being imported into another module")
    
    
