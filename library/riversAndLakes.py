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
        self.lakeMap = zeros((self.worldW, self.worldH))
        self.lakeList = []

    def run(self):
        riverSources = self.riverSources()

        for source in riverSources:
            x,y = source
            #self.riverMap[x,y] = 0.1
            #continue

            print "Finding path for river: ", source
            river = self.riverFlow(source)
            #print 'River path:', river

            if river:
                print "Simulating erosion..."
                self.riverErosion(river)

            for wx,wy in river:
                self.riverMap[wx, wy] = 0.1

            #self.riverMap[x, y] = 0.1
            #break

        for lake in self.lakeList:
            print "Found a lake here: ", lake
            #lakeWater = self.simulateFlood(lake['x'], lake['y'], self.heightmap[lake['x'], lake['y']] + 0.001)

        return

    def riverSources(self):
        '''Find places on map where sources of river can be found '''
        widgets = ['Finding river sources: ', Percentage(), ' ', ETA()]
        pbar = ProgressBar(widgets=widgets, maxval=self.worldH*self.worldH)

        riverSourceList = []

        square = 32
        #square = int(math.log(self.worldH, 2)**2)

        # iterate through map and mark river sources
        for x in range(0, self.worldW-1, square):
            for y in range(0, self.worldH-1, square):

                #print 'Ranges: ', x, y, square+x, square+y

                # chance of river if rainfall is high and
                # elevation around base of mountains
                # TODO

                # find random location
                sources = []
                for sx in range(x, x+square):
                    for sy in range(y, y+square):

                        if self.isOutOfBounds([sx, sy]):
                            continue

                        if self.heightmap[sx, sy] < BIOME_ELEVATION_HILLS or \
                            self.heightmap[sx, sy] > BIOME_ELEVATION_MOUNTAIN_LOW:
                            continue

                        sources.append([sx, sy])

                #print len(sources), sources

                if sources:
                    #print "Possible sources: ", len(sources)
                    source = sources[random.randint(0, len(sources))]
                    #print "River source: ", source
                    riverSourceList.append(source)

            pbar.update(x+y)
        pbar.finish()
        return riverSourceList

    def inCircle(self, radius, center_x, center_y, x, y):
        square_dist = (center_x - x) ** 2 + (center_y - y) ** 2
        return square_dist <= radius ** 2

    def riverFlow(self, source):
        '''simulate fluid dynamics by using starting point and flowing to the
        lowest available point'''
        x, y = source
        currentLocation =  source
        #currentElevation = self.heightmap[x, y]
        path = [source]
        direction = []

        # start the flow
        while True:

            # found another river?
            if self.riverMap[x, y] > 0.0:
                #print "A river found another river."
                break #TODO:  make remaining river stronge

            # found a sea?
            if self.heightmap[x, y] <= WGEN_SEA_LEVEL:
                #print "A river made it out sea."
                break

            # find our immediate lowest elevation and flow there
            quickSection = self.findQuickPath(currentLocation)

            if quickSection:
                path.append(quickSection)
                qx, qy = quickSection
                direction = [x-qx, y-qy]
                currentLocation = quickSection
                #currentElevation = self.heightmap[x, y]

            else:
                #print "  A river became stuck...", currentLocation, direction
                lowerElevation = self.findLowerElevation(currentLocation)
                if lowerElevation:
                    #print '    Found a lower elevation here: ', lowerElevation
                    lowerPath = self.findPath(currentLocation, lowerElevation)
                    if lowerPath:
                        #print '      Lower path found: ', lowerPath
                        path += lowerPath
                        currentLocation = lowerPath[-1]
                        #currentElevation = self.heightmap[x, y]
                    else:
                        #print '      No path to lower elevation found.'
                        break
                else:
                    #print '    This river flows into a lake!'
                    self.lakeList.append(currentLocation)
                    break

        return path

    def riverErosion(self, river):
        '''Simulate erosion in heightmap based on river path.
            * current location must be equal to or less than previous location
            * riverbed is carved out by % of volume/flow
            * sides of river are also eroded to slope into riverbed.
            '''

        for r in river:
            x,y = r


        return


    def findQuickPath(self, river):
        # Water flows based on cost, seeking the higest elevation difference
        # highest positive number is the path of least resistance (lowest point)
        # Cost
        # *** 1,0 ***
        # 0,1 *** 2,1
        # *** 1,2 ***
        x, y = river
        newPath = {}
        lowestElevation = self.heightmap[x, y]
        #lowestDirection = [0, 0]

        for direction in DIR_ALL:
            tempDir = [x+direction[0], y+direction[1]]
            tx, ty = tempDir


            if self.isOutOfBounds(tempDir):
                continue

            elevation = self.heightmap[tx, ty]

            #print river, direction, tempDir, elevation, direction[0], direction[1]

            if elevation < lowestElevation:
                lowestElevation = elevation
                #lowestDirection = direction
                newPath = tempDir

        #print newPath, lowestDirection, elevation
        #sys.exit()

        return newPath

    def isOutOfBounds(self, source):
        ''' verify that we do not go over the edge of map '''
        x, y = source
        if x < 0 or y < 0 or x >= self.worldW or y >= self.worldH:
            return True

        return False

    def findLowerElevation(self, source):
        '''Try to find a lower elevation with in a range of an increasing
        circle's radius and try to find the best path and return it'''
        x, y = source
        currentRadius = 1
        maxRadius = 40
        lowestElevation = self.heightmap[x, y]
        destination = []
        notFound = True

        while notFound and currentRadius <= maxRadius:
            for cx in range(-currentRadius, currentRadius+1):
                for cy in range(-currentRadius, currentRadius+1):
                    # are we within bounds?
                    if self.isOutOfBounds([x+cx, y+cy]):
                        continue

                    # are we within a circle?
                    if not self.inCircle(currentRadius, x, y, x+cx, y+cy):
                        continue

                    # have we found a lower elevation?
                    elevation = self.heightmap[x+cx, y+cy]

                    if elevation < lowestElevation:
                        lowestElevation = elevation
                        destination = [x+cx, y+cy]
                        notFound = False

            currentRadius += 1
        return destination

    def findPath(self, source, destination):
        '''Using the a* algo we will try to find the best path between two
        points'''
        sx, sy = source
        dx, dy = destination
        path = []

        # flatton array
        heightmap = self.heightmap.reshape(self.worldW * self.worldH)

        pathFinder = AStar(SQ_MapHandler(heightmap, self.worldW, self.worldH))
        start = SQ_Location(sx, sy)
        end = SQ_Location(dx, dy)

        #s = time()
        p = pathFinder.findPath(start, end)
        #e = time()

        if not p:
            #print "      No path found! It took %f seconds." % (e-s)
            pass
        else:
            #print "      Found path in %d moves and %f seconds." % (len(p.nodes), (e-s))
            for n in p.nodes:
                path.append([n.location.x, n.location.y])
                if self.riverMap[n.location.x, n.location.y] > 0.0:
                    #print "aStar: A river found another river"
                    break #TODO: add more river strength

                if self.heightmap[n.location.x, n.location.y] <= WGEN_SEA_LEVEL:
                    #print "aStar: A river made it to the sea."
                    break
        return path

    def simulateFloodi(self, x, y, elevation):
        '''Flood fill area based on elevation.
        The recursive algorithm. Starting at x and y, changes and marks any
        adjacent area that is under the elevation.'''

        # are we in bounds of world
        if self.isOutOfBounds({'x': x, 'y': y}):
            return

        # Base case. If the current [x, y] elevation is greater then do nothing.
        if self.heightmap[x, y] > elevation:   
            return

        # Flood area and mark on map
        self.lakeMap[x, y] = 1
        print 'lake at: ', x, y

        # Recursive calls.
        self.simulateFlood(x-1, y, elevation) # left
        self.simulateFlood(x, y-1, elevation) # up
        self.simulateFlood(x+1, y, elevation) # right
        self.simulateFlood(x, y+1, elevation) # down

    def simulateFlood(self, x, y, elevation):
        '''Flood fill area based on elevation.
        The iterative algorithm. Starting at x and y, changes and marks any
        adjacent area that is under the elevation.'''

        theStack = [(x, y)]

        while len(theStack) > 0:
            x, y = theStack.pop()

            # are we in bounds of world
            if self.isOutOfBounds({'x': x, 'y': y}):
                continue

            # Base case. If the current [x, y] elevation is greater then do nothing.
            if self.heightmap[x, y] > elevation:
                continue

            # Flood area and mark on map
            self.lakeMap[x, y] = 1
            print 'lake at: ', x, y

            theStack.append((x-1, y)) # left
            theStack.append((x, y-1)) # up
            theStack.append((x+1, y)) # right
            theStack.append((x, y+1)) # down



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

if __name__ == '__main__':
    print "hello!"
