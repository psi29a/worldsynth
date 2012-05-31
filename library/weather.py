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
from PySide import QtGui
from constants import *

class Weather():
    def __init__( self, heightmap = zeros( 1 ), temperature = zeros( 1 ) ):
        self.heightmap = heightmap
        self.temperature = temperature

    def run( self, sb = None):
        # setup or local variables
        rainFall = 1.0
        worldW = len( self.heightmap )
        worldH = len( self.heightmap[0] )
        r = int( math.sqrt( worldW * worldW + worldH * worldH ) )
        if sb != None:
            progressValue = 0
            progress = QtGui.QProgressBar()
            progress.setRange( 0, r )
            sb.addPermanentWidget( progress )
            progress.setValue( 0 )             
        self.windMap = zeros( ( worldW, worldH ) )
        self.rainMap = zeros( ( worldW, worldH ) )
        worldWindDir = random.randint( 0, 360 )
        theta1 = worldWindDir * WIND_PARITY + WIND_OFFSET
        theta2 = 180 - 90 - ( worldWindDir * WIND_PARITY + WIND_OFFSET )
        sinT1 = math.sin( theta1 )
        sinT2 = math.sin( theta2 )
        mapsqrt = math.sqrt( worldW * worldW + worldH * worldH )
        rainAmount = ( ( rainFall * mapsqrt ) / WGEN_WIND_RESOLUTION ) * WGEN_RAIN_FALLOFF
        rainMap = zeros( ( worldW, worldH ) )
        rainMap.fill( rainAmount )        

        # cast wind and rain
        for d in xrange( r , -1, -WGEN_WIND_RESOLUTION ):
            windx = int( d * sinT1 )
            windy = int( d * sinT2 )

            # continue if above are bigger than our map size
            if math.fabs(windx) > worldW or math.fabs(windy) > worldH:
                continue

            # calculate our range to save cpu cycles
            if windx < 0:
                xBegin = int(math.fabs(windx))
            else:
                xBegin = 0
                
            if windy < 0:
                yBegin = int(math.fabs(windy))
            else:
                yBegin = 0
            
            xEnd = worldW - windx
            if xEnd > worldW:
                xEnd = worldW

            yEnd = worldH - windy
            if yEnd > worldH:
                yEnd = worldH
            
            #print windx, xBegin, xEnd#windy, yBegin
            print windy, yBegin, yEnd
            
            
            for x in xrange( xBegin, xEnd ):
                windxX = windx + x
                for y in xrange( yBegin, worldH ):
                    windyY = windy + y
                    if windyY > -1 and windyY < worldH:
                        
                        # set our wind
                        windz = self.heightmap[windxX , windyY ]
                        self.windMap[x, y] = max( self.windMap[x, y] * WGEN_WIND_GRAVITY, windz )

                        # calculate how much rain is remaining
                        rainRemaining = rainMap[x, y] / rainAmount * ( 1.0 - ( self.temperature[x, y] / 2.0 ) )

                        # calculate our rainfall
                        rlost = self.windMap[x, y] * rainRemaining
                        if rlost < 0:
                            rlost = 0
                        self.rainMap[windxX , windyY ] = rlost
                        
                        # calculate rain loss due raining
                        rainMap[x, y] -= rlost
                        if rainMap[x, y] < 0:
                            rainMap[x, y] = 0
                        #print 'good', y, windy, windyY
                    else:
                        print 'crap', y, windy, windyY
            break

            if sb != None:
                progress.setValue( progressValue )
                progressValue += WGEN_WIND_RESOLUTION
        if sb != None:
            sb.removeWidget( progress )
            del progress

if __name__ == '__main__':
    heightMap = zeros( ( 128, 128 ) )
    tempMap = zeros( ( 128, 128 ) )    
    warObject = Weather( heightMap, tempMap )
    import cProfile
    cProfile.run( 'warObject.run()' )    
    #warObject.run()
