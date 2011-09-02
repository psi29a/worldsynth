#!/usr/bin/env python
#    Orographic effect:
#    - Warm, moist air carried in by wind
#    - Mountains forces air upwards, where it cools and condenses (rains)
#    - The leeward side of the mountain is drier and casts a "rain shadow".
#    
#    Wind is modelled here as a square of particles of area
#        worldW * worldH
#    and
#        Sqrt(worldW^2+worldH^2) away
#    The wind travels in direction of worldWinDir

from numpy import *
import math, random

class WindAndRain():
    def __init__(self, heightmap, temperature):
        self.heightmap = heightmap
        self.temperature = temperature
        self.rainFall = 1.0            
        self.worldW = len(self.heightmap)
        self.worldH = len(self.heightmap[0])
        self.windMap = empty((self.worldW,self.worldH))
        self.rainMap = empty((self.worldW,self.worldH))            
        self.worldWindDir = random.randint(0, 360) 
        self.WIND_OFFSET = 180
        self.WIND_PARITY = -1 # -1 or 1
        self.WGEN_WIND_RESOLUTION = 4 # 1 is perfect, higher = rougher
        self.WGEN_RAIN_FALLOFF = 0.2 # Default 0.2 - less for less rain, more for more rain
        self.WGEN_WIND_GRAVITY = 0.975

    def run(self):
        # setup or local variables
        r = math.sqrt(self.worldW*self.worldW + self.worldH*self.worldH)
        theta1 = self.worldWindDir * self.WIND_PARITY + self.WIND_OFFSET
        theta2 = 180 - 90 - (self.worldWindDir * self.WIND_PARITY + self.WIND_OFFSET)
        sinT1 = math.sin(theta1)
        sinT2 = math.sin(theta2)    
        windw = self.worldW
        windh = self.worldH
        mapsqrt = math.sqrt(WorldW*WorldW + WorldH*WorldH)
        
        # init wind and rain
        for x in range(0,windw):
            for y in range(0,windh):
                self.rainMap[x,y] = ((self.rainFall * mapsqrt) / WGEN_WIND_RESOLUTION) * WGEN_RAIN_FALLOFF

        # cast wind
        for d in range(r,0-1,-WGEN_WIND_RESOLUTION):
            windx = d * sinT1
            windy = d * sinT2
         
            for x in range(0,windw):
                for y in range(0,windh):
                    if (int(windx + x) > -1) and (int(windy + y) > -1):
                        if (int(windx + x) < (self.worldW)) and (int(windy + y) < (self.worldH)):
                        
                            windz = self.heightmap[ToInt(windx+x),ToInt(windy+y)]
                            self.windMap[x,y] = max(self.windMap[x,y] * self.WGEN_WIND_GRAVITY, windz)
                            
                            rainRemaining = self.rainMap[x,y] / (((rainfall * mapsqrt) / self.WGEN_WIND_RESOLUTION) * self.WGEN_RAIN_FALLOFF) * (1.0-(self.temperature[x,y]/2.0))
                            
                            rlost = self.windMap[x,y] * rainRemaining
                            if rlost < 0: 
                                rlost = 0
                            self.rainMap[x,y] = self.rainMap[x,y] - rlost                       
                            if self.rainMap[x,y] <= 0: 
                                self.rainMap[x,y] = 0
                             
                            self.windMap[int(windx+x),int(windy+y)] = wind[x,y]
                            self.rainMap[int(windx+x),int(windy+y)] = rlost
        
if __name__ == '__main__':
    warObject = WindAndRain()
    
  
    

    

