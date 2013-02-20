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

import math, random, constants
from numpy import zeros
from PySide import QtGui

class Weather():
    def __init__( self, heightmap = zeros( 1 ), temperature = zeros( 1 ) ):
        self.heightmap = heightmap
        self.temperature = temperature

    def run( self, sb = None ):
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
        self.erosionMap = zeros( ( worldW, worldH ) )
        worldWindDir = random.randint( 0, 360 )
        theta1 = worldWindDir * constants.WIND_PARITY + constants.WIND_OFFSET
        theta2 = 180 - 90 - ( worldWindDir * constants.WIND_PARITY + constants.WIND_OFFSET )
        sinT1 = math.sin( theta1 )
        sinT2 = math.sin( theta2 )
        mapsqrt = math.sqrt( worldW * worldW + worldH * worldH )
        rainAmount = ( ( rainFall * mapsqrt ) / constants.WGEN_WIND_RESOLUTION ) * constants.WGEN_RAIN_FALLOFF
        rainMap = zeros( ( worldW, worldH ) )
        rainMap.fill( rainAmount )

        # cast wind and rain
        for d in xrange( r , -1, -constants.WGEN_WIND_RESOLUTION ):
            windx = int( d * sinT1 )
            windy = int( d * sinT2 )

            # continue (next d) if above are bigger than our map size
            if math.fabs( windx ) > worldW or math.fabs( windy ) > worldH:
                continue # do no more processing, go to next value

            # calculate our range to save cpu cycles
            if windx < 0:
                xBegin = int( math.fabs( windx ) )
            else:
                xBegin = 0

            if windy < 0:
                yBegin = int( math.fabs( windy ) )
            else:
                yBegin = 0

            xEnd = worldW - windx
            if xEnd > worldW:
                xEnd = worldW

            yEnd = worldH - windy
            if yEnd > worldH:
                yEnd = worldH

            #print windx, xBegin, xEnd#windy, yBegin
            #print windy, yBegin, yEnd

            for x in xrange( xBegin, xEnd ):
                windxX = windx + x

                for y in xrange( yBegin, yEnd ):
                    windyY = windy + y

                    # set our wind
                    windz = self.heightmap[windxX , windyY ]
                    self.windMap[x, y] = max( self.windMap[x, y] * constants.WGEN_WIND_GRAVITY, windz )

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
            #break

            if sb != None:
                progress.setValue( progressValue )
                progressValue += constants.WGEN_WIND_RESOLUTION
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
