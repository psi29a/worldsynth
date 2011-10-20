#!/usr/bin/env python

import sys, random
from numpy import *
from progressbar import ProgressBar, Percentage, ETA
from constants import *


class Rivers():
    '''Creates and returns a rivermap'''

    def __init__(self, heightmap, rainmap):
        self.heightmap = heightmap
        self.rainmap = rainmap
        self.worldW = len(self.heightmap)
        self.worldH = len(self.heightmap[0])

        self.riverMap = zeros((self.worldW, self.worldH))

    def run(self):
        sources = self.riverSources()

        if sources:
            for source in sources:
                self.riverMap[source['x'], source['y']] = 0.1

                river = self.traceRiver(source)
                print 'River path:', river
                break
        else:
            print 'No estuaries...'

    def traceRiver(self, source):
        path = []

        stopChance = 0.05

        # find our initial direction
        radius = 1
        directions = []
        for x in range(-radius, radius+1):
            for y in range(-radius, radius+1):

                if self.heightmap[source['x']+x, source['y']+y] <= WGEN_SEA_LEVEL:
                    continue

                if not x and not y:
                    continue

                directions.append([x, y])

        print directions
        sys.exit()

        while True:
            stop = random.random()

            if stop < stopChance:
                break
            else:
                stopChance += 0.05

        return path

    def riverSources(self):
        widgets = ['Finding estuaries: ', Percentage(), ' ', ETA()]
        pbar = ProgressBar(widgets=widgets, maxval=self.worldH*self.worldH)

        riverSourceList = []

        # iterate through map and mark river sources
        for x in range(1, self.worldW-1):
            for y in range(1, self.worldH-1):

                # rivers will go inland from sea level
                if self.heightmap[x, y] <= WGEN_SEA_LEVEL or \
                     self.heightmap[x, y] > WGEN_SEA_LEVEL + 0.001:
                    continue

                # less rivers in places with less rainfall

                # check for rivers in range
                if self.isRiverInRange(20, x, y):
                    continue

                if random.random() <= 0.25:
                    # chance of river source
                    riverSource = {'x': x, 'y': y}
                    print riverSource
                    riverSourceList.append(riverSource)


                pbar.update(x+y)
        pbar.finish()
        return riverSourceList

    def isRiverInRange(self, radius, tryX, tryY):
        for x in range(-radius, radius+1):
            for y in range(-radius, radius+1):

                # are we within bounds?
                if tryX+x >= 0 or tryY+y >= 0 or \
                    tryX+x < self.worldW or tryY+y < self.worldH:
                    continue

                # are we within a circle?
                if not self.inCircle(radius, tryX, tryY, tryX+x, tryY+y):
                    continue

                # found a river?
                if self.riverMap[tryX+x, tryY+y] > 0:
                    return True

        # no river found
        return False

    def inCircle(self, radius, center_x, center_y, x, y):
        square_dist = (center_x - x) ** 2 + (center_y - y) ** 2
        return square_dist <= radius ** 2
