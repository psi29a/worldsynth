#!/usr/bin/env python
"""
World Generator: Generating worlds 

This program is a world generator using various simulations based
on real world phenomenon.

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
#system libraries
import random, sys, os, getopt, tables
from numpy import *
from PySide import QtGui, QtCore

# mapGen libraries
from library.constants import *
from library.menu import *
from library.render import render
from library.heightmap import *
from library.temperature import *
from library.weather import *
from library.rivers import *
from library.biomes import *

class MapGen( QtGui.QMainWindow ):

    def __init__( self, size = 512, debug = False, load = False ):
        '''Attempt to allocate the necessary resources'''
        super( MapGen, self ).__init__()

        # application variables
        self.height = self.width = size

        # setup our working directories
        self.homeDir = os.environ['HOME'] + os.sep + '.mapGen'
        if not os.path.exists( self.homeDir ):
            os.makedirs( self.homeDir )

        # world data
        self.elevation = zeros( ( self.width, self.height ) )
        self.wind = zeros( ( self.width, self.height ) )
        self.rainfall = zeros( ( self.width, self.height ) )
        self.temperature = zeros( ( self.width, self.height ) )
        self.rivers = zeros( ( self.width, self.height ) )
        self.lakes = zeros( ( self.width, self.height ) )
        self.drainage = zeros( ( self.width, self.height ) )
        self.biome = zeros( ( self.width, self.height ) )
        self.biomeColour = zeros( ( self.width, self.height ) )
        self.updateWorld()

        # set our state
        #self.settings = QSettings("Mindwerks", "mapGen")
        self.viewState = VIEWER_HEIGHTMAP

        # display the GUI!
        self.initUI()

        # Our debug / autopilot / crash dummy
        if debug:
            print "Going on full autopilot..."
            self.createHeightmap()
            #self.createTemperature()
            #self.createWindAndRain()
            #self.createRiversAndLakes()
            #self.createDrainage()
            #self.createBiomes()        

    def initUI( self ):
        '''Initialize the GUI for usage'''
        self.setMinimumSize( self.width, self.height )
        self.setWindowTitle( 'WorldGen: Generating Worlds' )
        self.sb = self.statusBar()

        self.setWindowIcon(QtGui.QIcon('./data/images/icon.png'))  
        self.trayIcon = QtGui.QSystemTrayIcon(QtGui.QIcon('./data/images/icon.png'),self)
        self.trayIcon.show()

        self.menuBar = self.menuBar()
        mapGenGui = Menu( self )

        self.mainImage = QtGui.QLabel( self )
        self.mainImage.setGeometry( 0, 0 , self.width, self.height )
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'heightmap' ) ) )
        self.setCentralWidget( self.mainImage )

        self.show()

        self.size = QtCore.QSize( self.geometry().width(), self.geometry().height() )
        self.heightOffset = self.geometry().height() - self.mainImage.geometry().height()

    def mouseMoveEvent( self, e ):
        x, y = e.pos().toTuple()

        if not self.menuBar.isNativeMenuBar(): # Does menu exists in parent window?
            y -= 25 # offset from menu

        if x < 0 or y < 0 or x > self.width - 1 or y > self.height - 1:
            return # do not bother going out of range of size

        sX, sY = str( x ).zfill( 4 ), str( y ).zfill( 4 ) # string formatting

        message = ''
        if self.viewState == VIEWER_HEIGHTMAP:
            message = 'Elevation is: ' + "{:4.2f}".format( self.elevation[x, y] )
        elif self.viewState == VIEWER_HEATMAP:
            message = 'Temperature is: ' + "{:4.2f}".format( self.temperature[x, y] )
        elif self.viewState == VIEWER_RAINFALL:
            message = 'Precipitation is: ' + "{:4.2f}".format( self.rainfall[x, y] )
        elif self.viewState == VIEWER_WIND:
            message = 'Wind strength is: ' + "{:4.2f}".format( self.wind[x, y] )
        elif self.viewState == VIEWER_DRAINAGE:
            message = 'Drainage is: ' + "{:4.2f}".format( self.drainage[x, y] )
        elif self.viewState == VIEWER_RIVERS:
            message = 'River flow is: ' + "{:4.2f}".format( self.rivers[x, y] )
        elif self.viewState == VIEWER_BIOMES:
            message = 'Biome type is: ' + Biomes().biomeType( self.biome[x, y] )

        self.statusBar().showMessage( ' At position: ' + sX + ',' + sY + ' - ' + message )

    def genHeightMap( self ):
        '''Generate our heightmap'''
        self.sb.showMessage( 'Generating heightmap...' )
        heightObject = HeightMap( self.width, self.height, roughness = 15 )
        found = False
        while not found: # loop until we have something workable
            heightObject.run( globe = True, seaLevel = WGEN_SEA_LEVEL - 0.1, method = HM_MDA )
            #break
            if heightObject.landMassPercent() < 0.15:
                self.statusBar().showMessage( 'Too little land mass' )
            elif heightObject.landMassPercent() > 0.85:
                self.statusBar().showMessage( 'Too much land mass' )
            elif heightObject.averageElevation() < 0.2:
                self.statusBar().showMessage( 'Average elevation is too low' )
            elif heightObject.averageElevation() > 0.8:
                self.statusBar().showMessage( 'Average elevation is too high' )
            elif heightObject.hasNoMountains():
                self.statusBar().showMessage( 'Not enough mountains' )
            elif heightObject.landTouchesEastWest():
                self.statusBar().showMessage( 'Cannot wrap around a sphere.' )
            else:
                found = True
        self.elevation = heightObject.heightmap
        del heightObject
        self.viewHeightMap()
        self.statusBar().showMessage( 'Successfully generated a heightmap!' )
        self.resize( self.size )

    def viewHeightMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'heightmap' ) ) )
        self.viewState = VIEWER_HEIGHTMAP
        self.statusBar().showMessage( 'Viewing raw heatmap.' )

    def viewElevation( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'elevation' ) ) )
        self.viewState = VIEWER_HEIGHTMAP
        self.statusBar().showMessage( 'Viewing elevation.' )

    def viewSeaLevel( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'sealevel' ) ) )
        self.viewState = VIEWER_HEIGHTMAP
        self.statusBar().showMessage( 'Viewing sealevel.' )

    def genHeatMap( self ):
        '''Generate a heatmap based on heightmap'''
        self.statusBar().showMessage( 'Generating heatmap...' )
        if self.elevation.sum() == 0:
            self.statusBar().showMessage( 'Error: You have not yet generated a heightmap.' )
            return
        hemisphere = random.randint( 1, 3 )
        tempObject = Temperature( self.elevation, hemisphere )
        tempObject.run( sb = self.sb )
        self.temperature = tempObject.temperature
        del tempObject
        self.viewHeatMap()
        self.statusBar().showMessage( 'Successfully generated a heatmap!' )
        self.resize( self.size )

    def viewHeatMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'heatmap' ) ) )
        self.viewState = VIEWER_HEATMAP
        self.statusBar().showMessage( 'Viewing heatmap.' )

    def viewRawHeatMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'rawheatmap' ) ) )
        self.viewState = VIEWER_HEATMAP
        self.statusBar().showMessage( 'Viewing raw heatmap.' )

    def genWeatherMap( self ):
        '''Generate a weather based on heightmap and heatmap'''
        self.sb.showMessage( 'Generating weather...' )
        if self.elevation.sum() == 0:
            self.statusBar().showMessage( 'Error: No heightmap!' )
            return
        if self.temperature.sum() == 0:
            self.statusBar().showMessage( 'Error: No heatmap!' )
            return
        weatherObject = Weather( self.elevation, self.temperature )
        weatherObject.run( self.sb )
        self.wind = weatherObject.windMap
        self.rainfall = weatherObject.rainMap
        del weatherObject
        self.viewWeatherMap()
        self.statusBar().showMessage( 'Successfully generated weather!' )
        self.resize( self.size )

    def viewWeatherMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'windandrainmap' ) ) )
        self.viewState = VIEWER_RAINFALL
        self.statusBar().showMessage( 'Viewing weathermap.' )

    def viewWindMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'windmap' ) ) )
        self.viewState = VIEWER_WIND
        self.statusBar().showMessage( 'Viewing windmap.' )

    def viewPrecipitation( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'rainmap' ) ) )
        self.viewState = VIEWER_RAINFALL
        self.statusBar().showMessage( 'Viewing rainmap.' )

    def genDrainageMap( self ):
        '''Generate a fractal drainage map'''
        self.sb.showMessage( 'Generating drainage...' )
        drainObject = MDA( self.width, self.height, 10 )
        drainObject.run()
        self.drainage = drainObject.heightmap
        del drainObject
        self.viewDrainageMap()
        self.statusBar().showMessage( 'Successfully generated drainage!' )
        self.resize( self.size )

    def viewDrainageMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'drainagemap' ) ) )
        self.viewState = VIEWER_DRAINAGE
        self.statusBar().showMessage( 'Viewing drainmap.' )

    def genBiomeMap( self ):
        '''Generate a biome map'''
        self.sb.showMessage( 'Generating biomes...' )
        if self.elevation.sum() == 0:
            self.statusBar().showMessage( 'Error: No heightmap!' )
            return
        if self.temperature.sum() == 0:
            self.statusBar().showMessage( 'Error: No heatmap!' )
            return
        if self.drainage.sum() == 0:
            self.statusBar().showMessage( 'Error: No drainage!' )
            return
        if self.wind.sum() == 0 or self.rainfall.sum() == 0:
            self.statusBar().showMessage( 'Error: No weather!' )
            return
        biomeObject = Biomes( self.elevation, self.rainfall, self.drainage, self.temperature )
        biomeObject.run()
        self.biome = biomeObject.biome
        self.biomeColour = biomeObject.biomeColourCode
        del biomeObject
        self.viewBiomeMap()
        self.statusBar().showMessage( 'Successfully generated biomes!' )
        self.resize( self.size )

    def viewBiomeMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'biomemap' ) ) )
        self.viewState = VIEWER_BIOMES
        self.statusBar().showMessage( 'Viewing biomes.' )

    def genRiverMap( self ):
        '''Generate a river map'''
        self.sb.showMessage( 'Generating rivers and lakes...' )
        if self.elevation.sum() == 0:
            self.statusBar().showMessage( 'Error: No heightmap!' )
            return
        if self.wind.sum() == 0 or self.rainfall.sum() == 0:
            self.statusBar().showMessage( 'Error: No weather!' )
            return
        riversObject = Rivers( self.elevation, self.rainfall )
        riversObject.run( self.sb )
        self.rivers = riversObject.riverMap
        self.lakes = riversObject.lakeMap
        del riversObject
        self.viewRiverMap()
        self.statusBar().showMessage( 'Successfully generated rivers and lakes!' )
        self.resize( self.size )

    def viewRiverMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'rivermap' ) ) )
        self.viewState = VIEWER_RIVERS
        self.statusBar().showMessage( 'Viewing rivers and lakes.' )

    def updateWorld( self ):
        # update and package up our world data
        self.world = {
          'elevation': self.elevation,
          'wind': self.wind,
          'rainfall': self.rainfall,
          'temperature': self.temperature,
          'rivers': self.rivers,
          'lakes': self.lakes,
          'drainage': self.drainage,
          'biome': self.biome,
          'biomeColour': self.biomeColour,
          }

    def importWorld( self ):
        file = self.homeDir + os.sep + 'worldData.h5'
        if tables.isHDF5File( file ) < 0 :
             self.statusBar().showMessage( 'worldData.h5 file does not exist' )
             return
        elif tables.isHDF5File( file ) == 0 :
             self.statusBar().showMessage( 'worldData.h5 file is not valid' )
             return
        h5file = tables.openFile( file, mode = 'r' )
        for k in self.world:
            exec( 'self.' + k + ' = h5file.getNode("/",k).read()' ) # read object out of pytables
        h5file.close()
        del h5file,file
        self.updateWorld()
        self.statusBar().showMessage( 'Imported world.' )
        self.viewBiomeMap()

    def exportWorld( self ):
        '''Dump all data to disk.'''
        self.updateWorld()
        file = self.homeDir + os.sep + 'worldData.h5'
        filter = tables.Filters( complevel = 9, complib = 'zlib', shuffle = True, fletcher32 = True )
        h5file = tables.openFile( file, mode = 'w', title = "worldData", filters = filter )
        for k in self.world:
            atom = tables.Atom.from_dtype(self.world[k].dtype)
            shape = self.world[k].shape
            cArray = h5file.createCArray( h5file.root, k, atom, shape )
            cArray[:] = self.world[k]
        h5file.close()
        del h5file,filter,file

    def aboutApp( self ):
        '''All about the application'''
        pass

def main():
    app = QtGui.QApplication( sys.argv )
    ex = MapGen()
    sys.exit( app.exec_() )

if __name__ == '__main__':
    #import cProfile
    #cProfile.run('main()')    
    main()
