#!/usr/bin/env python

import math, random
from numpy import *
from PySide import QtGui
from constants import *

class Temperature():
    def __init__( self, heightmap = zeros( 1 ), hemisphere = 2, resolution = TEMPERATURE_BAND_RESOLUTION ):
        self.heightmap = heightmap
        self.hemisphere = hemisphere
        self.resolution = resolution
        self.worldW = len( self.heightmap )
        self.worldH = len( self.heightmap[0] )
        self.temperature = zeros( ( self.worldW, self.worldH ) )

    def run( self, sb = None ):
        # setup or local variables
        if sb != None:
            progressValue = 0
            progress = QtGui.QProgressBar()
            progress.setRange( 0, self.worldH / self.resolution )
            sb.addPermanentWidget( progress )
            progress.setValue( 0 )

        for i in xrange( 0, self.worldH, self.resolution ):
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
                print "Whoops: no hemisphere chosen."
                exit()

            #print bandtemp,i,self.worldH
            bandtemp = max( bandtemp, 0.075 )

            # Initialise at bandy and randomise direction
            direction = 1.0
            diradj = 1
            dirsin = random.randint( 1, 8 )
            band = zeros( self.worldW )
            for x in xrange( self.worldW ):
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
            for x in xrange( self.worldW ):
                bandx = int( band[x] )
                for y in xrange( self.worldH ):
                    if y > bandx:
                        if self.heightmap[x, y] < WGEN_SEA_LEVEL: # typical temp at sea level
                                temperature = bandtemp * 0.7
                        else: # typical temp at elevation
                                temperature = bandtemp * ( 1.0 - ( self.heightmap[x, y] - WGEN_SEA_LEVEL ) )
                        self.temperature[x, y] = temperature
                    #pass

            #break # for profiling 
        if sb != None:
            sb.removeWidget( progress )
            del progress

if __name__ == '__main__':
    heightmap = zeros( ( 256, 256 ) )
    tempObject = Temperature( heightmap )
    #tempObject.run()
    import cProfile
    cProfile.run( 'tempObject.run()' )
    #print tempObject.temperature
