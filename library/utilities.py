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
import numpy

def inCircle(radius, center_x, center_y, x, y):
    squareDist = ( (center_x - x) ** 2 + (center_y - y) ** 2 )
    return squareDist <= radius ** 2

def normalize(data, newMin=0.0, newMax=1.0):
    # compress the range while maintaining ratio
    oldMin = numpy.amin(data)
    oldMax = numpy.amax(data)
    orgShape = data.shape
    data = numpy.reshape(data, data.size)
    for x in xrange(data.size):
            data[x] = (((data[x] - oldMin) * (newMax-newMin)) / (oldMax-oldMin)) + newMin
    return numpy.reshape(data, orgShape)

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


def radialGradient( size, fitEdges=True, invert=True ):
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
  
def frameGradient ( size, border=.1 ):
    width, height = size
    gradient = numpy.ones(( size ))
    borderSize = int(width*border)
    gBorder = numpy.linspace(0.0,1.0,borderSize)
    
    for x in xrange(width):
        for y in xrange(borderSize):
            value = gBorder[y]
            
            # top and bottom
            gradient[x,y] = value
            gradient[x,abs(y-height)-1] = value
            
            # left
            if (gradient[y,x] > value):
                gradient[y,x] = value
            
    for x in xrange(width):
        for y in xrange(borderSize):
            value = gBorder[y]
            # right   
            if (gradient[abs(y-height)-1,x] > value):
                gradient[abs(y-height)-1,x] = value
                pass
            
    return gradient

def rollingParticleGradient( size, centerBias=True ):
    import random
    width, height = size
    gradient = numpy.ones(( size ))
    
    PARTICLE_ITERATIONS = 3000
    PARTICLE_LENGTH = 50
    EDGE_BIAS = 12
    OUTER_BLUR = 0.75
    INNER_BLUR = 0.88
    
    for iterations in xrange(PARTICLE_ITERATIONS):
        # Start nearer the center
        if centerBias:
            sourceX = int(random.random() * (width-(EDGE_BIAS*2)) + EDGE_BIAS)
            sourceY = int(random.random() * (height-(EDGE_BIAS*2)) + EDGE_BIAS)
        # Random starting location
        else:
            sourceX = int(random.random() * (width - 1))
            sourceY = int(random.random() * (height - 1))
                
        for length in xrange(PARTICLE_LENGTH):
            sourceX += round(random.random() * 2 - 1)
            sourceY += round(random.random() * 2 - 1)
                                                        
            if sourceX < 1 or sourceX > width -2 or sourceY < 1 or sourceY > height - 2:
                break
                
            hood = mooreNeighborhood(size, sourceX, sourceY);
                
            for i in xrange(len(hood)):
                x,y = hood[i]
                if gradient[x,y] < gradient[sourceX,sourceY]:
                    sourceX,sourceY = hood[i]
                    break
                            
            gradient[sourceX,sourceY] += 1

    return normalize(gradient)

def mooreNeighborhood(size, x, y):
    '''Get the Moore neighborhood (3x3, 8 surrounding tiles, minus the center tile).'''
    import random
    result = []
    width, height = size
    
    for a in xrange(-1,2):
        for b in xrange(-1, 2):
            if a or b:
                if x + a >= 0 and x + a < width and y + b >= 0 and y + b < height:
                    result.append([int(x + a), int(y + b)])

    # Return the neighborhood in no particular order
    random.shuffle(result)                        
    return result