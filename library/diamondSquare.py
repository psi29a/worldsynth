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

#from numpy import *
from random import gauss,random,uniform
from numpy import *

def avg(*args):
    return sum(args)/len(args)    

class DSAv3():
    def __init__(self, size, roughness=0.5, scale=10.0, deviation=5.0, iterations= 10):
        ''' Create our initial heightmap '''
        self.size = size
        width = height = self.size + 1
        import numpy
        self.space = zeros((width,height))
    
    def randomHeightGen(self, height):
        ''' Random uniform distribution based on on min/max '''
        noise_min = -1.0
        noise_max = 1.0
        return uniform(noise_min*2**-height, noise_max*2**-height)
    
    def run(self, planet, seaLevel):
        ''' Square Diamond Algo '''
        corner = self.randomHeightGen(0)
        self.space[0,0] = corner
        self.space[0,-1] = corner
        self.space[-1,0] = corner
        self.space[-1,-1] = corner
                
        x_max,y_max = self.space.shape
        x_min = y_min = 0
        x_max -= 1; y_max -= 1
    
        side = x_max
        squares = 1
        i = 0
    
        while side > 1:
            for x in range(squares):
                for y in range(squares):
                    #Locations
                    x_left = x*side
                    x_right = (x+1)*side
                    y_top = y*side
                    y_bottom = (y+1)*side
    
                    dx = side/2
                    dy = side/2
    
                    xm = x_left + dx
                    ym = y_top + dy
    
                    #Diamond step- create center avg for each square
                    self.space[xm,ym] = avg(self.space[x_left, y_top],
                    self.space[x_left, y_bottom],
                    self.space[x_right, y_top],
                    self.space[x_right, y_bottom])
                    self.space[xm,ym] += self.randomHeightGen(i)
    
                    #Square step- create squares for each diamond
                    #Top Square
                    if (y_top - dy) < y_min:
                        temp = y_max - dy
                    else:
                        temp = y_top - dy
                    self.space[xm,y_top] = avg(self.space[x_left,y_top],
                                          self.space[x_right,y_top],
                                          self.space[xm,ym],
                                          self.space[xm,temp])
                    self.space[xm,y_top] += self.randomHeightGen(i)
    
                    #Top Wrapping
                    if y_top == y_min:
                        self.space[xm,y_max] = self.space[xm,y_top]
    
                    #Bottom Square
                    if (y_bottom + dy) > y_max:
                        temp = y_top + dy
                    else:
                        temp = y_bottom - dy
                    self.space[xm, y_bottom] = avg(self.space[x_left,y_bottom],
                                              self.space[x_right,y_bottom],
                                              self.space[xm,ym],
                                              self.space[xm,temp])
                    self.space[xm, y_bottom] += self.randomHeightGen(i)
    
                    #Bottom Wrapping
                    if y_bottom == y_max:
                        self.space[xm,y_min] = self.space[xm,y_bottom]
    
                    #Left Square
                    if (x_left - dx) < x_min:
                        temp = x_max - dx
                    else:
                        temp = x_left - dx
                    self.space[x_left, ym] = avg(self.space[x_left,y_top],
                                            self.space[x_left,y_bottom],
                                            self.space[xm,ym],
                                            self.space[temp,ym])
                    self.space[x_left, ym] += self.randomHeightGen(i)
    
                    #Left Wrapping
                    if x_left == x_min:
                        self.space[x_max,ym] = self.space[x_left,ym]
    
                    #Right Square
                    if (x_right + dx) > x_max:
                        temp = x_min + dx
                    else:
                        temp = x_right + dx
                    self.space[x_right, ym] = avg(self.space[x_right,y_top],
                                             self.space[x_right,y_bottom],
                                             self.space[xm,ym],
                                             self.space[temp,ym])
                    self.space[x_right, ym] += self.randomHeightGen(i)
    
                    #Right Wrapping
                    if x_right == x_max:
                        self.space[x_min,ym] = self.space[x_right,ym]
    
            #Refine the pass
            side /= 2
            squares *= 2
            i += 1
            print "Pass {0} complete.".format(i)
            self.heightmap = self.space
        
        # trim up heightmap to be power of 2
        self.heightmap = delete(self.heightmap,1,0)
        self.heightmap = delete(self.heightmap,1,1)        
        
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
                    
        
                

class DSAv2():
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
