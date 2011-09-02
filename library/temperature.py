#!/usr/bin/env python

from numpy import *
import math, random

class Temperature():
    def __init__(self, heightmap, hemisphere):
        self.heightmap = heightmap
        self.hemisphere = hemisphere
        self.worldW = len(self.heightmap)
        self.worldH = len(self.heightmap[0])        
        self.temperature = empty((self.worldW,self.worldH))
        self.TEMPERATURE_BAND_RESOLUTION = 2 # 1 is perfect, higher = rougher
        self.WGEN_HEMISPHERE_NORTH   = 1 # export
        self.WGEN_HEMISPHERE_EQUATOR = 2 # export
        self.WGEN_HEMISPHERE_SOUTH   = 3 # export
        self.WGEN_SEA_LEVEL = 0.333   

    def run(self):
        # setup or local variables
        for i in range(0, self.worldH+1, self.TEMPERATURE_BAND_RESOLUTION):
            
            # Generate band
            bandy = i
            bandrange = 7
            
            if self.hemisphere == self.WGEN_HEMISPHERE_NORTH:
                    # 0, 0.5, 1
                    bandtemp = i/self.worldH
            elif self.hemisphere == self.WGEN_HEMISPHERE_EQUATOR:
                    # 0, 1, 0
                    if i < (self.worldH/2):
                        bandtemp = i/self.worldH
                        bandtemp = bandtemp * 2.0
                    else:
                        bandtemp = 1.0 - i/self.worldH
                        bandtemp = bandtemp * 2.0
            elif self.hemisphere == self.WGEN_HEMISPHERE_SOUTH:
                    # 1, 0.5, 0
                    bandtemp = 1.0 - i/self.worldH
            else:
                print "Whoops: no hemisphere choosen."
                exit()
            
            bandtemp = max(bandtemp, 0.075) 

            # Initialise at bandy
            band = empty(self.worldW)
            for x in range(0,self.worldW):
                band[x] = bandy
            
            # Randomise
            direction = 1.0
            diradj = 1
            dirsin = random.randint(1,8)         
            for x in range (0,self.worldW):
                band[x] = band[x] + direction
                direction = direction + random.uniform(0.0, sin(dirsin*x)*diradj)
                if direction > bandrange:
                    diradj = -1
                    dirsin = random.randint(1,8)
                elif direction < -bandrange:
                    diradj = 1
                    dirsin = random.randint(1,8)   
        
            # create tempature map       
            for x in range(0,self.worldW):
                for y in range(0,self.worldH):
                    if self.heightmap[x,y] < self.WGEN_SEA_LEVEL: # typical temp at sea level
                        if y > band[x]: 
                            self.temperature[x,y] = bandtemp * 0.7
                    else: # typical temp at elevation
                        if y > band[x]: 
                            self.temperature[x,y] = bandtemp * (1.0 - (self.heightmap[x,y]-self.WGEN_SEA_LEVEL)) 
        
if __name__ == '__main__':
    heightmap = empty((512,512))
    tempObject = Temperature(heightmap,1)
    print tempObject.temperature
    tempObject.run()
    print tempObject.temperature
    
  
    

    

