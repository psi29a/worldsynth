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
import sys, numpy

def inCircle(radius, center_x, center_y, x, y):
    squareDist = ( (center_x - x) ** 2 + (center_y - y) ** 2 )
    return squareDist <= radius ** 2

def normalize(data, newMin=0.0, newMax=1.0):
    # compress the range while maintaining ratio
    width,height = data.shape
    oldMin = numpy.amin(data)
    oldMax = numpy.amax(data)    
    for x in xrange(0,width):
        for y in xrange(0,height):
            data[x,y] = (((data[x,y] - oldMin) * (newMax-newMin)) / (oldMax-oldMin)) + newMin    
    return data

def roof( data, limit ):
    xArray,yArray = numpy.where(data > limit)
    spikes = zip(xArray,yArray)
    for x,y in spikes:
        data[x,y] = limit
    return data

def floor( data, limit ):
    xArray,yArray = numpy.where(data < limit)
    spikes = zip(xArray,yArray)
    for x,y in spikes:
        data[x,y] = limit
    return data


def radialGradient( size, fitEdges=True, invert=False ):
    ''' Creates a radial gradient (half-sphere) to be used for masking images so
    that the edges have a curving sloop. You can specify the inverse as well as
    fitting to the edges or corners of a 2D array. '''
     
    width, height = size
    gradient = numpy.zeros(( size ))
    center_x, center_y = [width/2, height/2]
    midEdge = (center_x - center_x) ** 2 + (center_y - 0) ** 2
    for x in xrange( width ):
        for y in xrange( height ):
            squareDist = (center_x - x) ** 2 + (center_y - y) ** 2
            if invert:
                gradient[x,y] = ~squareDist
            else:
                gradient[x,y] = squareDist
    
    if fitEdges and invert: 
        gradient = floor(gradient, ~midEdge)
    elif fitEdges:
        gradient = roof(gradient, midEdge)
      
    return normalize(gradient)
  
def frameGradient ( size, border=.10 ):
    width, height = size
    gradient = numpy.zeros(( size ))
    borderSize = int(width*border)
    
    #top border
    target = 250
    beta = 1.0/target
    Y = numpy.random.exponential(beta, borderSize)
    Y = normalize(Y) #TODO: make normalize accept 1D arrays
    
    print Y
    
    for x in xrange(width):
        for y in xrange(0,borderSize):
            gradient[x,y] = 1
            
    print borderSize
    return gradient
    return normalize(gradient)
    