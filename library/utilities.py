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
import sys

def inCircle(radius, center_x, center_y, x, y):
    squareDist = ( (center_x - x) ** 2 + (center_y - y) ** 2 )
    return squareDist <= radius ** 2

def normalize(data, newMin=0.0, newMax=1.0):
    # compress the range while maintaining ratio
    oldMin = sys.float_info.max; oldMax = sys.float_info.min;
    width,height = data.shape
    for x in xrange(0,width):
        for y in xrange(0,height):
            if data[x,y] < oldMin:
                oldMin = data[x,y]
            if data[x,y] > oldMax:
                oldMax = data[x,y]
    for x in xrange(0,width):
        for y in xrange(0,height):
            data[x,y] = (((data[x,y] - oldMin) * (newMax-newMin)) / (oldMax-oldMin)) + newMin    
    return data

def radialGradient( size, invert=False ):
      import numpy
      width, height = size
      gradient = numpy.zeros(( size ))
      center_x, center_y = [width/2, height/2]
      for x in xrange( width ):
          for y in xrange( height ):
              squareDist = ( (center_x - x) ** 2 + (center_y - y) ** 2 )
              if invert:
                  gradient[x,y] = ~squareDist
              else:
                  gradient[x,y] = squareDist
      return normalize(gradient)