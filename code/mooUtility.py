# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 00:48:48 2018

@author: allen
"""

import math

class MOOUtility():
    @classmethod
    def simple_cull(cls, inputPoints, dominates): #类方法
        paretoPoints = set()
        candidateRowNr = 0
        dominatedPoints = set()
        while True:
            candidateRow = inputPoints[candidateRowNr]
            inputPoints.remove(candidateRow)
            rowNr = 0
            nonDominated = True
            while len(inputPoints) != 0 and rowNr < len(inputPoints):
                row = inputPoints[rowNr]
                if dominates(candidateRow, row):
                    # If it is worse on all features remove the row from the array
                    inputPoints.remove(row)
                    dominatedPoints.add(tuple(row))
                elif dominates(row, candidateRow):
                    nonDominated = False
                    dominatedPoints.add(tuple(candidateRow))
                    rowNr += 1
                else:
                    rowNr += 1
    
            if nonDominated:
                # add the non-dominated point to the Pareto frontier
                paretoPoints.add(tuple(candidateRow))
    
            if len(inputPoints) == 0:
                break
        return paretoPoints, dominatedPoints
    
    def dominates(row, candidateRow):
        #return sum([row[x] >= candidateRow[x] for x in range(len(row))]) == len(row)   
        #bug fixed here, we are doing for minimal 
        return sum([row[x] <= candidateRow[x] for x in range(len(row))]) == len(row)  
        
    
    @classmethod
    def round(cls, value):
        return math.floor(float(value)+0.5)
    
    @classmethod
    def arrayEqual(cls,dict1,array1):
        for i in range(0,len(array1)):
            if(i not in dict1) and (array1[i]==0):
                continue
            elif dict1[i] == array1[i]:
                continue
            else:
                return False
        return True
                