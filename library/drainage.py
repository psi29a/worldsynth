#!/usr/bin/env python

import math, random
from numpy import *
from progressbar import ProgressBar, Percentage, ETA
from constants import *

class Bunch(dict): # be careful to delete after use, circular references are bad
    def __init__(self,**kw):
        dict.__init__(self,kw)
        self.__dict__ = self

class Drainage():
    def __init__(self, heightmap, rainmap):
        self.heightmap = heightmap
        self.rainmap = rainmap
        self.worldW = len(self.heightmap)
        self.worldH = len(self.heightmap[0])
        self.drainageMap = zeros((self.worldW,self.worldH))
        self.riverMap = zeros((self.worldW,self.worldH))
        self.riverList = []

    def run(self):
        # setup or local variables
        steps = 0
        maxSteps = int(math.sqrt((self.worldW*self.worldW) + (self.worldH*self.worldH)) / 2)
        # maxSteps = self.worldW / 2

        widgets = ['Generating drainage map: ', Percentage(), ' ', ETA() ]
        pbar = ProgressBar(widgets=widgets, maxval=self.worldH*self.worldH)
        # create drainage map
        for x in range(0,self.worldW):
            for y in range(0,self.worldH):

                # find the differences in elevation
                # postive number means it is of lower elvation (which is what we want for drainage)
                # now we sum all the positive numbers and create our drainage factor for that point
                elevationDifferences = zeros((3,3))
                drainage = 0.0
                for i in range(0,3):
                    for j in range(0,3):
                        if x-i < 0 or y-j < 0:
                            pass
                        elif x-i > self.worldW or y-j > self.worldH:
                            pass
                        else:
                            elevationDifferences[i,j] = self.heightmap[x,y] - self.heightmap[x-i,y-j]
                            if elevationDifferences[i,j] < 0:
                                pass
                            elif elevationDifferences[i,j] > 1:
                                drainage += 1
                            else:
                                drainage += elevationDifferences[i,j]

                print drainage
                self.drainageMap[x,y] = drainage
                pbar.update(x+y)
        pbar.finish()


        # Init rivers
        for i in range(0, (maxSteps*8)+1):
            x = random.randint(1, self.worldW-2)
            y = random.randint(1, self.worldH-2)
            if self.heightmap[x,y] > WGEN_SEA_LEVEL and self.heightmap[x,y] < 1.0:
                if random.uniform(0, self.rainmap[x,y]) > 0.125:
                    river = Bunch()
                    river.x = x
                    river.y = y
                    self.riverList.append(river)
                    del river

        print len(self.riverList),maxSteps

        widgets = ['Generating rivers and lakes: ', Percentage(), ' ', ETA() ]
        pbar = ProgressBar(widgets=widgets, maxval=maxSteps)

        # find rivers
        while True:
            moves = 0
            steps += 1

            # Water physics
            for river in self.riverList:
                x = river.x
                y = river.y

                if self.heightmap[x,y] > WGEN_SEA_LEVEL and x > 0 and y > 0 and x < self.worldW-1 and y < self.worldH-1:
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

                    for i in range(0, 3):
                        for j in range(0,3):
                            if (i == 1 and j == 1) == False: #and (cost[i,j] < 0) then

                                # Divide water up...
                                if cost[i,j] == highestCost:
                                    river.x = x+(i-1)
                                    river.y = y+(j-1)
                                    self.riverMap[x,y] = 1
                                    moves+=1

            pbar.update(steps)

            if moves == 0 or steps > maxSteps-1: # our exit strategy
                break

        pbar.finish()

if __name__ == '__main__':
    print "hello!"
