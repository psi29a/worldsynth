#!/usr/bin/env python

import math, random, sys
from time import time
from numpy import *
from progressbar import ProgressBar, Percentage, ETA
from constants import *
from aStar import *


class Rivers():

    def __init__(self, heightmap, rainmap):
        self.heightmap = heightmap
        self.rainmap = rainmap
        self.worldW = len(self.heightmap)
        self.worldH = len(self.heightmap[0])
        self.riverMap = zeros((self.worldW, self.worldH))
        self.riverList = []

    def run(self):
        sources = self.riverSources()

        for source in sources:

            print "Finding path for river: ", source
            river = self.simulateFluid(source)
            print 'River path:', river

            for water in river:
                self.riverMap[water['x'], water['y']] = 0.1

            #self.riverMap[source['x'], source['y']] = 0.1
            #break
        return


    def riverSources(self):
        widgets = ['Finding river sources: ', Percentage(), ' ', ETA()]
        pbar = ProgressBar(widgets=widgets, maxval=self.worldH*self.worldH)

        riverSourceList = []

        # iterate through map and mark river sources
        for x in range(1, self.worldW-1):
            for y in range(1, self.worldH-1):

                # rivers are sourced at the base of mountains
                if self.heightmap[x, y] < BIOME_ELEVATION_HILLS or \
                    self.heightmap[x, y] > BIOME_ELEVATION_MOUNTAIN_LOW:
                    continue

                # chance of river if rainfall is high and elevation around base of mountains

                # based on size of map, we check if there are any rivers in the area
                if self.isRiverNearby(20, x, y):
                    continue

                if random.random() <= 0.01:
                    # chance of river source
                    riverSource = {'x': x, 'y': y}
                    print riverSource
                    riverSourceList.append(riverSource)

            pbar.update(x+y)
        pbar.finish()
        return riverSourceList

    def isRiverNearby(self, radius, tryX, tryY):
        ''' return true if there is a river in the range of radius from
        source '''
        for x in range(-radius, radius+1):
            for y in range(-radius, radius+1):

                # are we within bounds?
                if self.isOutOfBounds({'x': tryX+x, 'y': tryY+y}):
                    continue

                # are we within a circle?
                if not self.inCircle(radius, tryX, tryY, tryX+x, tryY+y):
                    continue

                # found a river?
                if self.riverMap[tryX+x, tryY+y] > 0.0:
                    return True

        # no river found
        return False

    def inCircle(self, center_x, center_y, radius, x, y):
        square_dist = (center_x - x) ** 2 + (center_y - y) ** 2
        return square_dist <= radius ** 2

    def simulateFluid(self, source):
        '''simulate fluid dynamics by using starting point and flowing to the
        lowest available point'''

        currentLocation = source
        currentElevation = self.heightmap[source['x'], source['y']]
        path = [source]
        direction = []

        while True:
            # find our immediate lowest elevation and flow there
            quickSection = self.findQuickPath(currentLocation)

            if quickSection:
                path.append(quickSection)
                direction = {'x': currentLocation['x']-quickSection['x'], 'y': currentLocation['y']-quickSection['y']}
                currentLocation = quickSection
                currentElevation = self.heightmap[currentLocation['x'], currentLocation['y']]

                if self.riverMap[currentLocation['x'], currentLocation['y']] > 0.0:
                    print "Quick: A river found another river"
                    break #TODO:  make remaining river stronger


                if self.heightmap[currentLocation['x'], currentLocation['y']] <= WGEN_SEA_LEVEL:
                    print "Quick: A river found the sea"
                    break

            else:
                print "A river became stuck...", currentLocation, direction
                break


        return path

    def findQuickPath(self, river):
        # Water flows based on cost, seeking the higest elevation difference
        # highest positive number is the path of least resistance (lowest point)
        # Cost
        # *** 1,0 ***
        # 0,1 *** 2,1
        # *** 1,2 ***

        newPath = {}
        lowestElevation = self.heightmap[river['x'], river['y']]
        lowestDirection = [0,0]

        for direction in DIRECTIONS:
            tempPath = {'x': river['x']+direction[0], 'y': river['y']+direction[1]}

            if self.isOutOfBounds(tempPath):
                continue

            elevation = self.heightmap[tempPath['x'], tempPath['y']]

            #print river, direction, tempPath, elevation, direction[0], direction[1]

            if elevation < lowestElevation:
                lowestElevation = elevation
                lowestDirection = direction
                newPath = tempPath


        #print newPath, lowestDirection, elevation
        #sys.exit()

        return newPath

    def isOutOfBounds(self, source):
        ''' verify that we do not go over the edge of map '''
        if source['x'] < 0 or source['y'] < 0 or \
            source['x'] >= self.worldW or source['y'] >= self.worldH:
            return True

        return False

    def findLowerElevation(self, source, radius):
        '''Try to find a lower elevation with in a range of an increasing
        circle's radius and try to find the best path and return it'''

        currentRadius = 1
        lowestElevation = self.heightmap[source['x'], source['y']]
        destination = []

        while currentRadius <= radius:
            for x in range(-currentRadius, currentRadius+1):
                for y in range(-currentRadius, currentRadius+1):

                    # are we within bounds?
                    if self.isOutOfBounds({'x': source['x']+x, 'y': source['y']+y}):
                        continue

                    # are we within a circle?
                    if not self.inCircle(currentRadius, source['x'], source['y'], source['x']+x, source['y']+y):
                        continue

                    # have we found a lower elevation?
                    elevation = self.heightmap[source['x']+x, source['y']+y]
                    if elevation < lowestElevation:
                        lowestElevation = elevation
                        destination = {'x': source['x']+x, 'y': source['y']+y}


             currentRadius += 1









    def floodArea(self, currentLocation):
        '''begin flooding area until we find a lower elevation or until we
        reach saturation of begin of mountain range'''

        river = currentLocation

        # check radius around location if we can find a lower elevation
        radius = 2
        startElevation = self.heightmap[river.x, river.y]
        elevation = self.heightmap[river.x, river.y]
        pressure = 0.01

        #floodMap = zeros((self.worldW, self.worldH))

        while pressure > 0:
            newPaths = []
            # increase our water elevation
            elevation += 0.001
            pressure -= 0.001

            for x in range(-radius, radius+1):
                for y in range(-radius, radius+1):

                    # ignore ourselves
                    if x == 0 and y == 0:
                        continue

                    # verify that we do not go over the edge of map
                    if river.x+x < 0 or river.y+y < 0 or \
                    river.x+x > self.worldW-1 or river.y+y > self.worldH-1:
                        continue # is out of bounds, ignore

                    # check that we are in circle
                    if not self.in_circle(river.x, river.y, radius, river.x+x, river.y+y):
                        continue

                    # are we in the mountains?
                    if self.heightmap[river.x+x, river.y+y] > BIOME_ELEVATION_MOUNTAIN_LOW:
                        continue

                    # is an increase in water elevation enough to find a way out?
                    if self.heightmap[river.x+x, river.y+y] < elevation:
                        newPaths.append({'x': river.x+x, 'y': river.y+y})
                        #floodMap[river.x+x, river.y+y] = 0.1



        print startElevation, elevation, newPaths
        #sys.exit()
        return newPaths

    def findLowerElevation(self, river, radius):
        '''Try to find a lower elevation with in a range of a circle's radius
        and try to find the best path and return it'''

        #TODO: perhaps flooding algo is better?

        lowestElevation = self.heightmap[river.x, river.y]
        lowestRiver = river
        foundLowerElevation = False

        for x in range(-radius, radius+1):
            for y in range(-radius, radius+1):
                # verify that we do not go over the edge of map
                if river.x+x < 0 or river.y+y < 0 or \
                river.x+x > self.worldW-1 or river.y+y > self.worldH-1:
                    continue # is out of bounds, ignore

                # check that we are in circle
                if not self.in_circle(river.x, river.y, radius, river.x+x, river.y+y):
                    continue

                if self.heightmap[river.x+x, river.y+y] < lowestElevation:
                    foundLowerElevation = True
                    lowestElevation = self.heightmap[river.x+x, river.y+y]
                    lowestRiver.x = river.x+x
                    lowestRiver.y = river.y+y

        if foundLowerElevation:
            return self.findPath(river, lowestRiver)
        else:
            return None


    def findPath(self, source, destination):
        '''Using the a* algo we will try to find the best path between two
        points'''

        path = []

        heightmap = self.heightmap.reshape(self.worldW * self.worldH) # flatton array

        pathFinder = AStar(SQ_MapHandler(heightmap, self.worldW, self.worldH))
        start = SQ_Location(source.x, source.y)
        end = SQ_Location(destination.x, destination.x)

        s = time()
        p = pathFinder.findPath(start, end)
        e = time()

        if not p:
            print "No path found! It took %f seconds." % (e-s)
        else:
            print "Found path in %d moves and %f seconds." % (len(p.nodes), (e-s))
            for n in p.nodes:
                path.append({'x': n.location.x, 'y': n.location.y})
                if self.riverMap[n.location.x, n.location.y] > 0.0:
                    print "aStar: A river found another river"
                    break #TODO: add more river strength

                if self.heightmap[n.location.x, n.location.y] <= WGEN_SEA_LEVEL:
                    print "aStar: A river made it to the sea."
                    break

        return path





    def makePath(self, river, newPath):
        heightmap = self.heightmap.reshape(self.worldW * self.worldH)

        pathFinder = AStar(SQ_MapHandler(heightmap, self.worldW, self.worldH))
        start = SQ_Location(river.x, river.y)
        end = SQ_Location(newPath['x'], newPath['y'])

        s = time()
        p = pathFinder.findPath(start, end)
        e = time()

        if not p:
            print "No path found! It took %f seconds." % (e-s)
            return {}
        else:
            print "Found path in %d moves and %f seconds." % (len(p.nodes), (e-s))
            for n in p.nodes:
                #self.pathlines.append((n.location.x*16+8,n.location.y*16+8))
                #print river.x, river.y, n.location.x, n.location.y, newPath['x'], newPath['y']
                if self.riverMap[n.location.x, n.location.y] > 0.0:
                    print "River found another river"
                    break #TODO: add more river strength
                self.riverMap[n.location.x, n.location.y] = 0.1
            return {'x': newPath['x'], 'y': newPath['y']}


    def findClosestSea(self, river):
        '''Try to find the closest sea by avoiding watersheds, the returned
        value should be a point in sea itself '''

        radius = 1
        while radius < self.worldW:

            for x in range(-radius, radius+1):
                for y in range(-radius, radius+1):
                    # verify that we do not go over the edge of map
                    if river.x+x >= 0 and river.y+y >= 0 and \
                    river.x+x < self.worldW and river.y+y < self.worldH:

                        # check that we are in circle
                        if not self.in_circle(river.x, river.y, radius, river.x+x, river.y+y):
                            continue

                        elevation = self.heightmap[river.x+x, river.y+y]
                        #if elevation > BIOME_ELEVATION_MOUNTAIN:
                        #    break # we hit the watershed, do not continue

                        if elevation < WGEN_SEA_LEVEL:
                            # possible sea, lets check it out...
                            # is the spot surrounded by sea?
                            isSea = True
                            seaRange = 4
                            for i in range(-seaRange, seaRange+1):
                                for j in range(-seaRange, seaRange+1):
                                    if river.x+x+i >= 0 and river.y+y+j >= 0 and \
                                    river.x+x+i < self.worldW and river.y+y+j < self.worldH:
                                        if self.heightmap[river.x+x+i, river.y+y+j] > WGEN_SEA_LEVEL:
                                            isSea = False

                            if isSea:
                                print "River at source:", river.x, river.y, " found the sea at: ", river.x+x, river.y+y
                                return {'x': river.x+x, 'y': river.y+y}

            radius += 1 # increase searchable area

        print "Could not find sea."
        return {}

    def pathFindToLocation(self, river, depth=20): # 10 = 10x10 area is -10 to 10
        temp = delta = 0.0
        currentElevation = self.heightmap[river.x, river.y]
        newPath = {}

        # find out next lowest point in range
        for x in range(-depth, depth+1):
            for y in range(-depth, depth+1):
                if river.x+x >= 0 and river.y+y >= 0 and \
                river.x+x < self.worldW and river.y+y < self.worldH:
                    temp = currentElevation - self.heightmap[river.x+x, river.y+y]
                    if temp > delta and temp >= WGEN_SEA_LEVEL:
                        newPath = {'x': river.x+x, 'y': river.y+y}
                        delta = temp

        if newPath:
            print "Found a possible lowest point..."
