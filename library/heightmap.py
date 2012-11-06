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
import math, random, sys
from numpy import *
from PySide import QtGui
from constants import *
from midpointDisplacement import MDA
from diamondSquare import DSAv3
from sphere import Sphere

class HeightMap():
    '''An heightmap generator with various backends'''
    
    def __init__( self, width, height, roughness, scale ):
        self.width = width
        self.height = height
        self.size = width
        self.roughness = roughness
        self.scale = scale
        self.heightmap = None

    def run(self, planet = False, seaLevel = WGEN_SEA_LEVEL, method = HM_MDA):
        if method == HM_MDA:
            heightObject = MDA(self.width, self.height, self.roughness, self.scale)
        elif method == HM_DSA:
            heightObject = DSAv3(self.size)
        elif method == HM_SPH:
            heightObject = Sphere(self.width, self.height)
        else:
            print "No method for generating heightmap found!"
            
        heightObject.run(planet, seaLevel)
        self.heightmap = heightObject.heightmap
        del heightObject

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