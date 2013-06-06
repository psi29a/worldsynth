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

from random import uniform #,gauss,random
import numpy, sys

def avg(*args):
    return sum(args)/len(args)    

class DSA():
    def __init__(self, size):
        ''' Create our initial heightmap '''
        self.size = map(lambda x: x+1, size)
        self.heightmap = numpy.zeros(self.size)
        self.noise_min = -1.0
        self.noise_max = 1.0
        
    def randomHeightGen(self, i):
        ''' Random uniform distribution based on on min/max '''
        return uniform(self.noise_min*2**-i, self.noise_max*2**-i)
    
    def run(self):
        ''' Square Diamond Algo '''

        corner = self.randomHeightGen(0.0)
        self.heightmap[0,0]   = corner
        self.heightmap[0,-1]  = corner
        self.heightmap[-1,0]  = corner
        self.heightmap[-1,-1] = corner
                
        x_max,y_max = self.heightmap.shape
        x_min = y_min = 0
        x_max -= 1; y_max -= 1
    
        side = x_max
        squares = 1
        i = 0
    
        while side > 1:
            for x in xrange(squares):
                for y in xrange(squares):
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
                    self.heightmap[xm,ym] = avg(self.heightmap[x_left, y_top],
                    self.heightmap[x_left, y_bottom],
                    self.heightmap[x_right, y_top],
                    self.heightmap[x_right, y_bottom])
                    self.heightmap[xm,ym] += self.randomHeightGen(i)
    
                    #Square step- create squares for each diamond
                    #Top Square
                    if (y_top - dy) < y_min:
                        temp = y_max - dy
                    else:
                        temp = y_top - dy
                    self.heightmap[xm,y_top] = avg(self.heightmap[x_left,y_top],
                                          self.heightmap[x_right,y_top],
                                          self.heightmap[xm,ym],
                                          self.heightmap[xm,temp])
                    self.heightmap[xm,y_top] += self.randomHeightGen(i)
    
                    #Top Wrapping
                    if y_top == y_min:
                        self.heightmap[xm,y_max] = self.heightmap[xm,y_top]
    
                    #Bottom Square
                    if (y_bottom + dy) > y_max:
                        temp = y_top + dy
                    else:
                        temp = y_bottom - dy
                    self.heightmap[xm, y_bottom] = avg(self.heightmap[x_left,y_bottom],
                                              self.heightmap[x_right,y_bottom],
                                              self.heightmap[xm,ym],
                                              self.heightmap[xm,temp])
                    self.heightmap[xm, y_bottom] += self.randomHeightGen(i)
    
                    #Bottom Wrapping
                    if y_bottom == y_max:
                        self.heightmap[xm,y_min] = self.heightmap[xm,y_bottom]
    
                    #Left Square
                    if (x_left - dx) < x_min:
                        temp = x_max - dx
                    else:
                        temp = x_left - dx
                    self.heightmap[x_left, ym] = avg(self.heightmap[x_left,y_top],
                                            self.heightmap[x_left,y_bottom],
                                            self.heightmap[xm,ym],
                                            self.heightmap[temp,ym])
                    self.heightmap[x_left, ym] += self.randomHeightGen(i)
    
                    #Left Wrapping
                    if x_left == x_min:
                        self.heightmap[x_max,ym] = self.heightmap[x_left,ym]
    
                    #Right Square
                    if (x_right + dx) > x_max:
                        temp = x_min + dx
                    else:
                        temp = x_right + dx
                    self.heightmap[x_right, ym] = avg(self.heightmap[x_right,y_top],
                                             self.heightmap[x_right,y_bottom],
                                             self.heightmap[xm,ym],
                                             self.heightmap[temp,ym])
                    self.heightmap[x_right, ym] += self.randomHeightGen(i)
    
                    #Right Wrapping
                    if x_right == x_max:
                        self.heightmap[x_min,ym] = self.heightmap[x_right,ym]
    
            #Refine the pass
            side /= 2
            squares *= 2
            i += 1
            
        #trim up heightmap to be power of 2
        self.heightmap = numpy.delete(numpy.delete(self.heightmap,1,0),1,1) 

# runs the program
if __name__ == '__main__':
    dsa = DSA((512,512))
    import cProfile
    cProfile.run( 'dsa.run()' )
