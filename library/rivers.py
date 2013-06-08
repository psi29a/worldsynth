#!/usr/bin/env python
"""
Part of the World Generator project. 

author:  Bret Curtis
license: LGPL v2

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
version 2 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
02110-1301 USA
"""
import math, random, numpy, aStar, constants, utilities
from PySide import QtGui

overflow = lambda value, maxValue: value % maxValue

class Rivers():
    '''Generates fresh water sources, rivers and lakes either randomly or with 
    a rainmap.'''

    def __init__(self):
        pass

    def generate(self, heightmap, rainmap=None, sb=None, wrap=True):
        if sb:
            progressValue = 0
            progress = QtGui.QProgressBar()
            progress.setRange(0, 5)
            sb.addPermanentWidget(progress)
            progress.setValue(0)
        self.heightmap = heightmap.copy()
        self.size = heightmap.shape
        self.worldW = len(self.heightmap)
        self.worldH = len(self.heightmap[0])
        self.riverMap = numpy.zeros((self.worldW, self.worldH))
        self.lakeMap = numpy.zeros((self.worldW, self.worldH))
        self.waterPath = numpy.zeros((self.worldW, self.worldH), dtype=int)
        self.erosionMap = numpy.zeros((self.worldW, self.worldH))
        self.lakeList = []
        self.riverList = []
        self.rainMap = rainmap
        self.waterFlow = numpy.zeros((self.worldW, self.worldH))
        self.wrap = wrap
        
        # step one: water flow per cell based on rainfall 
        self.findWaterFlow()
        if sb:
            progress.setValue(progressValue)
            progressValue += 1

        # step two: find river sources (seeds)
        riverSources = self.riverSources()
        if sb:
            progress.setValue(progressValue)
            progressValue += 1
        print riverSources
        # step three: for each source, find a path to sea
        for source in riverSources:
            river = self.riverFlow(source)
            if len(river) > 0:
                self.riverList.append(river)
                self.cleanUpFlow(river)
                rx, ry = river[-1]  # find last cell in river                
                if (self.heightmap[rx, ry] > constants.WGEN_SEA_LEVEL):
                    self.lakeList.append(river[-1])  # river flowed into a lake         
        if sb:
            progress.setValue(progressValue)
            progressValue += 1

        # step four: simulate erosion and updating river map
        for river in self.riverList:
            self.riverErosion(river)
            self.riverMapUpdate(river)
        if sb:
            progress.setValue(progressValue)
            progressValue += 1

        # step five: rivers with no paths to sea form lakes    
        for lake in self.lakeList:
            # print "Found lake at:",lake
            lx, ly = lake
            self.lakeMap[lx, ly] = 0.1  # TODO: make this based on rainfall/flow
            # lakeWater = self.simulateFlood(lake['x'], lake['y'], self.heightmap[lake['x'], lake['y']] + 0.001)
        
        # step six: generate an erosion map that gives us the height difference from original heightmap
        self.erosionMap = heightmap - self.heightmap  # erosion is of positive values
        
        if sb:
            progress.setValue(progressValue)
            progressValue += 1
            sb.removeWidget(progress)
            del progress
        return

    def findWaterFlow(self):
        '''Find the flow direction for each cell in heightmap'''
        # iterate through each cell
        for x in xrange(self.worldW - 1):
            for y in xrange(self.worldH - 1):
                # search around cell for a direction
                path = self.findQuickPath([x, y])
                if path:
                    tx, ty = path
                    flowDir = [tx - x, ty - y]
                    key = 0
                    for direction in constants.DIR_NEIGHBORS_CENTER:
                        if direction == flowDir:
                            self.waterPath[x, y] = key
                        key += 1

                # print DIR_ALL_CENTER[self.waterPath[x,y]]

    def riverSources(self):
        '''Find places on map where sources of river can be found'''
        riverSourceList = []
        if self.waterFlow is None:
            # Version 1, is 'good enough' but we can do better.          
            square = 32
            # square = int(math.log(self.worldH, 2)**2)
            # iterate through map and mark river sources
            for x in range(0, self.worldW - 1, square):
                for y in range(0, self.worldH - 1, square):
                    # print 'Ranges: ', x, y, square+x, square+y    
                    # find random location
                    sources = []
                    for sx in range(x, x + square):
                        for sy in range(y, y + square):
                            if not self.wrap and utilities.outOfBounds([sx, sy], self.size):
                                continue
                            # convert to wrap around
                            sx, sy = overflow(sx, self.worldW), overflow(sy, self.worldH)
                            if self.heightmap[sx, sy] < constants.BIOME_ELEVATION_HILLS or \
                                self.heightmap[sx, sy] > constants.BIOME_ELEVATION_MOUNTAIN_LOW:
                                continue
                            sources.append([sx, sy])
                    # print len(sources), sources
                    if sources:
                        # print "Possible sources: ", len(sources)
                        source = sources[random.randint(0, len(sources))]
                        # print "River source: ", source
                        riverSourceList.append(source)
        else:
            # Version 2, with rainfall
            #  Using the wind and rainfall data, create river 'seeds' by 
            #     flowing rainfall along paths until a 'flow' threshold is reached
            #     and we have a beginning of a river... trickle->stream->river->sea

            # step one: Using flow direction, follow the path for each cell
            #     adding the previous cell's flow to the current cell's flow.
            # step two: We loop through the water flow map looking for cells 
            #     above the water flow threshold. These are our river sources and
            #     we mark them as rivers. While looking, the cells with no
            #     out-going flow, above water flow threshold and are still 
            #     above sea level are marked as 'sources'.
            for x in range(0, self.worldW - 1):
                for y in range(0, self.worldH - 1):
                    rainFall = self.rainMap[x, y]
                    self.waterFlow[x, y] = rainFall

                    if self.waterPath[x, y] == 0:
                        continue  # ignore cells without flow direction
                    cx, cy = x, y  # begin with starting location
                    neighbourSeedFound = False
                    while not neighbourSeedFound:  # follow flow path to where it may lead

                        # have we found a seed?
                        if self.heightmap[cx, cy] >= constants.BIOME_ELEVATION_HILLS_LOW and \
                            self.heightmap[cx, cy] <= constants.BIOME_ELEVATION_MOUNTAIN_LOW and \
                            self.waterFlow[cx, cy] >= 10.0:

                            # try not to create seeds around other seeds
                            for seed in riverSourceList:
                                sx, sy = seed
                                if utilities.inCircle(9, cx, cy, sx, sy):
                                    neighbourSeedFound = True
                            if neighbourSeedFound:
                                break  # we do not want seeds for neighbors

                            riverSourceList.append([cx, cy])  # river seed
                            # self.riverMap[cx,cy] = self.waterFlow[cx,cy] #temp: mark it on map to see 'seed'
                            break

                        # no path means dead end...
                        if self.waterPath[cx, cy] == 0:
                            break  # break out of loop

                        # follow path, add water flow from previous cell                            
                        dx, dy = constants.DIR_NEIGHBORS_CENTER[self.waterPath[cx, cy]]
                        nx, ny = cx + dx, cy + dy  # calculate next cell
                        self.waterFlow[nx, ny] += rainFall
                        cx, cy = nx, ny  # set current cell to next cell 
        return riverSourceList

    def riverFlow(self, source):
        '''simulate fluid dynamics by using starting point and flowing to the
        lowest available point'''
        currentLocation = source
        path = [source]

        # start the flow
        while True:
            x, y = currentLocation
            lowerElevation = None
            quickSection = None            
            isWrapped = False

            for dx, dy in constants.DIR_NEIGHBORS:  # is there a river nearby, flow into it
                ax, ay = x + dx, y + dy
                if self.wrap:
                    ax, ay = overflow(ax, self.worldW), overflow(ay, self.worldH)
                    
                for river in self.riverList:
                    if [ax, ay] in river:
                        #print "Found another river at:", x, y, " -> ", ax, ay, " Thus, using that river's path."
                        merge = False
                        for rx, ry in river:
                            if [ax, ay] == [rx, ry]:
                                merge = True
                                path.append([rx, ry])
                            elif merge == True:
                                path.append([rx, ry])
                        return path  # skip the rest, return path

            # found a sea?
            #print "Flowing to...",x,y
            if self.heightmap[x, y] <= constants.WGEN_SEA_LEVEL:
                break

            # find our immediate lowest elevation and flow there
            quickSection = self.findQuickPath(currentLocation)

            if quickSection:
                path.append(quickSection)
                currentLocation = quickSection
                continue # stop here and enter back into loop
            
            isWrapped, lowerElevation = self.findLowerElevation(currentLocation)
            if lowerElevation and not isWrapped:
                lowerPath = None                                   
                lowerPath = aStar.pathFinder().find(self.heightmap, currentLocation, lowerElevation)            
                if lowerPath:
                    path += lowerPath
                    currentLocation = path[-1]
                else:
                    break
            elif lowerElevation and isWrapped:
                #TODO: make this more natural
                maxRadius = 40
                wrappedX = wrappedY = False
