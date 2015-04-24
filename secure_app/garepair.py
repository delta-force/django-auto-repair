#!/usr/bin/env python
import re
import sys
import random
import numpy
from deap import algorithms
from deap import base
from deap import creator
from deap import tools

import pprint
class GaRegexCreator():

    CXPB, MUTPB, ADDPB, DELPB, MU, NGEN = 0.7, 0.4, 0.4, 0.4, 100, 1000
    ESCAPED = ['\d', '\D', '\w', '\W', '\s', '\S']
    SPECIAL = ['\@', '\\', '\<' ,'/', '\>', '\.', '-']
#VALID_CHARS = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,*+?{}[]()") + escaped
    ALPHANUMERIC = map(chr,range(65,91)) + map(chr,range(97,123)) + map(str,range(0,10))
    VALID_CHARS = list("+*[]") + ESCAPED # + ALPHANUMERIC
    MAX_LENGTH = 20
    MIN_LENGTH = 5

    def __init__(self, data_evil, data_benign, verbose=False):
        '''
        A list of evil inputs
        A list of benign (acceptable) inputs
        '''
        self.data_evil = data_evil
        self.data_benign = data_benign
        self.verbose = verbose

        creator.create("FitnessMin", base.Fitness, weights=(-1.0,-1.0,-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        self.toolbox = base.Toolbox()
        # Attribute generator
        self.toolbox.register("attr_item", self.get_random_char)

        self.toolbox.register("word", self.gen_filter, self.MIN_LENGTH, self.MAX_LENGTH)
        # Structure initializers
        self.toolbox.register("individual", tools.initIterate, creator.Individual, self.toolbox.word)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        # Operator registering
        self.toolbox.register("evaluate",self.eval)
        self.toolbox.register("mate", self.mate)
        self.toolbox.register("mutate",self.mut)
        self.toolbox.register("addFilter", self.mutAddFilter)
        self.toolbox.register("delFilter", self.mutDelFilter)
        self.toolbox.register("select",tools.selBest )


    def get_random_char(self):
        r = random.randint(0, len(self.VALID_CHARS)-1)
        return self.VALID_CHARS[r]

    def gen_filter(self, min, max):
        l = random.randint(min, max)
        return [self.get_random_char() for i in range(l)]
    
    def get_evil_score(self, pattern, verbose=False):
        '''
        Get the score for the evil data
        This is separate from good because we may want to penalize 
        differently
        '''
        score = 0
        for evil in self.data_evil:
            try:
                if re.match(pattern, evil):
                    score+=100
                    if verbose:
                        print "%d    Match!: %s for %s" % (score, pattern, evil)
                else:
                    score-=1
                    if verbose:
                        print "%d   No match: %s for %s" %  (score, pattern, evil)
            except Exception as e:
                if verbose:
                    print e
                score+=100
        return score

    def get_good_score(self, pattern, verbose=False):
        score = 0
        for good in self.data_benign:
            try:
                if re.match(pattern, good):
                    score-=1
                else:
                    score+=1
            except Exception as e:
                score+=100
        return score


    def eval(self, ind):
        pattern = "^" + "".join(ind) + "$"
        sB = 0
        sE = 0
#Need to make sure if there is a opening there is also a closing
        if pattern.count("[") != 0 and pattern.count("]") == 0:
            sB += 5
            sE += 5
            
        sE += self.get_evil_score(pattern)
        sB += self.get_good_score(pattern)    

        # Need to minimize these values
        good_score =len(self.data_benign) + sB
        bad_score = len(self.data_evil) + sE
        len_score = len(pattern)

        if good_score == 0 and bad_score == 0:
            pass
            #pprint.pprint( log)
            #print "%s  Good=%d Bad=%d Len=%d" % (pattern, good_score, bad_score, len_score)
        return good_score, bad_score, len_score,

    def mutAddFilter(self, ind):
        c = self.get_random_char()
        ind.append(c)
        return ind,

    def mutDelFilter(self, ind):
        pos = random.randint(0, len(ind)-1)
        if not ind:
            ind.pop(pos)
        return ind,

    def mut(self, individual):
        c = self.get_random_char()
        pos = random.randint(0, len(individual)-1)
        individual[pos] = c
        return individual, 

    def mate(self, ind1, ind2):
        '''
        Random swap
        '''
        for i in range(min(len(ind1), len(ind2))):
            if random.random() < 0.5:
                ind1[i], ind2[i] = ind2[i], ind1[i]
        return ind1, ind2

    def evolve(self):
        random.seed(65)


        pop = self.toolbox.population(n=self.MU)
        hof = tools.ParetoFront()
        
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", numpy.mean, axis=0)
        stats.register("std", numpy.std, axis=0)
        stats.register("min", numpy.min, axis=0)
        stats.register("max", numpy.max, axis=0)
        
        logbook = tools.Logbook()
        logbook.header = "gen", "evals", "std", "min", "avg", "[good,evil,len]", "best"
        
        # Evaluate every individuals
        fitnesses = self.toolbox.map(self.toolbox.evaluate, pop)
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit

        hof.update(pop)
        record = stats.compile(pop)
        logbook.record(gen=0, evals=len(pop), **record)

#Only if verbose
        if self.verbose:
            print(logbook.stream)

        gen = 1
        while gen <= self.NGEN and (logbook[-1]["max"][0] != 0.0 or logbook[-1]["max"][1] != 0.0):
            
            # Select the next generation individuals
            offspring = self.toolbox.select(pop, len(pop))
            # Clone the selected individuals
            offspring = list(map(self.toolbox.clone, offspring))
        
            # Apply crossover and mutation on the offspring
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.CXPB:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < self.MUTPB:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values
                if random.random() < self.ADDPB:
                    self.toolbox.addFilter(mutant)
                    del mutant.fitness.values
                if random.random() < self.DELPB:
                    self.toolbox.delFilter(mutant) 
                    del mutant.fitness.values

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            
            b = tools.selBest(pop, k=1)[0]
            w = "".join(b) 
           
            if self.verbose:
                for p in pop:
                    _p = "".join(p)
                    if w == _p:
                        print "*\t" + _p
                    else:
                        print "\t" + _p

            # Select the next generation population
            record = stats.compile(pop)
            logbook.record(gen=gen, evals=len(invalid_ind), best=w, **record)
            pop = self.toolbox.select(pop + offspring, self.MU)
#only if verbose            
            if self.verbose:            
                print(logbook.stream)

            gen += 1

        return pop, logbook
    
    def create_regex(self):
        pop, stats = self.evolve()
        b = tools.selBest(pop, k=1)[0]
        return "^" + "".join(b) + "$"




def read_data(filename):
    with open(filename) as f:
        lines = f.read().splitlines()
        return lines

if __name__ == "__main__":
    f1 = sys.argv[1]
    f2 = sys.argv[2]
    data_evil = read_data(f1)
    data_benign = read_data(f2)
    ga = GaRegexCreator(data_evil, data_benign, verbose = True)
    
    filter = ga.create_regex()
    print filter

    ga.get_evil_score(filter, verbose=True)
