#!/usr/bin/env python

import math, random
from numpy import *
from progressbar import ProgressBar, Percentage, ETA
from constants import *

class Temperature():
    def __init__(self, heightmap=zeros(1), hemisphere=2):
        self.heightmap = heightmap
        self.hemisphere = hemisphere
        self.worldW = len(self.heightmap)
        self.worldH = len(self.heightmap[0])
        self.temperature = zeros((self.worldW,self.worldH))

    def run(self):
        # setup or local variables
        widgets = ['Generating temperature map: ', Percentage(), ' ', ETA() ]
        pbar = ProgressBar(widgets=widgets, maxval=self.worldH)
        for i in range(0, self.worldH+1, TEMPERATURE_BAND_RESOLUTION):

            # Generate band
            bandy = i
            bandrange = 7

            if self.hemisphere == WGEN_HEMISPHERE_NORTH:
                    # 0, 0.5, 1
                    bandtemp = float(i)/self.worldH
            elif self.hemisphere == WGEN_HEMISPHERE_EQUATOR:
                    # 0, 1, 0
                    if i < (self.worldH/2):
                        bandtemp = float(i)/self.worldH
                        bandtemp = bandtemp * 2.0
                    else:
                        bandtemp = 1.0 - float(i)/self.worldH
                        bandtemp = bandtemp * 2.0
            elif self.hemisphere == WGEN_HEMISPHERE_SOUTH:
                    # 1, 0.5, 0
                    bandtemp = 1.0 - float(i)/self.worldH
            else:
                print "Whoops: no hemisphere choosen."
                exit()

            #print bandtemp,i,self.worldH

            bandtemp = max(bandtemp, 0.075)

            # Initialise at bandy
            band = zeros(self.worldW)
            for x in range(0,self.worldW):
                band[x] = bandy

            # Randomise
            direction = 1.0
            diradj = 1
            dirsin = random.randint(1,8)
            for x in range (0,self.worldW):
                band[x] = band[x] + direction
                direction = direction + random.uniform(0.0, math.sin(dirsin*x)*diradj)
                if direction > bandrange:
                    diradj = -1
                    dirsin = random.randint(1,8)
                if direction < -bandrange:
                    diradj = 1
                    dirsin = random.randint(1,8)



            # create tempature map
            for x in range(0,self.worldW):
                for y in range(0,self.worldH):
                    if self.heightmap[x,y] < WGEN_SEA_LEVEL: # typical temp at sea level
                        if y > band[x]:
                            self.temperature[x,y] = bandtemp * 0.7
                    else: # typical temp at elevation
                        if y > band[x]:
                            self.temperature[x,y] = bandtemp * (1.0 - (self.heightmap[x,y]-WGEN_SEA_LEVEL))
            pbar.update(i)
        pbar.finish()

if __name__ == '__main__':
    heightmap = zeros((128,128))
    tempObject = Temperature(heightmap)
    tempObject.run()
    print tempObject.temperature
