#!/usr/bin/env python
#
# Sphere algorithm for heightmap generation based on the work here:
# url: http://freespace.virgin.net/hugo.elias/models/m_landsp.htm
# Original code written by Shea Kauffman
# Refactored and modified to to be generic by Bret Curtis

import Image, ImageDraw, ImageChops, ImageOps, ImageFilter
import random
import sys
from math import ceil
from numpy import *

class Sphere():
    def __init__( self, width, height ):
            self.percentWater = .70
            self.mapSize = width #width (same as height) in pixels
            self.maxSize = 1.40 # 1 to 5 How big should the slices be cut, smaller slices create more islands
            self.shape = 1.40 # 1 has round continents .5 is twice as tall as it is wide, 2.0 is twice as wide as tall
            self.driftRate = .70 # As the world ages how much slower does it drift. 1 creates a more textured world but takes longer
            self.roughness = 1 #High numbers make a world faster, with more "ridges", but also makes things less "smooth"
            self.filename = 'heightmap.bmp'
            self.heightmap = zeros( ( self.mapSize, self.mapSize ) )
            self.randType = random.uniform #change to alter variability
            self.xrand = lambda ms = self.mapSize * 3: int( self.randType( 0, ms ) )
            self.yrand = lambda ms = self.mapSize * 2: int( self.randType( 0 - ( ms / 2 ), ms ) )


    def normalizeImage( self, image ):
        image = image.filter( ImageFilter.BLUR )
        picture = ImageChops.blend( ImageOps.equalize( image ), image, .5 )
        return ImageChops.multiply( picture, picture )

    def normalizeArray( self, object ):
        xArray,yArray = where(object > 1.0)
        gtone = zip(xArray,yArray)
        for x,y in gtone:
            object[x,y] = 1
        return object

    def drawPieSlices( self, oval, orig, action ):
        fl = action[1]
        img = Image.new( 'L', ( self.mapSize * 2, self.mapSize ) )
        draw = ImageDraw.Draw( img )
        draw.pieslice( [oval[0], oval[1], self.mapSize * 4, oval[3]], 90, 270, fill = fl )
        del draw
        orig = action[0]( orig, img )
        img = Image.new( 'L', ( self.mapSize * 2, self.mapSize ) )
        draw = ImageDraw.Draw( img )
        draw.pieslice( [0 - oval[0], oval[1], oval[2] - self.mapSize * 2, oval[3]], 270, 90, fill = fl )
        del draw
        return action[0]( orig, img )

    def drawOval( self, oval, orig, action ):
        img = Image.new( 'L', ( self.mapSize * 2, self.mapSize ) )
        draw = ImageDraw.Draw( img )
        draw.ellipse( oval, fill = action[1] )
        del draw
        return action[0]( orig, img )

    def cutOval( self, orig, smallness = 1 ):
        smallness = smallness ** self.driftRate
        landAction = lambda: ( 
            ImageChops.add,
            ceil( self.randType( 1, self.roughness * smallness * ( self.percentWater ) ) )
            )
        seaAction = lambda: ( 
            ImageChops.subtract,
            ceil( self.randType( 1, self.roughness * smallness * ( 1.0 - self.percentWater ) ) )
            )
        action = seaAction() if random.random() < self.percentWater else landAction()
        oval = [self.xrand( self.mapSize * 2 ), self.yrand( self.mapSize ), 1, 1] #x,y,x,y
        oval[2] = int( oval[0] + ( self.mapSize * self.maxSize * self.shape ) * smallness )
        oval[3] = int( oval[1] + ( self.mapSize * self.maxSize ) * smallness )
        if oval[2] > self.mapSize * 2: #if x values cross our border, we needto wrap
            ret = self.drawPieSlices( oval, orig, action )
        else:
            ret = self.drawOval( oval, orig, action )
        return ret

    def highestPointOnSphere( self, sphere ):
        ex, ey = sphere.getextrema()
        return ex / 255.0 if self.percentWater > .5 else 1 - ( ey / 255.0 )

    def createSphere( self ):
        sphere = Image.new( 'L', ( self.mapSize, self.mapSize ) )
        img = ImageDraw.Draw( sphere )
        baseline = ( 256 * ( 1.0 - ( self.percentWater ) ) )
        img.rectangle( [0 - self.mapSize, 0, self.mapSize * 4, self.mapSize], fill = baseline )
        del img
        return sphere

    def run( self, globe = True, seaLevel = 0.25, displayInterval = 50 ):
        sphere = self.createSphere()
        extrema = self.highestPointOnSphere( sphere )
        while extrema > self.driftRate / ( self.roughness * 10 * self.maxSize ):
            sphere = self.cutOval( sphere, extrema )
            extrema = self.highestPointOnSphere( sphere )

        sphere = self.normalizeImage( sphere ) # normal image
        self.heightmap = array( sphere.getdata(), float ) #convert image to numpy array
        self.heightmap = self.heightmap.reshape( self.mapSize, self.mapSize ) / 100
        self.heightmap = self.normalizeArray( self.heightmap )
        del sphere

if __name__ == '__main__':
    sphere = Sphere(512,512)
    import cProfile
    cProfile.run( 'sphere.run()' )