#                print 'Found a lower elevation on wrapped path, searching path!'
#                print 'We go from',currentLocation,'to',lowerElevation
                cx,cy = currentLocation
                lx,ly = lowerElevation
                nx,ny = lowerElevation
                
                if (x < 0 or y < 0 or x > self.worldW or y > self.worldH):
                    print "BUG: fix me... we shouldn't be here:", currentLocation, lowerElevation
                    break
                
                if not utilities.inCircle(maxRadius, cx, cy, lx, cy):
                    # are we wrapping on x axis?
                    #print "We found wrapping along x-axis"
                    if cx-lx < 0:
                        lx = 0 # move to left edge
                        nx = self.worldW-1 # next step is wrapped around
                    else:
                        lx = self.worldW-1 # move to right edge
                        nx = 0 # next step is wrapped around
                    ly = ny = int( (cy+ly)/2 ) # move halfway
                elif not utilities.inCircle(maxRadius, cx, cy, cx, ly):
                    # are we wrapping on y axis?
#                    print "We found wrapping along y-axis"
                    if cy-ly < 0:
                        ly = 0 # move to top edge
                        ny = self.worldH-1 # next step is wrapped around
                    else:
                        ly = self.worldH-1 # move to bottom edge
                        ny = 0 # next step is wrapped around
                    lx = nx = int( (cx+lx)/2 ) # move halfway
                else:
