#!/usr/bin/python
import math, random, sys
from numpy import *
from PySide import QtGui
from constants import *
from midpointDisplacement import MDA
from diamondSquare import DSA
from sphere import Sphere

class HeightMap():
    '''An heightmap generator with various backends'''
    
    def __init__( self, width, height, roughness = 8 ):
        self.width = width
        self.height = height
        self.roughness = roughness
        self.heightmap = None

    def run(self, globe = False, seaLevel = WGEN_SEA_LEVEL, method = HM_MDA):
        if method == HM_MDA:
            heightObject = MDA(self.width, self.height, self.roughness)
        elif method == HM_DSA:
            heightObject = DSA(self.width, self.height)
        elif method == HM_SPH:
            heightObject = Sphere(self.width, self.height)
        else:
            print "No method for generating heightmap found!"
            
        heightObject.run(globe, seaLevel)
        self.heightmap = heightObject.heightmap

    def landMassPercent( self ):
        return self.heightmap.sum() / ( self.width * self.height )

    def averageElevation( self ):
        return average( self.heightmap )

    def hasNoMountains( self ):
        if self.heightmap.max() > BIOME_ELEVATION_MOUNTAIN:
            return False
        return True

    def landTouchesEastWest( self ):
        for x in range( 0, 1 ):
            for y in range( 0, self.height ):
                if self.heightmap[x, y] > WGEN_SEA_LEVEL or \
                    self.heightmap[self.width - 1 - x, y] > WGEN_SEA_LEVEL:
                    return True
        return False

    def landTouchesMapEdge( self ):
        result = False
        for x in range( 4, self.width - 4 ):
            if self.heightmap[x, 4] > WGEN_SEA_LEVEL or self.heightmap[x, self.height - 4] > WGEN_SEA_LEVEL:
                result = True
                break

        for y in range( 4, self.height - 4 ):
            if self.heightmap[4, y] > WGEN_SEA_LEVEL or self.heightmap[self.width - 4, y] > WGEN_SEA_LEVEL:
                result = True
                break

        return result            