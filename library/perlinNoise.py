#!/usr/bin/python
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
import numpy, utilities
from noise.perlin import SimplexNoise
from noise import snoise2

class Perlin():
    def __init__( self, size ):
        self.width, self.height = size
        self.heightmap = None
        
    def run( self ):
        noiseMap = numpy.zeros((self.width, self.height))
        
        # pure python version
        sn = SimplexNoise(period = self.width)
        persistance = 0.5
        octaves = [1, 2, 4, 8, 16]
        for octave in octaves:
            freq = 16.0 * octave
            for y in xrange(self.height):
                for x in xrange(self.width):
                    fn = sn.noise2( x/freq, y/freq )
                    noiseMap[x,y] += fn * persistance
            persistance *= 2

#        octaves = 5
#        freq = 16.0 * octaves
#        for y in xrange(self.height):
#            for x in xrange(self.width):
#                fn = snoise2(x / freq, y / freq, octaves=octaves, persistence=0.5, lacunarity=2.0, repeatx=self.width, repeaty=self.height, base=0.0)
#                noiseMap[x,y] = fn
        
        print noiseMap
        #noiseMap = numpy.gradient(noiseMap).shape((self.width, self.height))
        #print noiseMap
        self.heightmap = noiseMap
        #print self.heightmap        

# runs the program
if __name__ == '__main__':
    perlin = Perlin((512,512))
    import cProfile
    cProfile.run( 'perlin.run()' )    