#                    print "BUG: fix me... we are not in circle:", currentLocation, lowerElevation
                    break
                
                # find our way to the edge
                edgePath = None  
                edgePath = aStar.pathFinder().find(self.heightmap, [cx,cy], [lx,ly])
                if not edgePath:
#                    print "We've reached the end of this river, we cannot get through."
                    # can't find another other path, make it a lake
                    self.lakeList.append(currentLocation)
                    break
                path += edgePath # add our newly found path
                path.append([nx,ny]) # finally add our overflow to other side
                currentLocation = path[-1]
#                print "Path found from ", [cx,cy], 'to', [lx,ly], 'via:'
#                print edgePath
#                print "We then wrap on: ", [nx, ny]
                
                # find our way to lowest position original found
                lowerPath = aStar.pathFinder().find(self.heightmap, currentLocation, lowerElevation)
                path += lowerPath
                currentLocation = path[-1]
#                print "We then go to our destination: ", lowerElevation
#                print lowerPath
#                print " "                    
#                print "Full path begin and end ", path[0], path[-1]
                hx,hy = path[0]
                hlx,hly = path[-1]
#                print "Elevations: ", self.heightmap[hx,hy], self.heightmap[hlx,hly]
#                print "Erosion: ", self.erosionMap[hx,hy], self.erosionMap[hlx,hly]
#                print " "
                #break
            else: # can't find any other path, make it a lake
                self.lakeList.append(currentLocation)
                break # end of river
            
            if utilities.outOfBounds(currentLocation, self.size):
                print "Why are we here:",currentLocation   

        return path

    def cleanUpFlow(self, river):
        '''Validate that for each point in river is equal to or lower than the
        last'''
        celevation = 1.0
        for r in river:
            rx, ry = r
            relevation = self.heightmap[rx, ry]
            if relevation <= celevation:
                celevation = relevation
            elif relevation > celevation:
                self.heightmap[rx, ry] = celevation
        return river


    def riverErosion(self, river):
        '''Simulate erosion in heightmap based on river path.
            * current location must be equal to or less than previous location
            * riverbed is carved out by % of volume/flow
            * sides of river are also eroded to slope into riverbed.
            '''
        # erosion of riverbed itself
        maxElevation = 1.0
        minElevation = 0.0
        for r in river:
            rx, ry = r
            if self.heightmap[rx, ry] < maxElevation:
                maxElevation = self.heightmap[rx, ry]
            minElevation = maxElevation * 0.99
            maxElevation = random.uniform(minElevation, maxElevation)
            self.heightmap[rx, ry] = maxElevation

        # erosion around river, create river valley
        for r in river:
            rx, ry = r
            radius = 2
            for x in range(rx - radius, rx + radius):
                for y in range(ry - radius, ry + radius):
                    if not self.wrap and utilities.outOfBounds([x, y], self.size):  # ignore edges of map
                        continue
                    x, y = overflow(x, self.worldW), overflow(y, self.worldH)
                    curve = 1.0
                    if [x, y] == [0, 0]:  # ignore center
                        continue
                    if [x, y] in river:  # ignore river itself
                        continue
                    if self.heightmap[x, y] <= self.heightmap[rx, ry]:  # ignore areas lower than river itself
                        continue
                    if not utilities.inCircle(radius, rx, ry, x, y):  # ignore things outside a circle
                        continue

                    adx, ady = math.fabs(rx - x), math.fabs(ry - y)
                    if adx == 1 or ady == 1:
                        curve = 0.2
                    elif adx == 2 or ady == 2:
                        curve = 0.05

                    diff = self.heightmap[rx, ry] - self.heightmap[x, y]
                    newElevation = self.heightmap[x, y] + (diff * curve)
                    if newElevation <= self.heightmap[rx, ry]:
                        print 'newElevation is <= than river, fix me...'
                        newElevation = self.heightmap[x, y]
                    self.heightmap[x, y] = newElevation
        return

    def riverMapUpdate(self, river):
        '''Update the rivermap with the rainfall that is to become the waterflow'''
        isSeed = True
        px, py = (0, 0)
        for x, y in river:
            if isSeed:
                self.riverMap[x, y] = self.waterFlow[x, y]
                isSeed = False
            else:
                self.riverMap[x, y] = self.rainMap[x, y] + self.riverMap[px, py]
            px, py = x, y


    def findQuickPath(self, river):
        # Water flows based on cost, seeking the highest elevation difference
        # highest positive number is the path of least resistance (lowest point)
        # Cost
        # *** 1,0 ***
        # 0,1 *** 2,1
        # *** 1,2 ***
        x, y = river
        newPath = []
        lowestElevation = self.heightmap[x, y]
        # lowestDirection = [0, 0]

        for dx, dy in constants.DIR_ALL:
            tempDir = [x + dx, y + dy]
            tx, ty = tempDir

            if not self.wrap and utilities.outOfBounds(tempDir, self.size):
                continue

            tx, ty = overflow(tx, self.worldW), overflow(ty, self.worldH)      

            elevation = self.heightmap[tx, ty]
            
            # print river, direction, tempDir, elevation, direction[0], direction[1]

            if elevation < lowestElevation:
                if utilities.outOfBounds(tempDir, self.size):
                    #print "Lower OOB:",tempDir, "Corrected:", tx, ty
                    pass          
                lowestElevation = elevation
                newPath = [tx,ty]

        # print newPath, lowestDirection, elevation
        # sys.exit()

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
        isWrapped = False
        wrapped = []

        while notFound and currentRadius <= maxRadius:
            for cx in range(-currentRadius, currentRadius + 1):
                for cy in range(-currentRadius, currentRadius + 1):
                    rx, ry = x + cx, y + cy
                    
                    # are we within bounds?
                    if not self.wrap and utilities.outOfBounds([rx, ry], self.size):
                        continue     

                    # are we within a circle?
                    if not utilities.inCircle(currentRadius, x, y, rx, ry):
                        continue
                    
                    rx, ry = overflow(rx, self.worldW), overflow(ry, self.worldH)

