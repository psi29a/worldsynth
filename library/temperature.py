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

import math, random, numpy
from PySide import QtGui
    
if __name__ == '__main__': # handle multiple entry points
    from constants import *
else:
    from .constants import *     

class Temperature():
    def __init__( self, heightmap, seaLevel, hemisphere = WGEN_HEMISPHERE_EQUATOR, resolution = TEMPERATURE_BAND_RESOLUTION):
        self.heightmap = heightmap
        self.hemisphere = hemisphere
        self.resolution = resolution
        self.worldW = len( self.heightmap )
        self.worldH = len( self.heightmap[0] )
        self.temperature = numpy.zeros( ( self.worldW, self.worldH ) )
        self.seaLevel = seaLevel / 100.0 # reduce to 0.0 - 1.0 range

    def run( self, sb = None ):
        # setup or local variables
        if sb != None:
            progressValue = 0
            progress = QtGui.QProgressBar()
            progress.setRange( 0, self.worldH / self.resolution )
            sb.addPermanentWidget( progress )
            progress.setValue( 0 )

        for i in range( 0, self.worldH, self.resolution ):
            if sb != None:
                progress.setValue( progressValue )
                progressValue += 1

            # Generate band
            bandy = i
            bandrange = 7

            if self.hemisphere == WGEN_HEMISPHERE_NORTH:
                    # 0, 0.5, 1
                    bandtemp = float( i ) / self.worldH
            elif self.hemisphere == WGEN_HEMISPHERE_EQUATOR:
                    # 0, 1, 0
                    if i < ( self.worldH / 2 ):
                        bandtemp = float( i ) / self.worldH
                    else:
                        bandtemp = 1.0 - float( i ) / self.worldH
                    bandtemp *= 2.0
            elif self.hemisphere == WGEN_HEMISPHERE_SOUTH:
                    # 1, 0.5, 0
                    bandtemp = 1.0 - float( i ) / self.worldH
            else:
                print("Whoops: no hemisphere chosen.")
                exit()

            #print bandtemp,i,self.worldH
            bandtemp = max( bandtemp, 0.075 )

            # Initialise at bandy and randomise direction
            direction = 1.0
            diradj = 1
            dirsin = random.randint( 1, 8 )
            band = numpy.zeros( self.worldW )
            for x in range( self.worldW ):
                band[x] = bandy
                band[x] += direction
                direction = direction + random.uniform( 0.0, math.sin( dirsin * x ) * diradj )
                if direction > bandrange:
                    diradj = -1
                    dirsin = random.randint( 1, 8 )
                if direction < -bandrange:
                    diradj = 1
                    dirsin = random.randint( 1, 8 )


            # create temperature map
            for x in range( self.worldW ):
                bandx = int( band[x] )
                for y in range(bandx+1, self.worldH ):
                    if self.heightmap[x, y] <= self.seaLevel: # typical temp at sea level
                            self.temperature[x, y] = bandtemp * 0.7
                    else: # typical temp at elevation
                            self.temperature[x, y] = bandtemp * ( 1.0 - ( self.heightmap[x, y] - self.seaLevel ) )

            #break # for profiling 
        if sb != None:
            sb.removeWidget( progress )
            del progress

if __name__ == '__main__':
    heightmap = numpy.zeros( ( 256, 256 ) )
    tempObject = Temperature( heightmap )
    #tempObject.run()
    import cProfile
    cProfile.run( 'tempObject.run()' )
    #print tempObject.temperature