#            pathFinder = AStar(self.heightmap, (river.x, river.y), (newPath['x'],newPath['y']), EUCLIDEAN)
#            for i in pathFinder.step():
#                pass

            # flatten heightmap
            heightmap = self.heightmap.reshape(self.worldW * self.worldH)

            pathFinder = AStar(SQ_MapHandler(heightmap, self.worldW, self.worldH))
            start = SQ_Location(river.x, river.y)
            end = SQ_Location(newPath['x'], newPath['y'])
            s = time()
            p = pathFinder.findPath(start, end)
            e = time()

            if not p:
                print "No path found!"
                return {}
            else:
                print "Found path in %d moves and %f seconds." % (len(p.nodes), (e-s))
                for n in p.nodes:
                    #self.pathlines.append((n.location.x*16+8,n.location.y*16+8))
                    #print river.x, river.y, n.location.x, n.location.y, newPath['x'], newPath['y']
                    self.riverMap[n.location.x, n.location.y] = 0.1

#            if pathFinder.path:
#                print "Found path: ", pathFinder.path
#            else:
#                print "Could not find a new path."
#                return {}

#            for path in pathFinder.path:
#                self.riverMap[path[0],path[1]] = 0.1
#                if self.heightmap[path[0],path[1]] > currentElevation:
#                   self.heightmap[path[0],path[1]] = currentElevation
#                else:
#                    currentElevation = self.heightmap[path[0],path[1]]
#
#            return newPath


#    def makePath(self,currentX,currentY,river):
#        currentElevation = self.heightmap[currentX,currentY]
#        stepX = 1
#        stepY = 1
#        if river.x - currentX < 0:
#            stepX = -1
#        if river.y - currentY < 0:
#            stepY = -1
#
#        while currentX != river.x and currentY != river.y:
#            currentX += stepX
#            self.heightmap[currentX,currentY] = currentElevation
#            self.riverMap[currentX,currentY] = 0.1
#            currentY += stepY
#            self.heightmap[currentX,currentY] = currentElevation
#            self.riverMap[currentX,currentY] = 0.1

if __name__ == '__main__':
    print "hello!"
