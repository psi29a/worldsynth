#!/usr/bin/env python
"""
Map Generator 

This program is a world generator using various simulations based
on real world phenomenon. The output data should be reusable by other
applications. 

author:  Bret Curtis
website: http://www.mindwerks.net 
license: LGPL
"""
#system libraries
import random, sys, os, getopt, tables
from numpy import *
from PySide import QtGui, QtCore

# mapGen libraries
from library.constants import *
from library.menu import *
from library.render import render
from library.midpointDisplacement import *
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
        self.setGeometry( 300, 300, self.width, self.height + 32 )
        self.setWindowTitle( 'Map Generator' )
        self.sb = self.statusBar()

        mapGenGui = Menu( self, self.menuBar() )

        self.mainImage = QtGui.QLabel( self )
        self.setCentralWidget( self.mainImage )

        self.show()


    def genHeightMap( self ):
        '''Generate our heightmap'''
        self.sb.showMessage( 'Generating heightmap...' )
        mda = MDA( self.width, self.height, roughness = 15 )
        found = False
        while not found: # loop until we have something workable
            mda.run( globe = True, seaLevel = WGEN_SEA_LEVEL - 0.1 )
            if mda.landMassPercent() < 0.15:
                self.statusBar().showMessage( 'Too little land mass' )
            elif mda.landMassPercent() > 0.85:
                self.statusBar().showMessage( 'Too much land mass' )
            elif mda.averageElevation() < 0.2:
                self.statusBar().showMessage( 'Average elevation is too low' )
            elif mda.averageElevation() > 0.8:
                self.statusBar().showMessage( 'Average elevation is too high' )
            elif mda.hasNoMountains():
                self.statusBar().showMessage( 'Not enough mountains' )
            elif mda.landTouchesEastWest():
                self.statusBar().showMessage( 'Cannot wrap around a sphere.' )
            else:
                found = True
        self.elevation = mda.heightmap
        del mda
        self.viewHeightMap()
        self.statusBar().showMessage( 'Successfully generated a heightmap!' )

    def viewHeightMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'heightmap' ) ) )
        self.statusBar().showMessage( 'Viewing raw heatmap.' )

    def viewElevation( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'elevation' ) ) )
        self.statusBar().showMessage( 'Viewing elevation.' )

    def viewSeaLevel( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'sealevel' ) ) )
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

    def viewHeatMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'heatmap' ) ) )

    def viewRawHeatMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'rawheatmap' ) ) )

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

    def viewWeatherMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'windandrainmap' ) ) )

    def viewWindMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'windmap' ) ) )

    def viewPrecipitation( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'rainmap' ) ) )

    def genDrainageMap(self):
        '''Generate a fractal drainage map'''
        self.sb.showMessage( 'Generating drainage...' )        
        drainObject = MDA(self.width, self.height, 10)
        drainObject.run()
        self.drainage = drainObject.heightmap
        del drainObject
        self.viewDrainageMap()
        self.statusBar().showMessage( 'Successfully generated drainage!' )

    def viewDrainageMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'drainagemap' ) ) )

    def genBiomeMap(self):
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
        biomeObject = Biomes(self.elevation, self.rainfall, self.drainage, self.temperature)
        biomeObject.run()
        self.biome = biomeObject.biome
        self.biomeColour = biomeObject.biomeColourCode
        del biomeObject
        self.viewBiomeMap()
        self.statusBar().showMessage( 'Successfully generated biomes!' )    

    def viewBiomeMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'biomemap' ) ) )

    def genRiverMap(self):
        '''Generate a river map'''
        self.sb.showMessage( 'Generating rivers and lakes...' )
        if self.elevation.sum() == 0:
            self.statusBar().showMessage( 'Error: No heightmap!' )
            return
        if self.wind.sum() == 0 or self.rainfall.sum() == 0:
            self.statusBar().showMessage( 'Error: No weather!' )
            return                       
        riversObject = Rivers(self.elevation, self.rainfall)
        riversObject.run()
        self.rivers = riversObject.riverMap
        self.lakes = riversObject.lakeMap
        del riversObject
        self.viewRiverMap()
        self.statusBar().showMessage( 'Successfully generated rivers and lakes!' )  

    def viewRiverMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( render( self.world ).convert( 'rivermap' ) ) )

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
        h5file = tables.openFile( self.homeDir + os.sep + 'worldData.h5', mode = 'r' )
        for k in self.world:
            exec( 'self.' + k + ' = h5file.getNode("/",k).read()' ) # read object out of pytables
        h5file.close()
        self.updateWorld()
        self.showMap( 'biomemap' )

    def exportWorld( self ):
        '''Dump all data to disk.'''
        filter = tables.Filters( complevel = 9, complib = 'zlib', fletcher32 = True )
        h5file = tables.openFile( self.homeDir + os.sep + 'worldData.h5', mode = 'w', title = "worldData", filters = filter )
        root = h5file.root
        for k in self.world:
            exec( 'h5file.createArray(root,k,self.world["' + k + '"])' )
        h5file.close()

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
