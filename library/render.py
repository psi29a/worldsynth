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
from constants import *
from PySide import QtGui
from PySide.QtGui import QImage

class Render():
    '''Transform the numpy data into a renderable image suitable for screen'''

    def __init__( self, world ):
        self.world = world
        for k in self.world:
            exec( 'self.' + k + ' = self.world[k]' )

        self.width = len( self.elevation )
        self.height = self.width
        self.image = QImage( self.width, self.height, QImage.Format_RGB32 )

    def hex2rgb( self, hexcolor ):
        r = ( hexcolor >> 16 ) & 0xFF;
        g = ( hexcolor >> 8 ) & 0xFF;
        b = hexcolor & 0xFF;
        return [r, g, b]

    def rgb2hex( self, rgb ):
        assert( len( rgb ) == 3 )
        return '#%02x%02x%02x' % rgb

    def convert( self, mapType ):

        background = []
        if mapType == "heightmap":
            heightmap = self.elevation * 255 # convert to greyscale
            for x in xrange( self.width ):
                for y in xrange( self.height ):
                    gValue = heightmap[x, y]
                    self.image.setPixel( x, y, QtGui.QColor( gValue, gValue, gValue ).rgb() )

        elif mapType == "sealevel":
            for x in xrange( self.width ):
                for y in xrange( self.height ):
                    elevation = self.elevation[x, y]
                    gValue = elevation * 255
                    if elevation <= WGEN_SEA_LEVEL: # sealevel
                        self.image.setPixel( x, y, QtGui.QColor( 0, 0, gValue ).rgb() )
                    else:
                        self.image.setPixel( x, y, QtGui.QColor( gValue, gValue, gValue ).rgb() )

        elif mapType == "elevation":
            for x in xrange( self.width ):
                for y in xrange( self.height ):
                    elevation = self.elevation[x, y]
                    if elevation <= WGEN_SEA_LEVEL: # sealevel
                        self.image.setPixel( x, y, QtGui.QColor( 0, 0, 128 ).rgb() )
                    elif elevation < BIOME_ELEVATION_HILLS: # grasslands
                        self.image.setPixel( x, y, QtGui.QColor( 128, 255, 0 ).rgb() )
                    elif elevation < BIOME_ELEVATION_MOUNTAIN_LOW: # mountains
                        self.image.setPixel( x, y, QtGui.QColor( 90, 128, 90 ).rgb() )
                    else:
                        self.image.setPixel( x, y, QtGui.QColor( 255, 255, 255 ).rgb() )

        elif mapType == "heatmap":
            for x in xrange( self.width ):
                for y in xrange( self.height ):
                    gValue = self.temperature[x, y]
                    self.image.setPixel( x, y, QtGui.QColor( gValue * 255, gValue * 128, ( 1 - gValue ) * 255 ).rgb() )

        elif mapType == "rawheatmap":
            temperature = self.temperature * 255 # convert to greyscale
            for x in xrange( self.width ):
                for y in xrange( self.height ):
                    gValue = temperature[x, y]
                    self.image.setPixel( x, y, QtGui.QColor( gValue, gValue, gValue ).rgb() )

        elif mapType == 'windmap':
            for x in xrange( self.width ):
                for y in xrange( self.height ):
                    gValue = self.wind[x, y]
                    self.image.setPixel( x, y, QtGui.QColor( 0, gValue * 255, 0 ).rgb() )

        elif mapType == 'rainmap':
            for x in xrange( self.width ):
                for y in xrange( self.height ):
                    gValue = self.rainfall[x, y]
                    self.image.setPixel( x, y, QtGui.QColor( gValue * 100, gValue * 100, gValue * 255 ).rgb() )

        elif mapType == 'windandrainmap':
            for x in xrange( self.width ):
                for y in xrange( self.height ):
                    rain = int( 255 * min( self.wind[x, y], 1.0 ) )
                    wind = int( 255 * min( self.rainfall[x, y], 1.0 ) )
                    self.image.setPixel( x, y, QtGui.QColor( 0, wind, rain ).rgb() )

        elif mapType == 'drainagemap':
            drainage = self.drainage * 255 # convert to greyscale
            for x in xrange( self.width ):
                for y in xrange( self.height ):
                    gValue = drainage[x, y]
                    self.image.setPixel( x, y, QtGui.QColor( gValue, gValue, gValue ).rgb() )

        elif mapType == 'rivermap':
            for x in xrange( self.width ):
                for y in xrange( self.height ):
                    gValue = self.elevation[x, y] * 255
                    if self.elevation[x, y] <= WGEN_SEA_LEVEL: # sealevel
                        self.image.setPixel( x, y, QtGui.QColor( 0, 0, gValue ).rgb() )
                    else:
                        rgb = QtGui.QColor( gValue, gValue, gValue ).rgb()
                        if self.rivers[x, y] > 0.0:
                            rgb = COLOR_COBALT
                        if self.lakes[x, y] > 0.0:
                            rgb = COLOR_AZURE
                        self.image.setPixel( x, y, rgb )

        elif mapType == 'biomemap':
            for x in xrange( self.width ):
                for y in xrange( self.height ):
                    self.image.setPixel( x, y, self.biomeColour[x, y] )

        else: # something bad happened...
            print "did not get a valid map type, check your bindings programmer man!"
            print len( background ), background, mapType
            from numpy import zeros
            background = zeros( ( self.width, self.height ), dtype = "int32" )

        return self.image
