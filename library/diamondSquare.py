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
# A simple implementation of the diamond-square fractal algorithm for
# random terrain generation.
#   depth - level of detail of terrain, where grid size is 2^depth+1
#   roughness - a roughness constant for how rough the terrain should be
#   scale - a scaling factor for the maximum y height of the geometry

from numpy import *
from random import gauss,random

class DSA():
    def __init__(self, size, roughness=0.5, scale=10.0, deviation=5.0, iterations= 10):
        # initialise arguments to constructor
        self.iterations = iterations
        self.seed = float(scale)
        self.deviation = float(deviation)
        self.roughness = float(roughness) / 10.0
        self.size = size + 1
        self.heightmap = zeros((self.size, self.size))
            
    def run(self, globe = True, sealevel = 0.25):
        self.heightmap[0][0] = gauss(self.seed, self.deviation)
        self.heightmap[0,self.size-1] = gauss(self.seed, self.deviation)
        self.heightmap[self.size-1][0] = gauss(self.seed, self.deviation)
        self.heightmap[self.size-1][self.size-1] = gauss(self.seed, self.deviation)
        
        # how many units (width/height) the array is
        size = self.size - 1
        deviation = self.deviation
        roughness = self.roughness
        
        for i in range(self.iterations):
        
            span = size / 2**(i+1)
            span2 = span*2
        
            for x in range(2**i):
                for y in range(2**i):
                    dx = x * span2
                    dy = y * span2
                
                    # diamond step
                    A = self.heightmap[dx][dy]
                    B = self.heightmap[dx + span2][dy]
                    C = self.heightmap[dx + span2][dy + span2]
                    D = self.heightmap[dx][dy + span2]
                    E = gauss(((A + B + C + D) / 4.0), deviation)
                    
                    if self.heightmap[dx + span][dy + span] == 0.0:
                        self.heightmap[dx + span][dy + span] = E
                        
                    # squared step
                    if self.heightmap[dx][dy + span] == 0.0:
                        self.heightmap[dx][dy + span] = gauss(((A + C + E) / 3.0), deviation) # F
                        
                    if self.heightmap[dx + span][dy] == 0.0:
                        self.heightmap[dx + span][dy] = gauss(((A + B + E) / 3.0), deviation) # G
                        
                    if self.heightmap[dx + span2][dy + span] == 0.0:
                        self.heightmap[dx + span2][dy + span] = gauss(((B + D + E) / 3.0), deviation) # H
                        
                    if self.heightmap[dx + span][dy + span2] == 0.0:
                        self.heightmap[dx + span][dy + span2] = gauss(((C + D + E) / 3.0), deviation) # I
                    
            deviation = deviation * (2**-roughness)

        # compress the range while maintaining ratio
        newMin = 0.0; newMax = 1.0;
        oldMin = 0.0; oldMax = 0.0
        for x in range(0,self.size):
            for y in range(0,self.size):
                if self.heightmap[x,y] < oldMin:
                    oldMin = self.heightmap[x,y]
                if self.heightmap[x,y] > oldMax:
                    oldMax = self.heightmap[x,y]
        for x in range(0,self.size):
            for y in range(0,self.size):
                self.heightmap[x,y] = (((self.heightmap[x,y] - oldMin) * (newMax-newMin)) / (oldMax-oldMin)) + newMin
                    
        # trim up heightmap to be power of 2
        self.heightmap = delete(self.heightmap,1,0)
        self.heightmap = delete(self.heightmap,1,1)

class DSAv1():
    #def __init__( self, depth=9, roughness=0.5, scale=1.0):
    def __init__(self, width, height, roughness=0.5, scale=10.0):
        # initialise arguments to constructor
        #self.depth = int(depth)
        self.width = width
        self.height = height
        self.depth = int(math.log(width,2))        
        self.roughness = float(roughness) / 10.0 
        self.scale = float(scale)
        self.size = (1 << self.depth)+1         # grid size, 2^depth+1
        self.heightmap = zeros((self.size,self.size))

        print self.roughness, self.scale

    # Iterative terrain deformer using classic diamond-square algorithm.
    def run(self, globe = True, sealevel = 0.25):
        # Seeds an initial random altitude for the four corners of the dataset.
        self.heightmap[0,0]                     = self.scale*(random.random()-self.roughness)
        self.heightmap[0,self.size-1]           = self.scale*(random.random()-self.roughness)
        self.heightmap[self.size-1,0]           = self.scale*(random.random()-self.roughness)
        self.heightmap[self.size-1,self.size-1] = self.scale*(random.random()-self.roughness)

        rough = self.roughness
        r = self.size-1

        # Diamond-square iterative implementation:
        for i in range(self.depth):
          s = r >> 1
          x = 0
          while ( x < self.size-1 ):
            y = 0
            while ( y < self.size-1 ):
              self.diamond( rough, x, y, r )
              y = y + r
            x = x + r

          if s > 0:
            x = 0
            while ( x < self.size ):
              y = (x + s) % r
              while ( y < self.size ):
                self.square( rough, x-s, y-s, r )
                y = y + r
              x = x + s
          rough = rough * self.roughness #0.5
          r = r >> 1

        # compress the range while maintaining ratio
        newMin = 0.0; newMax = 1.0;
        oldMin = 0.0; oldMax = 0.0
        for x in range(0,self.size):
            for y in range(0,self.size):
                if self.heightmap[x,y] < oldMin:
                    oldMin = self.heightmap[x,y]
                if self.heightmap[x,y] > oldMax:
                    oldMax = self.heightmap[x,y]
        for x in range(0,self.size):
            for y in range(0,self.size):
                self.heightmap[x,y] = (((self.heightmap[x,y] - oldMin) * (newMax-newMin)) / (oldMax-oldMin)) + newMin

        # trim up heightmap to be power of 2
        self.heightmap = delete(self.heightmap,1,0)
        self.heightmap = delete(self.heightmap,1,1)

    def diamond( self, c, x, y, step ):
        if step > 1:
            half=step/2
            avg = ( self.heightmap[x][y] +
                    self.heightmap[x][y+step] +
                    self.heightmap[x+step][y] +
                    self.heightmap[x+step][y+step] ) / 4
            h = avg + self.scale * c * (random.random()-self.roughness)
            self.heightmap[x+half][y+half] = h

    def square( self, c, x, y, step ):
        num=0
        avg=0.0
        half=step/2
        if ( x >= 0 ):
            avg=avg+self.heightmap[x][y+half]
            num=num+1
        if ( y >= 0 ):
              avg=avg+self.heightmap[x+half][y]
              num=num+1
        if ( x+step < self.size ):
              avg=avg+self.heightmap[x+step][y+half]
              num=num+1
        if ( y+step < self.size ):
              avg=avg+self.heightmap[x+half][y+step]
              num=num+1

        h = avg/num + self.scale * c * (random.random()-self.roughness)
        self.heightmap[x+half][y+half] = h

# runs the program
if __name__ == '__main__':
    dsa = DSA(512,512)
    import cProfile
    cProfile.run( 'dsa.run()' )
