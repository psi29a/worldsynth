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
import constants, utilities, numpy

class HeightMap():
    '''An heightmap generator with various backends'''
    def __init__( self, size, roughness = 0.5, islands = False ):
        self.size = size
        self.width, self.height = self.size
        self.roughness = roughness
        self.heightmap = None
        self.islands = islands

    def run(self, method = None):      
        if method == constants.HM_MDA:
            from midpointDisplacement import MDA            
            heightObject = MDA(self.size, self.roughness)
        elif method == constants.HM_DSA:
            from diamondSquare import DSA
            heightObject = DSA(self.size)
        elif method == constants.HM_SPH:
            from sphere import Sphere
            heightObject = Sphere(self.size, self.roughness)
        elif method == constants.HM_PERLIN:
            from perlinNoise import Perlin
            heightObject = Perlin(self.size)
        else:
            print "No method for generating heightmap found!"
        
        heightObject.run()
        self.heightmap = utilities.normalize(heightObject.heightmap)
        
        if self.islands:
            gradient = utilities.radialGradient(self.size, True, True)
            #gradient = utilities.rollingParticleGradient(self.size)
            self.heightmap = self.heightmap * gradient

        del heightObject
        
        #self.heightmap = utilities.rollingParticleGradient(self.size)
        print self.heightmap

    def landMassPercent( self ):
        return self.heightmap.sum() / ( self.width * self.height )

    def averageElevation( self ):
        return numpy.average( self.heightmap )

    def hasNoMountains( self ):
        if self.heightmap.max() > constants.BIOME_ELEVATION_MOUNTAIN:
            return False
        return True

    def landTouchesEastWest( self ):
        for x in range( 0, 1 ):
            for y in range( 0, self.height ):
                if self.heightmap[x, y] > constants.WGEN_SEA_LEVEL or \
                    self.heightmap[self.width - 1 - x, y] > constants.WGEN_SEA_LEVEL:
                    return True
        return False

    def landTouchesMapEdge( self ):
        result = False
        for x in range( 4, self.width - 4 ):
            if self.heightmap[x, 4] > constants.WGEN_SEA_LEVEL or self.heightmap[x, self.height - 4] > constants.WGEN_SEA_LEVEL:
                result = True
                break

        for y in range( 4, self.height - 4 ):
            if self.heightmap[4, y] > constants.WGEN_SEA_LEVEL or self.heightmap[self.width - 4, y] > constants.WGEN_SEA_LEVEL:
                result = True
                break

        return result