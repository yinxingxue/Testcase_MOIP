# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 21:02:40 2018

@author: allen
"""
class Schaffer:
    # Define objectives
    def fitness(self, x):
        f1 = x[0]**2
        f2 = (x[0]-2)**2
        #ci1 = x[0]-1
        return [f1, f2]#, ci1]

    # Return number of objectives
    def get_nobj(self):
        return 2

    # Return bounds of decision variables
    def get_bounds(self):
        return ([0]*1, [2]*1)

    # Return function name
    def get_name(self):
        return "Schaffer function N.1"

    #def get_nic(self):
    #    return 1
    # return the number of integer 
    def get_nix(self):
        return 1

import pygmo as pg
# create UDP
prob = pg.problem(Schaffer())
print (prob)
# create population
pop = pg.population(prob, size=20)
# select algorithm
algo = pg.algorithm(pg.nsga2(gen=40))
# run optimization
pop = algo.evolve(pop)
# extract results
fits, vectors = pop.get_f(), pop.get_x()
# extract and print non-dominated fronts
ndf, dl, dc, ndr = pg.fast_non_dominated_sorting(fits)
print(ndf) 