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
import os, math, numpy, tables
from PySide import QtGui, QtCore, QtUiTools, QtXml

# mapGen libraries
from library.constants import *
from library.menu import Menu
from library.render import Render
from library.heightmap import HeightMap
from library.temperature import Temperature
from library.weather import Weather
from library.rivers import Rivers
from library.biomes import Biomes

class MapGen( QtGui.QMainWindow ):

    def __init__( self, mapSize = 256, debug = False ):
        '''Attempt to allocate the necessary resources'''
        super( MapGen, self ).__init__()

        # application variables
        self.mapSize = ( mapSize, mapSize )

        # setup our working directories
        self.homeDir = os.environ['HOME'] + os.sep + '.mapGen'
        if not os.path.exists( self.homeDir ):
            os.makedirs( self.homeDir )

        # set our state
        #self.settings = QSettings("Mindwerks", "mapGen")
        self.viewState = VIEWER_HEIGHTMAP

        # set initial world data
        self.elevation      = numpy.zeros(self.mapSize)
        self.wind           = None
        self.rainfall       = None
        self.temperature    = None 
        self.drainage       = None
        self.rivers         = None
        self.lakes          = None           
        self.erosion        = numpy.zeros(self.mapSize)        
        self.biome          = None
        self.biomeColour    = None

        # to give us something to display
        self.world = {'elevation': self.elevation}

        # display the GUI!
        self.initUI()

        # make our world persistent
        self.updateWorld()   

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
        width, height = self.mapSize
        self.setMinimumSize( 512, 512 )
        self.setWindowTitle( 'WorldGen: Generating Worlds' )
        self.sb = self.statusBar()

        self.setWindowIcon( QtGui.QIcon( './data/images/icon.png' ) )

        self.menuBar = self.menuBar()
        Menu( self )

        self.mainImage = QtGui.QLabel( self )
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage(QtGui.QImage(width, height, QtGui.QImage.Format_RGB32)) )
        self.scrollArea = QtGui.QScrollArea( self )
        self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.scrollArea.setWidget(self.mainImage)
        self.setCentralWidget(self.scrollArea)

        self.show()

        # load our gui files
        loader = QtUiTools.QUiLoader()
        fileLocation = QtCore.QFile( "./data/qt4/dWorldConf.ui" )
        fileLocation.open( QtCore.QFile.ReadOnly )
        self.dWorldConf = loader.load( fileLocation, self )
        fileLocation.close()

        # set defaults and attach signals
        self.dWorldConf.cSize.setCurrentIndex( math.log( width, 2 ) - 5 )
        self.dWorldConf.pbResize.clicked.connect( self.acceptSettings )
        self.dWorldConf.buttonBox.accepted.connect( self.acceptSettings )
        self.dWorldConf.buttonBox.rejected.connect( self.rejectSettings )
        self.dWorldConf.gbRoughness.hide()

    def resizeEvent(self, e):
        # Capture resize event, and align to new layout
        offset = 2
        sa = self.scrollArea.geometry()
        self.mainImage.setGeometry( sa.x(), sa.y(), sa.width()-offset, sa.height()-offset ) # set to be just as big as our scrollarea
        self.mainImage.setAlignment(QtCore.Qt.AlignCenter) # center our image        

    def mouseMoveEvent( self, e ): 
        # Give information about graphics being shown
        width, height = self.mapSize
        mx, my = e.pos().toTuple()
        
        if not self.menuBar.isNativeMenuBar(): # Does menu exists in parent window?
            offset = 25 # offset from menu        
        else:
            offset = 0
            
        # calculate our imagearea offsets
        sa = self.scrollArea.geometry()
        ox = sa.width()/2 - width/2
        oy = sa.height()/2+offset - height/2

        if mx < ox or my < oy or mx > width+ox-1 or my > height+oy-1:
            return # do not bother going out of range of size

        x,y = mx-ox,my-oy # transpose

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
        elif self.viewState == VIEWER_EROSION:
            message = 'Erosion amount is: ' + "{:4.2f}".format( self.erosion[x, y] )
        elif self.viewState == VIEWER_EROSIONAPP:
            message = 'Elevation in eroded heightmap is: ' + "{:4.2f}".format( self.elevation[x, y] - self.erosion[x, y] )

        self.statusBar().showMessage( ' At position: ' + sX + ',' + sY + ' - ' + message )

    def genWorld( self ):
        self.genHeightMap()
        self.genHeatMap()
        self.genWeatherMap()
        self.genDrainageMap()
        self.genRiverMap()
        self.genBiomeMap()

    def confWorld( self ):
        '''World settings'''
        self.dWorldConf.show()

    def acceptSettings( self ):
        size = 2 ** ( self.dWorldConf.cSize.currentIndex() + 5 )
        if self.mapSize[0] != size:
            self.newWorld( size )

    def rejectSettings( self ):
        size = 2 ** ( self.dWorldConf.cSize.currentIndex() + 5 )
        if self.mapSize[0] != size:
            self.dWorldConf.cSize.setCurrentIndex( math.log( self.mapSize[0], 2 ) - 5 )

    def genHeightMap( self ):
        '''Generate our heightmap'''
        self.sb.showMessage( 'Generating heightmap...' )

        # grab our values from config
        roughness = self.dWorldConf.sbRoughness.value()

        if self.dWorldConf.rMDA.isChecked():
            method = HM_MDA
        elif self.dWorldConf.rDSA.isChecked():
            method = HM_DSA
        elif self.dWorldConf.rSPH.isChecked():
            method = HM_SPH
        elif self.dWorldConf.rPerlin.isChecked():
            method = HM_PERLIN         
        else:
            print "Error: no heightmap algo selected."
            return

        # create our heightmap
        heightObject = HeightMap( self.mapSize, roughness )
        found = False
        #method = 3 #testing
        while not found: # loop until we have something workable
            heightObject.run( method )
            break
            if self.dWorldConf.cbAvgLandmass.isChecked() and  heightObject.landMassPercent() < 0.15:
                self.statusBar().showMessage( 'Too little land mass' )
            elif self.dWorldConf.cbAvgLandmass.isChecked() and  heightObject.landMassPercent() > 0.85:
                self.statusBar().showMessage( 'Too much land mass' )
            elif self.dWorldConf.cbAvgElevation.isChecked() and heightObject.averageElevation() < 0.2:
                self.statusBar().showMessage( 'Average elevation is too low' )
            elif self.dWorldConf.cbAvgElevation.isChecked() and heightObject.averageElevation() > 0.8:
                self.statusBar().showMessage( 'Average elevation is too high' )
            elif self.dWorldConf.cbMountains.isChecked() and heightObject.hasNoMountains():
                self.statusBar().showMessage( 'Not enough mountains' )
            else:
                found = True

        self.elevation = heightObject.heightmap
        del heightObject
        self.viewHeightMap()
        self.statusBar().showMessage( 'Successfully generated a heightmap!' )

    def viewHeightMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( Render( self.world ).convert( 'heightmap' ) ) )
        self.viewState = VIEWER_HEIGHTMAP
        self.statusBar().showMessage( 'Viewing raw heatmap.' )

    def viewElevation( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( Render( self.world ).convert( 'elevation' ) ) )
        self.viewState = VIEWER_HEIGHTMAP
        self.statusBar().showMessage( 'Viewing elevation.' )

    def viewSeaLevel( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( Render( self.world ).convert( 'sealevel' ) ) )
        self.viewState = VIEWER_HEIGHTMAP
        self.statusBar().showMessage( 'Viewing sealevel.' )

    def genHeatMap( self ):
        '''Generate a heatmap based on heightmap'''
        from random import randint
        if self.elevation is None:
            self.statusBar().showMessage( 'Error: You have not yet generated a heightmap.' )
            return

        if self.dWorldConf.rbHemisphereRandom.isChecked():
            hemisphere = randint( 1, 3 )
        elif self.dWorldConf.rbHemisphereBoth.isChecked():
            hemisphere = WGEN_HEMISPHERE_EQUATOR
        elif self.dWorldConf.rbHemisphereNorth.isChecked():
            hemisphere = WGEN_HEMISPHERE_NORTH
        elif self.dWorldConf.rbHemisphereSouth.isChecked():
            hemisphere = WGEN_HEMISPHERE_SOUTH
        else:
            self.statusBar().showMessage( 'Error: No Hemisphere chosen for heatmap.' )
            return

        self.statusBar().showMessage( 'Generating heatmap...' )
        tempObject = Temperature( self.elevation, hemisphere )
        tempObject.run( sb = self.sb )
        self.temperature = tempObject.temperature
        del tempObject
        self.viewHeatMap()
        self.statusBar().showMessage( 'Successfully generated a heatmap!' )

    def viewHeatMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( Render( self.world ).convert( 'heatmap' ) ) )
        self.viewState = VIEWER_HEATMAP
        self.statusBar().showMessage( 'Viewing heatmap.' )

    def viewRawHeatMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( Render( self.world ).convert( 'rawheatmap' ) ) )
        self.viewState = VIEWER_HEATMAP
        self.statusBar().showMessage( 'Viewing raw heatmap.' )

    def genWeatherMap( self ):
        '''Generate a weather based on heightmap and heatmap'''
        self.sb.showMessage( 'Generating weather...' )
        if self.elevation is None:
            self.statusBar().showMessage( 'Error: No heightmap!' )
            return
        if self.temperature is None:
            self.statusBar().showMessage( 'Error: No heatmap!' )
            return
        weatherObject = Weather( self.elevation, self.temperature )
        weatherObject.run( self.sb )
        self.wind = weatherObject.windMap
        self.rainfall = weatherObject.rainMap
        self.erosion += weatherObject.erosionMap
        del weatherObject
        self.viewWeatherMap()
        self.statusBar().showMessage( 'Successfully generated weather!' )

    def viewWeatherMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( Render( self.world ).convert( 'windandrainmap' ) ) )
        self.viewState = VIEWER_RAINFALL
        self.statusBar().showMessage( 'Viewing weathermap.' )

    def viewWindMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( Render( self.world ).convert( 'windmap' ) ) )
        self.viewState = VIEWER_WIND
        self.statusBar().showMessage( 'Viewing windmap.' )

    def viewPrecipitation( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( Render( self.world ).convert( 'rainmap' ) ) )
        self.viewState = VIEWER_RAINFALL
        self.statusBar().showMessage( 'Viewing rainmap.' )

    def genDrainageMap( self ):
        '''Generate a fractal drainage map'''
        self.sb.showMessage( 'Generating drainage...' )
        drainObject = HeightMap( self.mapSize )
        drainObject.run( HM_DSA)
        self.drainage = drainObject.heightmap
        del drainObject
        self.viewDrainageMap()
        self.statusBar().showMessage( 'Successfully generated drainage!' )

    def viewDrainageMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( Render( self.world ).convert( 'drainagemap' ) ) )
        self.viewState = VIEWER_DRAINAGE
        self.statusBar().showMessage( 'Viewing drainmap.' )

    def genBiomeMap( self ):
        '''Generate a biome map'''
        self.sb.showMessage( 'Generating biomes...' )
        if self.elevation is None:
            self.statusBar().showMessage( 'Error: No heightmap!' )
            return
        if self.temperature is None:
            self.statusBar().showMessage( 'Error: No heatmap!' )
            return
        if self.drainage is None:
            self.statusBar().showMessage( 'Error: No drainage!' )
            return
        if self.wind.sum is None or self.rainfall is None:
            self.statusBar().showMessage( 'Error: No weather!' )
            return
        biomeObject = Biomes( self.elevation, self.rainfall, self.drainage, self.temperature )
        biomeObject.run()
        self.biome = biomeObject.biome
        self.biomeColour = biomeObject.biomeColourCode
        del biomeObject
        self.viewBiomeMap()
        self.statusBar().showMessage( 'Successfully generated biomes!' )

    def viewBiomeMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( Render( self.world ).convert( 'biomemap' ) ) )
        self.viewState = VIEWER_BIOMES
        self.statusBar().showMessage( 'Viewing biomes.' )

    def genRiverMap( self ):
        '''Generate a river map'''
        self.sb.showMessage( 'Generating rivers and lakes...' )
        if self.elevation is None:
            self.statusBar().showMessage( 'Error: No heightmap!' )
            return
        if self.wind is None or self.rainfall is None:
            self.statusBar().showMessage( 'Error: No weather!' )
            return
        if self.drainage is None:
            self.statusBar().showMessage( 'Error: No drainage!' )
            return
        riversObject = Rivers()
        riversObject.generate( self.elevation, self.rainfall, self.sb )
        self.rivers = riversObject.riverMap
        self.lakes = riversObject.lakeMap
        self.erosion += riversObject.erosionMap
        del riversObject
        self.viewRiverMap()
        self.statusBar().showMessage( 'Successfully generated rivers and lakes!' )

    def viewRiverMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( Render( self.world ).convert( 'rivermap' ) ) )
        self.viewState = VIEWER_RIVERS
        self.statusBar().showMessage( 'Viewing rivers and lakes.' )

    def viewErosionMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( Render( self.world ).convert( 'erosionmap' ) ) )
        self.viewState = VIEWER_EROSION
        self.statusBar().showMessage( 'Viewing raw erosion.' )
    
    def viewErosionAppliedMap( self ):
        self.updateWorld()
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage( Render( self.world ).convert( 'erosionappliedmap' ) ) )
        self.viewState = VIEWER_EROSIONAPP
        self.statusBar().showMessage( 'Viewing applied erosion map.' )
    
    def updateWorld( self ):
        # update and package up our world data
        self.world = {
          'elevation': self.elevation,
          'wind': self.wind,
          'rainfall': self.rainfall,
          'temperature': self.temperature,
          'drainage': self.drainage,
          'rivers': self.rivers,
          'lakes': self.lakes,          
          'erosion': self.erosion,          
          'biome': self.biome,
          'biomeColour': self.biomeColour,
          }
        self.mapSize = self.elevation.shape
        #self.resizeEvent(e)
        #self.viewHeightMap()


    def newWorld( self, size = 256 ):
        width = height = size
        self.mapSize = ( size, size )
        self.elevation = numpy.zeros( self.mapSize )
        self.wind = None
        self.rainfall = None
        self.temperature = None
        self.drainage = None
        self.rivers = None
        self.lakes = None
        self.erosion = numpy.zeros( self.mapSize )        
        self.biome = None
        self.biomeColour = None
        
        self.mainImage.setPixmap( QtGui.QPixmap.fromImage(QtGui.QImage(width, height, QtGui.QImage.Format_RGB32)) )
        self.updateWorld()

    def saveWorld( self ):
        '''TODO: check if we are currently working on a world, save it.
        if not, we ignore the command. '''
        pass

    def saveWorldAs( self ):
        '''Present a save world dialog'''
        self.updateWorld()
        fileLocation, _ = QtGui.QFileDialog.getSaveFileName( self, 'Open fileLocation' )
        h5Filter = tables.Filters( complevel = 9, complib = 'zlib', shuffle = True, fletcher32 = True )
        h5file = tables.openFile( fileLocation, mode = 'w', title = "worldData", filters = h5Filter )
        for k in self.world:
            if self.world[k] is not None:
                atom = tables.Atom.from_dtype( self.world[k].dtype )
                shape = self.world[k].shape
                cArray = h5file.createCArray( h5file.root, k, atom, shape )
                cArray[:] = self.world[k]
        h5file.close()
        del h5file, h5Filter, fileLocation

    def openWorld( self ):
        '''Open existing world project'''
        fileLocation, _ = QtGui.QFileDialog.getOpenFileName( self, 'Open file' )
        if not fileLocation:
            self.statusBar().showMessage( 'Canceled open world.' )
            return

        if tables.isHDF5File( fileLocation ) < 0 :
            self.statusBar().showMessage( fileLocation + ' does not exist' )
            return
        elif tables.isHDF5File( fileLocation ) == 0 :
            self.statusBar().showMessage( fileLocation + ' is not valid' )
            return

        self.newWorld(self.mapSize[0]) # reset data
        h5file = tables.openFile( fileLocation, mode = 'r' )
        for array in h5file.walkNodes("/", "Array"):
            exec( 'self.' + array.name + '= array.read()')
            
        h5file.close()
        del h5file, fileLocation
        
        self.updateWorld()
        self.statusBar().showMessage( 'Imported world.' )
        self.viewHeightMap()

    def importWorld( self ):
        pass

    def exportWorld( self ):
        '''Eventually allow exporting to all formats, but initially only heightmap
        as 16-bit greyscale png'''
        import png
        width, height = self.mapSize
        heightmap = self.elevation.copy() * 65536
        pngObject = png.Writer( width, height, greyscale = True, bitdepth = 16 )
        fileLocation = open( './heightmap.png', 'wb' )
        pngObject.write( fileLocation, heightmap )
        file.close()

        # flat heightmap
        heightmap.astype( 'uint16' ).flatten( 'C' ).tofile( './heightmapCRowMajor.raw', format = 'C' )
        heightmap.astype( 'uint16' ).flatten( 'F' ).tofile( './heightmapFortranColumnMajor.raw', format = 'F' )

        # flat to text file
        heightmap.astype( 'uint16' ).flatten( 'C' ).tofile( './heightmapCRowMajor.csv', sep = "," )
        heightmap.astype( 'uint16' ).flatten( 'F' ).tofile( './heightmapFortranColumnMajor.csv', sep = "," )

    def aboutApp( self ):
        '''All about the application'''
        pass

def main():
    from sys import argv, exit
    app = QtGui.QApplication( argv )
    ex = MapGen()
    ex
    exit( app.exec_() )

if __name__ == '__main__':
    #import cProfile
    #cProfile.run('main()')    
    main()
