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

import math, random
from numpy import *
from progressbar import ProgressBar, Percentage, ETA
from constants import *

class WindAndRain():
    def __init__(self, heightmap=zeros(1), temperature=zeros(1)):
        self.heightmap = heightmap
        self.temperature = temperature

    def run(self):
        # setup or local variables
        rainFall = 1.0
        worldW = len(self.heightmap)
        worldH = len(self.heightmap[0])
        self.windMap = zeros((worldW,worldH))
        self.rainMap = zeros((worldW,worldH))
        worldWindDir = random.randint(0, 360)
        r = math.sqrt(worldW*worldW + worldH*worldH)
        theta1 = worldWindDir * WIND_PARITY + WIND_OFFSET
        theta2 = 180 - 90 - (worldWindDir * WIND_PARITY + WIND_OFFSET)
        sinT1 = math.sin(theta1)
        sinT2 = math.sin(theta2)
        mapsqrt = math.sqrt(worldW*worldW + worldH*worldH)
        rainAmount = ((rainFall * mapsqrt) / WGEN_WIND_RESOLUTION) * WGEN_RAIN_FALLOFF
        rainMap = zeros((worldW,worldH))
        rainMap.fill(rainAmount)

        # cast wind and rain
        widgets = ['Generating wind and rain: ', Percentage(), ' ', ETA() ]
        pbar = ProgressBar(widgets=widgets, maxval=int(r))
        for d in range(int(r),-1,-WGEN_WIND_RESOLUTION):
            windx = d * sinT1
            windy = d * sinT2

            for x in range(0,worldW):
                for y in range(0,worldH):
                    if (int(windx + x) > -1) and (int(windy + y) > -1):
                        if (int(windx + x) < (worldW)) and (int(windy + y) < (worldH)):

                            # set our wind
                            windz = self.heightmap[int(windx+x),int(windy+y)]
                            self.windMap[x,y] = max(self.windMap[x,y] * WGEN_WIND_GRAVITY, windz)

                            # calculate how much rain is remaining
                            rainRemaining = rainMap[x,y] / rainAmount * (1.0-(self.temperature[x,y]/2.0))

                            # calculate our rainfall
                            rlost = (self.windMap[x,y]) * rainRemaining
                            if rlost < 0:
                                rlost = 0
                            rainMap[x,y] = rainMap[x,y] - rlost
                            if rainMap[x,y] <= 0:
                                rainMap[x,y] = 0

                            self.rainMap[int(windx+x),int(windy+y)] = rlost

            pbar.update(int(r)-d)
        pbar.finish()

if __name__ == '__main__':
    heightMap = zeros((128,128))
    tempMap = zeros((128,128))
    warObject = WindAndRain(heightMap,tempMap)
    warObject.run()
