#!/usr/bin/env python

import math, random, sys
from numpy import *
from progressbar import ProgressBar, Percentage, ETA
from constants import *
from astar import AStar

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
        for x in range(1,self.worldW-1):
            for y in range(1,self.worldH-1):

                # rivers are sourced at the base of mountains
                if self.heightmap[x,y] < BIOME_ELEVATION_MOUNTAIN_LOW or self.heightmap[x,y] > BIOME_ELEVATION_MOUNTAIN:
                    continue

                # chance of river if rainfall is high and elevation around base of mountains

                # no rivers in 10x10 areas
                if self.isRiverInRange(20,x,y):
                    continue

                if random.random() <= 0.01:
                    # chance of river source
                    river = Bunch()
                    river.x = x
                    river.y = y
                    self.riverList.append(river)
                    del river
                    self.riverMap[x,y] = 0.1    # source is always a small in beginning
                    print x,y
            pbar.update(x+y)
        pbar.finish()

        #print len(self.riverList),maxSteps

        widgets = ['Generating river paths: ', Percentage(), ' ', ETA() ]
        pbar = ProgressBar(widgets=widgets, maxval=len(self.riverList))
        counter = 0
        # iterate through river sources
        for river in self.riverList:
            # begin a river route until it reaches sea level
            while True:

                newPath = {}
                newPath = self.findQuickPath(river)
                
                if newPath:
                    river.x = newPath['x']
                    river.y = newPath['y']

                # did we get to the sea?
                if self.heightmap[river.x,river.y] <= WGEN_SEA_LEVEL:
                    print "A river made it out to sea."
                    break

                # check if new river direction is an existing river
                if newPath and self.riverMap[river.x,river.y]:
                    print "A river found another river."
                    # follow route but strengthen the river
                    break #TODO

                if not newPath:
                    print "Trying to find another route to sea..."
                    newPath = self.findClosestSea(river)
                    if newPath:
                        river.x = newPath['x']
                        river.y = newPath['y']
                    else:
                        "River turns into a lake, begin flooding area..."
                        break

                self.riverMap[river.x,river.y] = 0.1


            counter += 1
            pbar.update(counter)

        pbar.finish()

    def findClosestSea(self, river, depth=20): # 10 = 10x10 area is -10 to 10
        temp = delta = 0.0
        currentElevation = self.heightmap[river.x, river.y]
        newPath = {}
        
        # find out next lowest point in range
        for x in range(-depth,depth+1):
            for y in range(-depth,depth+1):
                if river.x+x >= 0 and river.y+y >= 0 and \
                river.x+x < self.worldW and river.y+y < self.worldH:
                    temp = currentElevation - self.heightmap[river.x+x,river.y+y]
                    if temp > delta and temp >= WGEN_SEA_LEVEL:
                        newPath = {'x':river.x+x, 'y':river.y+y}
                        delta = temp
                    
        if newPath:
            print "Found a possible lowest point..."
            pathFinder = AStar(self.heightmap, (river.x, river.y), (newPath['x'],newPath['y']), EUCLIDEAN)
            for i in pathFinder.step():
                pass
            
            if pathFinder.path:
                print "Found path: ", pathFinder.path
            else:
                print "Could not find a new path."
                return {}
            
            for path in pathFinder.path:
                self.riverMap[path[0],path[1]] = 0.1
                if self.heightmap[path[0],path[1]] > currentElevation:
                   self.heightmap[path[0],path[1]] = currentElevation
                else:
                    currentElevation = self.heightmap[path[0],path[1]]
            
            return newPath

    def findQuickPath(self, river):
        # Water flows based on cost, seeking the higest elevation difference
        # highest positive number is the path of least resistance (lowest point)
        # Cost
        # *** 1,0 ***
        # 0,1 *** 2,1
        # *** 1,2 ***
        
        newPath = {}
        currentElevation = self.heightmap[river.x, river.y]
        
        # have we hit sea level?
        if currentElevation <= WGEN_SEA_LEVEL:
            return newPath
        
        # top
        if river.y-1 >= 0:
            top = currentElevation - self.heightmap[river.x, river.y-1]
            if top > 0.0: # if greater than current posistion
                newPath = {'x':river.x, 'y':river.y-1}
        else:
            top = 0.0
            
        # left
        if river.x-1 >= 0:
            left = currentElevation - self.heightmap[river.x-1, river.y]
            if left > 0.0 and left > top:
                newPath = {'x':river.x-1, 'y':river.y}
        else:
            left = top
            
        # right
        if river.x+1 < self.worldW:
            right = currentElevation - self.heightmap[river.x+1, river.y]
            if right > 0.0 and right > left:
                newPath = {'x':river.x+1, 'y':river.y}
        else:
            right = left
                        
        # bottom
        if river.y+1 < self.worldH:
            bottom = currentElevation - self.heightmap[river.x, river.y+1]
            if bottom > 0.0 and bottom > right:
                newPath = {'x':river.x, 'y':river.y+1}
        else:
            bottom = right
        
        
        # now try diagnals and find/digout/erode linking tile
        # top left
        if river.y-1 >= 0 and river.x-1 >= 0:
            topLeft = currentElevation - self.heightmap[river.x-1, river.y-1]
            if topLeft > 0.0 and topLeft > bottom:
                # find linking tile