#                    if utilities.outOfBounds([x+cx, y+cy], self.size):
#                        print "Fixed:",x ,y,  rx, ry

                    elevation = self.heightmap[rx, ry]
                    if elevation < lowestElevation: # have we found a lower elevation?
                        lowestElevation = elevation
                        destination = [rx, ry]
                        notFound = False
                        if utilities.outOfBounds([x+cx, y+cy], self.size):
                            wrapped.append(destination)                        

            currentRadius += 1
            
        if destination in wrapped:
            isWrapped = True
#            print "Wrapped lower elevation found:", rx, ry, "!"
        return isWrapped, destination
    
#### experimental code ####
    def simulateFloodi(self, x, y, elevation):
        '''Flood fill area based on elevation.
        The recursive algorithm. Starting at x and y, changes and marks any
        adjacent area that is under the elevation.'''

        # are we in bounds of world
        if utilities.outOfBounds({'x': x, 'y': y}, self.size):
            return

        # Base case. If the current [x, y] elevation is greater then do nothing.
        if self.heightmap[x, y] > elevation:
            return

        # Flood area and mark on map
        self.lakeMap[x, y] = 1
        print 'lake at: ', x, y

        # Recursive calls.
        self.simulateFlood(x - 1, y, elevation)  # left
        self.simulateFlood(x, y - 1, elevation)  # up
        self.simulateFlood(x + 1, y, elevation)  # right
        self.simulateFlood(x, y + 1, elevation)  # down

    def simulateFlood(self, x, y, elevation):
        '''Flood fill area based on elevation.
        The iterative algorithm. Starting at x and y, changes and marks any
        adjacent area that is under the elevation.'''

        theStack = [(x, y)]

        while len(theStack) > 0:
            x, y = theStack.pop()

            # are we in bounds of world
            if utilities.outOfBounds({'x': x, 'y': y}, self.size):
                continue

            # Base case. If the current [x, y] elevation is greater then do nothing.
            if self.heightmap[x, y] > elevation:
                continue

            # Flood area and mark on map
            self.lakeMap[x, y] = 1
            print 'lake at: ', x, y

            theStack.append((x - 1, y))  # left
            theStack.append((x, y - 1))  # up
            theStack.append((x + 1, y))  # right
            theStack.append((x, y + 1))  # down



    def isRiverNearby(self, radius, tryX, tryY):
        ''' return true if there is a river in the range of radius from
        source '''
        for x in range(-radius, radius + 1):
            for y in range(-radius, radius + 1):

                # are we within bounds?
                if utilities.outOfBounds({'x': tryX + x, 'y': tryY + y}, self.size):
                    continue

                # are we within a circle?
                if not utilities.inCircle(radius, tryX, tryY, tryX + x, tryY + y):
                    continue

                # found a river?
                if self.riverMap[tryX + x, tryY + y] > 0.0:
                    return True

        # no river found
        return False

    def findClosestSea(self, river):
        '''Try to find the closest sea by avoiding watersheds, the returned
        value should be a point in sea itself '''

        radius = 1
        while radius < self.worldW:

            for x in range(-radius, radius + 1):
                for y in range(-radius, radius + 1):
                    # verify that we do not go over the edge of map
                    if river.x + x >= 0 and river.y + y >= 0 and \
                    river.x + x < self.worldW and river.y + y < self.worldH:

                        # check that we are in circle
                        if not self.in_circle(river.x, river.y, radius, river.x + x, river.y + y):
                            continue

                        elevation = self.heightmap[river.x + x, river.y + y]
                        # if elevation > BIOME_ELEVATION_MOUNTAIN:
                        #     break # we hit the watershed, do not continue

                        if elevation < constants.WGEN_SEA_LEVEL:
                            # possible sea, lets check it out...
                            # is the spot surrounded by sea?
                            isSea = True
                            seaRange = 4
                            for i in range(-seaRange, seaRange + 1):
                                for j in range(-seaRange, seaRange + 1):
                                    if river.x + x + i >= 0 and river.y + y + j >= 0 and \
                                    river.x + x + i < self.worldW and river.y + y + j < self.worldH:
                                        if self.heightmap[river.x + x + i, river.y + y + j] > constants.WGEN_SEA_LEVEL:
                                            isSea = False

                            if isSea:
                                print "River at source:", river.x, river.y, " found the sea at: ", river.x + x, river.y + y
                                return {'x': river.x + x, 'y': river.y + y}

            radius += 1  # increase searchable area

        print "Could not find sea."
        return {}

if __name__ == '__main__':
    print "hello!"
