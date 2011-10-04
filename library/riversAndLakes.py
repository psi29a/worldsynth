#!/usr/bin/env python

import math, random
from numpy import *
from progressbar import ProgressBar, Percentage, ETA
from constants import *

class Bunch(dict): # be careful to delete after use, circular references are bad
    def __init__(self,**kw):
        dict.__init__(self,kw)
        self.__dict__ = self

class Rivers():
    def __init__(self, heightmap, rainmap):
        self.heightmap = heightmap
        self.rainmap = rainmap
        self.worldW = len(self.heightmap)
        self.worldH = len(self.heightmap[0])
        self.riverMap = zeros((self.worldW,self.worldH))
        self.riverList = []

    def run(self):
        widgets = ['Generating river sources: ', Percentage(), ' ', ETA() ]
        pbar = ProgressBar(widgets=widgets, maxval=self.worldH*self.worldH)
        # iterate through map and mark river sources
            # chance of river if rainfall is high and elevation around base of mountains
                # no rivers in 3x3 areas
                    # begin of a river
                    river = Bunch()
                    river.x = x
                    river.y = y
                    self.riverList.append(river)
                    del river

            pbar.update(x+y)
        pbar.finish()

        #print len(self.riverList),maxSteps

        widgets = ['Generating river paths: ', Percentage(), ' ', ETA() ]
        pbar = ProgressBar(widgets=widgets, maxval=maxSteps)

        # iterate through river sources
        for river in self.riverList:
            while self.heightmap[river.x,river.y] > WGEN_SEA_LEVEL:             # begin a river route until it reaches sea level
                # loop prevention checker
                    # if riverLoop > MAX_RIVER_LOOP: break
                # find path of least resistance and flow there
                    # Water flows based on cost, seeking the higest elevation difference
                    # biggest difference = lower (negative) cost
                    # Cost
                    # 0,0 1,0 2,0
                    # 0,1 *** 2,1
                    # 0,2 1,2 2,2
                    #cost[0,0] = 0 ; cost[1,0] = 0 ; cost[2,0] = 0
                    #cost[0,1] = 0 ;                 cost[2,1] = 0
                    #cost[0,2] = 0 ; cost[1,2] = 0 ; cost[2,2] = 0
                    cost = zeros((3,3))

                    # Top
                    cost[0,0] = ((self.heightmap[x-1,y-1]) - (self.heightmap[x,y]) ) //1.41
                    cost[1,0] =  (self.heightmap[x  ,y-1]) - (self.heightmap[x,y])
                    cost[2,0] = ((self.heightmap[x+1,y-1]) - (self.heightmap[x,y]) ) //1.41

                    # Mid
                    cost[0,1] =  (self.heightmap[x-1,y  ]) - (self.heightmap[x,y])
                    cost[2,1] =  (self.heightmap[x+1,y  ]) - (self.heightmap[x,y])

                    # Bottom
                    cost[0,2] = ((self.heightmap[x-1,y+1]) - (self.heightmap[x,y]) ) //1.41
                    cost[1,2] =  (self.heightmap[x  ,y+1]) - (self.heightmap[x,y])
                    cost[2,2] = ((self.heightmap[x+1,y+1]) - (self.heightmap[x,y]) ) //1.41

                    # Randomise flow */ 2
                    cost[0,0] = cost[0,0] * random.uniform(0.5, 2)
                    cost[1,0] = cost[1,0] * random.uniform(0.5, 2)
                    cost[2,0] = cost[2,0] * random.uniform(0.5, 2)
                    cost[0,1] = cost[0,1] * random.uniform(0.5, 2)
                    cost[2,1] = cost[2,1] * random.uniform(0.5, 2)
                    cost[0,2] = cost[0,2] * random.uniform(0.5, 2)
                    cost[1,2] = cost[1,2] * random.uniform(0.5, 2)
                    cost[2,2] = cost[2,2] * random.uniform(0.5, 2)

                    # Highest Cost
                    highestCost = min(cost[0,0], cost[1,0], cost[2,0],
                        cost[0,1], cost[2,1], cost[0,2], cost[1,2], cost[2,2])

                # no path found, find the lowest difference
                    # if lowest difference already a river
                        # mark as lake
                        # increment riverLoop
                    # else
                        #mark as river and keep going

        pbar.finish()

if __name__ == '__main__':
    print "hello!"