#                if top > left:
#                    self.riverMap[river.x,river.y-1] = 0.1
#                    self.heightmap[river.x,river.y-1] = currentElevation
#                else:
#                    self.riverMap[river.x-1,river.y] = 0.1
#                    self.heightmap[river.x-1,river.y] = currentElevation                    
                newPath = {'x':river.x-1, 'y':river.y-1}      
        else:
            topLeft = bottom
        
        # top right
        if river.x+1 < self.worldW and river.x-1 >= 0:
            topRight = currentElevation - self.heightmap[river.x+1, river.y-1]
            if topRight > 0.0 and topRight > topLeft:
#                if top > right:
#                    self.riverMap[river.x,river.y-1] = 0.1
#                    self.heightmap[river.x,river.y-1] = currentElevation
#                else:
#                    self.riverMap[river.x+1,river.y] = 0.1
#                    self.heightmap[river.x+1,river.y] = currentElevation
                newPath = {'x':river.x+1, 'y':river.y-1}       
        else:
            topRight = topLeft 
        
        # bottom left
        if river.y-1 >= 0 and river.y+1 < self.worldH >= 0:
            bottomLeft = currentElevation - self.heightmap[river.x-1, river.y+1]
            if bottomLeft > 0.0 and bottomLeft > topRight:
#                if left > bottom:
#                    self.riverMap[river.x-1,river.y] = 0.1
#                    self.heightmap[river.x-1,river.y] = currentElevation
#                else:
#                    self.riverMap[river.x,river.y+1] = 0.1
#                    self.heightmap[river.x,river.y+1] = currentElevation
                newPath = {'x':river.x-1, 'y':river.y+1}         
        else:
            bottomLeft = topRight 
            
        # bottom right
        if river.x+1 < self.worldW and river.y+1 < self.worldH:
            bottomRight = currentElevation - self.heightmap[river.x+1, river.y+1]
            if bottomRight > 0.0 and bottomRight > bottomLeft:
#                if right > bottom:
#                    self.riverMap[river.x+1,river.y] = 0.1
#                    self.heightmap[river.x+1,river.y] = currentElevation
#                else:
#                    self.riverMap[river.x,river.y+1] = 0.1
#                    self.heightmap[river.x,river.y+1] = currentElevation
                newPath = {'x':river.x+1, 'y':river.y+1}           
        else:
            bottomRight = bottomLeft 
        
        #print river, newPath, top, left, right, bottom, topLeft, topRight, bottomLeft, bottomRight
        #sys.exit()
                
        return newPath
        

    def isRiverInRange(self, mapRange, tryX, tryY):
        absRange = abs(mapRange)
        for x in range(-(absRange/2),absRange/2+1):
            for y in range(-(absRange/2),absRange/2+1):
                if tryX+x >= 0 and tryY+y >= 0 and tryX+x < self.worldW and tryY+y < self.worldH:
                    if self.riverMap[tryX+x,tryY+y] > 0:
                        return True
        # no river found
        return False

    def makePath(self,currentX,currentY,river):
        currentElevation = self.heightmap[currentX,currentY]
        stepX = 1
        stepY = 1
        if river.x - currentX < 0:
            stepX = -1
        if river.y - currentY < 0:
            stepY = -1
        
        while currentX != river.x and currentY != river.y:
            currentX += stepX
            self.heightmap[currentX,currentY] = currentElevation
            self.riverMap[currentX,currentY] = 0.1
            currentY += stepY
            self.heightmap[currentX,currentY] = currentElevation
            self.riverMap[currentX,currentY] = 0.1
                                
if __name__ == '__main__':
    print "hello!"
