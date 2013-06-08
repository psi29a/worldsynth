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
# system libraries
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

class MapGen(QtGui.QMainWindow):

    def __init__(self, mapSize=256, debug=False):
        '''Attempt to allocate the necessary resources'''
        super(MapGen, self).__init__()

        # application variables
        self.mapSize = (mapSize, mapSize)

        # setup our working directories
        self.fileLocation = None 
        self.homeDir = os.path.expanduser('~') + os.sep + '.mapGen'
        if not os.path.exists(self.homeDir):
            os.makedirs(self.homeDir)

        # set our state
        # self.settings = QSettings("Mindwerks", "mapGen")
        self.viewState = VIEWER_HEIGHTMAP

        # set initial world data
        self.resetDatasets()
        self.elevation = numpy.zeros(self.mapSize)
        self.world = {'elevation': self.elevation}
        
        # display the GUI!
        self.initUI()

        # make our world persistent
        self.updateWorld()   

        # Our debug / autopilot / crash dummy
        if debug:
            print "Going on full autopilot..."
            self.dNewWorld.rPRL.click()
            #self.mapSize = [1024,1024]
            self.genHeightMap()
       

    def initUI(self):
        '''Initialize the GUI for usage'''
        width, height = self.mapSize
        self.setMinimumSize(512, 512)
        self.setWindowTitle('WorldGen: Generating Worlds')
        self.sb = self.statusBar()

        self.setWindowIcon(QtGui.QIcon('./data/images/icon.png'))

        self.menuBar = self.menuBar()
        Menu(self)

        self.mainImage = QtGui.QLabel(self)
        blank = QtGui.QImage(width, height, QtGui.QImage.Format_Indexed8)
        blank.fill(QtGui.QColor(0,0,0))
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(blank))
        self.scrollArea = QtGui.QScrollArea(self)
        self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.scrollArea.setWidget(self.mainImage)
        self.setCentralWidget(self.scrollArea)

        self.show()

        # load our gui files
        loader = QtUiTools.QUiLoader()
        fileLocation = QtCore.QFile("./data/qt4/dNewWorld.ui")
        fileLocation.open(QtCore.QFile.ReadOnly)
        self.dNewWorld = loader.load(fileLocation, self)
        fileLocation.close()

        # New World defaults and attach signals
        self.dNewWorld.cSymmetricSize.setCurrentIndex(math.log(width, 2) - 5)
        self.dNewWorld.buttonBox.accepted.connect(self.acceptNewWorld)
        self.dNewWorld.buttonBox.rejected.connect(self.rejectNewWorld)
        self.dNewWorld.gbRoughness.hide()

        # Load our default values from UI
        self.algorithm      = self.getAlgorithm()
        self.roughness      = self.dNewWorld.sbRoughness.value()
        self.avgLandmass    = self.dNewWorld.cbAvgLandmass.isChecked()
        self.avgElevation   = self.dNewWorld.cbAvgElevation.isChecked()
        self.hasMountains   = self.dNewWorld.cbMountains.isChecked()
        self.hemisphere     = self.getHemisphere()        

    def resizeEvent(self, e):
        # Capture resize event, and align to new layout
        offset = 2
        sa = self.scrollArea.geometry()
        self.mainImage.setGeometry(sa.x(), sa.y(), sa.width() - offset, sa.height() - offset)  # set to be just as big as our scrollarea
        self.mainImage.setAlignment(QtCore.Qt.AlignCenter)  # center our image        

    def mouseMoveEvent(self, e): 
        # Give information about graphics being shown
        width, height = self.mapSize
        mx, my = e.pos().toTuple()
        
        if not self.menuBar.isNativeMenuBar():  # Does menu exists in parent window?
            offset = 25  # offset from menu        
        else:
            offset = 0
            
        # calculate our imagearea offsets
        sa = self.scrollArea.geometry()
        ox = sa.width() / 2 - width / 2
        oy = sa.height() / 2 + offset - height / 2

        if mx < ox or my < oy or mx > width + ox - 1 or my > height + oy - 1:
            return  # do not bother going out of range of size

        x, y = mx - ox, my - oy  # transpose

        sX, sY = str(x).zfill(4), str(y).zfill(4)  # string formatting

        message = ''
        if self.viewState == VIEWER_HEIGHTMAP:
            message = 'Elevation is: ' + "{:4.2f}".format(self.elevation[x, y])
        elif self.viewState == VIEWER_HEATMAP:
            message = 'Temperature is: ' + "{:4.2f}".format(self.temperature[x, y])
        elif self.viewState == VIEWER_RAINFALL:
            message = 'Precipitation is: ' + "{:4.2f}".format(self.rainfall[x, y])
        elif self.viewState == VIEWER_WIND:
            message = 'Wind strength is: ' + "{:4.2f}".format(self.wind[x, y])
        elif self.viewState == VIEWER_DRAINAGE:
            message = 'Drainage is: ' + "{:4.2f}".format(self.drainage[x, y])
        elif self.viewState == VIEWER_RIVERS:
            message = 'River flow is: ' + "{:4.2f}".format(self.rivers[x, y])
        elif self.viewState == VIEWER_BIOMES:
            message = 'Biome type is: ' + Biomes().biomeType(self.biome[x, y])
        elif self.viewState == VIEWER_EROSION:
            message = 'Erosion amount is: ' + "{:4.2f}".format(self.erosion[x, y])
        elif self.viewState == VIEWER_EROSIONAPP:
            message = 'Elevation in eroded heightmap is: ' + "{:4.2f}".format(self.elevation[x, y] - self.erosion[x, y])

        self.statusBar().showMessage(' At position: ' + sX + ',' + sY + ' - ' + message)

    def genWorld(self):
        self.genHeightMap()
        self.genHeatMap()
        self.genWeatherMap()
        self.genDrainageMap()
        self.genRiverMap()
        self.genBiomeMap()

    def getAlgorithm(self):
        if self.dNewWorld.rMDA.isChecked():
            method = HM_MDA
        elif self.dNewWorld.rDSA.isChecked():
            method = HM_DSA
        elif self.dNewWorld.rSPH.isChecked():
            method = HM_SPH
        elif self.dNewWorld.rPRL.isChecked():
            method = HM_PERLIN         
        else:
            method = None
            print "Error: no heightmap algo selected."
        
        return method

    def setAlgorithm(self, method): 
        if method == HM_MDA:
            self.dNewWorld.rMDA.click()
        elif method == HM_DSA:
            self.dNewWorld.rDSA.click()
        elif method == HM_SPH:
            self.dNewWorld.rSPH.click()
        elif method == HM_PERLIN:
            self.dNewWorld.rPRL.click()
        else:
            print "Error: no heightmap algo selected."
            
        return

    def genHeightMap(self):
        '''Generate our heightmap'''
        self.sb.showMessage('Generating heightmap...')

        # grab our values from config
        roughness = self.dNewWorld.sbRoughness.value()
        method = self.getAlgorithm()

        # create our heightmap
        heightObject = HeightMap(self.mapSize, roughness)
        found = False
        # method = 3 #testing
        while not found:  # loop until we have something workable
            heightObject.run(method)
            break #testing
            if self.dNewWorld.cbAvgLandmass.isChecked() and heightObject.landMassPercent() < 0.15:
                self.statusBar().showMessage('Too little land mass')
            elif self.dNewWorld.cbAvgLandmass.isChecked() and  heightObject.landMassPercent() > 0.85:
                self.statusBar().showMessage('Too much land mass')
            elif self.dNewWorld.cbAvgElevation.isChecked() and heightObject.averageElevation() < 0.2:
                self.statusBar().showMessage('Average elevation is too low')
            elif self.dNewWorld.cbAvgElevation.isChecked() and heightObject.averageElevation() > 0.8:
                self.statusBar().showMessage('Average elevation is too high')
            elif self.dNewWorld.cbMountains.isChecked() and heightObject.hasNoMountains():
                self.statusBar().showMessage('Not enough mountains')
            else:
                found = True

        self.elevation = heightObject.heightmap
        del heightObject
        self.viewHeightMap()
        self.statusBar().showMessage('Successfully generated a heightmap!')

    def viewHeightMap(self):
        self.updateWorld()
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(Render(self.world).convert('heightmap')))
        self.viewState = VIEWER_HEIGHTMAP
        self.statusBar().showMessage('Viewing heightmap.')

    def viewElevation(self):
        self.updateWorld()
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(Render(self.world).convert('elevation')))
        self.viewState = VIEWER_HEIGHTMAP
        self.statusBar().showMessage('Viewing elevation.')

    def viewSeaLevel(self):
        self.updateWorld()
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(Render(self.world).convert('sealevel')))
        self.viewState = VIEWER_HEIGHTMAP
        self.statusBar().showMessage('Viewing sealevel.')

    def getHemisphere(self):
        from random import randint
        if self.dNewWorld.rbHemisphereRandom.isChecked():
            hemisphere = randint(1, 3)
        elif self.dNewWorld.rbHemisphereBoth.isChecked():
            hemisphere = WGEN_HEMISPHERE_EQUATOR
        elif self.dNewWorld.rbHemisphereNorth.isChecked():
            hemisphere = WGEN_HEMISPHERE_NORTH
        elif self.dNewWorld.rbHemisphereSouth.isChecked():
            hemisphere = WGEN_HEMISPHERE_SOUTH
        else:
            hemisphere = None
            self.statusBar().showMessage('Error: No Hemisphere chosen for heatmap.')
        return hemisphere

    def setHemisphere(self, hemisphere):
        if hemisphere == WGEN_HEMISPHERE_EQUATOR:
            self.dNewWorld.rbHemisphereBoth.click()
        elif hemisphere == WGEN_HEMISPHERE_NORTH:
            self.dNewWorld.rbHemisphereNorth.click()
        elif hemisphere == WGEN_HEMISPHERE_SOUTH:
            self.dNewWorld.rbHemisphereSouth.click()
        else:
            self.statusBar().showMessage('Error: No Hemisphere chosen for heatmap.')
            
        return hemisphere

    def genHeatMap(self):
        '''Generate a heatmap based on heightmap'''
        if self.elevation is None:
            self.statusBar().showMessage('Error: You have not yet generated a heightmap.')
            return
        
        self.statusBar().showMessage('Generating heatmap...')
        hemisphere = self.getHemisphere()
        tempObject = Temperature(self.elevation, hemisphere)
        tempObject.run(sb=self.sb)
        self.temperature = tempObject.temperature
        del tempObject
        self.viewHeatMap()
        self.statusBar().showMessage('Successfully generated a heatmap!')

    def viewHeatMap(self):
        self.updateWorld()
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(Render(self.world).convert('heatmap')))
        self.viewState = VIEWER_HEATMAP
        self.statusBar().showMessage('Viewing heatmap.')

    def viewRawHeatMap(self):
        self.updateWorld()
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(Render(self.world).convert('rawheatmap')))
        self.viewState = VIEWER_HEATMAP
        self.statusBar().showMessage('Viewing raw heatmap.')

    def genWeatherMap(self):
        '''Generate a weather based on heightmap and heatmap'''
        self.sb.showMessage('Generating weather...')
        if self.elevation is None:
            self.statusBar().showMessage('Error: No heightmap!')
            return
        if self.temperature is None:
            self.statusBar().showMessage('Error: No heatmap!')
            return
        weatherObject = Weather(self.elevation, self.temperature)
        weatherObject.run(self.sb)
        self.wind = weatherObject.windMap
        self.rainfall = weatherObject.rainMap
        self.erosion = weatherObject.erosionMap
        del weatherObject
        self.viewWeatherMap()
        self.statusBar().showMessage('Successfully generated weather!')

    def viewWeatherMap(self):
        self.updateWorld()
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(Render(self.world).convert('windandrainmap')))
        self.viewState = VIEWER_RAINFALL
        self.statusBar().showMessage('Viewing weathermap.')

    def viewWindMap(self):
        self.updateWorld()
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(Render(self.world).convert('windmap')))
        self.viewState = VIEWER_WIND
        self.statusBar().showMessage('Viewing windmap.')

    def viewPrecipitation(self):
        self.updateWorld()
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(Render(self.world).convert('rainmap')))
        self.viewState = VIEWER_RAINFALL
        self.statusBar().showMessage('Viewing rainmap.')

    def genDrainageMap(self):
        '''Generate a fractal drainage map'''
        self.sb.showMessage('Generating drainage...')
        drainObject = HeightMap(self.mapSize)
        drainObject.run(HM_DSA)
        self.drainage = drainObject.heightmap
        del drainObject
        self.viewDrainageMap()
        self.statusBar().showMessage('Successfully generated drainage!')

    def viewDrainageMap(self):
        self.updateWorld()
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(Render(self.world).convert('drainagemap')))
        self.viewState = VIEWER_DRAINAGE
        self.statusBar().showMessage('Viewing drainmap.')

    def genBiomeMap(self):
        '''Generate a biome map'''
        self.sb.showMessage('Generating biomes...')
        if self.elevation is None:
            self.statusBar().showMessage('Error: No heightmap!')
            return
        if self.temperature is None:
            self.statusBar().showMessage('Error: No heatmap!')
            return
        if self.drainage is None:
            self.statusBar().showMessage('Error: No drainage!')
            return
        if self.wind.sum is None or self.rainfall is None:
            self.statusBar().showMessage('Error: No weather!')
            return
        biomeObject = Biomes(self.elevation, self.rainfall, self.drainage, self.temperature)
        biomeObject.run()
        self.biome = biomeObject.biome
        self.biomeColour = biomeObject.biomeColourCode
        del biomeObject
        self.viewBiomeMap()
        self.statusBar().showMessage('Successfully generated biomes!')

    def viewBiomeMap(self):
        self.updateWorld()
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(Render(self.world).convert('biomemap')))
        self.viewState = VIEWER_BIOMES
        self.statusBar().showMessage('Viewing biomes.')

    def genRiverMap(self):
        '''Generate a river map'''
        self.sb.showMessage('Generating rivers and lakes...')
        if self.elevation is None:
            self.statusBar().showMessage('Error: No heightmap!')
            return
        if self.wind is None or self.rainfall is None:
            self.statusBar().showMessage('Error: No weather!')
            return
        if self.drainage is None:
            self.statusBar().showMessage('Error: No drainage!')
            return
        riversObject = Rivers()
        riversObject.generate(self.elevation, self.rainfall, self.sb)
        self.rivers = riversObject.riverMap
        self.lakes = riversObject.lakeMap
        self.erosion += riversObject.erosionMap
        del riversObject
        self.viewRiverMap()
        self.statusBar().showMessage('Successfully generated rivers and lakes!')

    def viewRiverMap(self):
        self.updateWorld()
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(Render(self.world).convert('rivermap')))
        self.viewState = VIEWER_RIVERS
        self.statusBar().showMessage('Viewing rivers and lakes.')

    def viewErosionMap(self):
        self.updateWorld()
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(Render(self.world).convert('erosionmap')))
        self.viewState = VIEWER_EROSION
        self.statusBar().showMessage('Viewing raw erosion.')
    
    def viewErosionAppliedMap(self):
        self.updateWorld()
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(Render(self.world).convert('erosionappliedmap')))
        self.viewState = VIEWER_EROSIONAPP
        self.statusBar().showMessage('Viewing applied erosion map.')
    
    def updateWorld(self):
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

    def resetDatasets(self):
        self.elevation      = None
        self.wind           = None
        self.rainfall       = None
        self.temperature    = None
        self.drainage       = None
        self.rivers         = None
        self.lakes          = None
        self.erosion        = None        
        self.biome          = None
        self.biomeColour    = None
        
    def newWorld(self):
        self.dNewWorld.show()

    def acceptNewWorld(self):
        #size = 2 ** (self.dNewWorld.cSymmetricSize.currentIndex() + 5)
        #if self.mapSize[0] != size:
        #    self.newWorld(size)
        # local
        width = int(self.dNewWorld.leWidth.text())
        height = int(self.dNewWorld.leHeight.text())
        
        # global
        self.algorithm      = self.getAlgorithm()
        self.roughness      = self.dNewWorld.sbRoughness.value()
        self.avgLandmass    = self.dNewWorld.cbAvgLandmass.isChecked()
        self.avgElevation   = self.dNewWorld.cbAvgElevation.isChecked()
        self.hasMountains   = self.dNewWorld.cbMountains.isChecked()
        self.hemisphere     = self.getHemisphere()

        self.resetDatasets()
        self.mapSize        = (width, height)
        self.elevation      = numpy.zeros(self.mapSize)
        
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(width, height, QtGui.QImage.Format_RGB32)))
        self.updateWorld()            
        self.statusBar().showMessage(' Created New World!')

    def rejectNewWorld(self):
        #size = 2 ** (self.dNewWorld.cSize.currentIndex() + 5)
        #if self.mapSize[0] != size:
        #    self.dNewWorld.cSize.setCurrentIndex(math.log(self.mapSize[0], 2) - 5)
        self.statusBar().showMessage(' Canceled New World! ')

    def editWorldSettings(self):
        self.dNewWorld.cSize.setCurrentIndex(math.log(self.mapSize[0], 2) - 5)       
        self.dNewWorld.sbRoughness.setValue(int(settings['roughness']))
        self.dNewWorld.cbAvgLandmass.setCheckState((QtCore.Qt.Unchecked, QtCore.Qt.Checked)[settings['avgLandmass']])
        self.dNewWorld.cbAvgElevation.setCheckState((QtCore.Qt.Unchecked, QtCore.Qt.Checked)[settings['avgElevation']])
        self.dNewWorld.cbMountains.setCheckState((QtCore.Qt.Unchecked, QtCore.Qt.Checked)[settings['hasMountains']])
        self.setAlgorithm(settings['algorithm'])
        self.setHemisphere(settings['hemisphere'])
        
    def saveWorld(self):
        '''TODO: check if we are currently working on a world, save it.
        if not, we ignore the command. '''
        self.updateWorld()
        alreadyTried = False
        if not self.fileLocation and not alreadyTried:
            alreadyTried = True
            self.saveWorldAs()
        else:
            h5Filter = tables.Filters(complevel=9, complib='zlib', shuffle=True, fletcher32=True)
            h5file = tables.openFile(self.fileLocation, mode='w', title="worldData", filters=h5Filter)
            
            # store our numpy datasets
            for k in self.world:
                if self.world[k] is not None:
                    atom = tables.Atom.from_dtype(self.world[k].dtype)
                    shape = self.world[k].shape
                    cArray = h5file.createCArray(h5file.root, k, atom, shape)
                    cArray[:] = self.world[k]
        
            # store our world settings
            pyDict = {
                'key'         : tables.StringCol(itemsize=40),
                'value'       : tables.IntCol(),
            }
            settingsTable = h5file.createTable('/', 'settings', pyDict)
            
            settings = dict(
                            width=self.mapSize[0],                            
                            height=self.mapSize[1],
                            algorithm=self.algorithm,
                            roughness=self.roughness,
                            avgLandmass=self.avgLandmass,
                            avgElevation=self.avgElevation,
                            hasMountains=self.hasMountains,
                            hemisphere=self.hemisphere,
                            )
            
            settingsTable.append(settings.items())
            settingsTable.cols.key.createIndex()  # create an index
            
            h5file.close()
            del h5file, h5Filter            

    def saveWorldAs(self):
        '''Present a save world dialog'''
        self.fileLocation, _ = QtGui.QFileDialog.getSaveFileName(self, 'Save world as...')
        if self.fileLocation:
            self.saveWorld()
        else:
            self.statusBar().showMessage('Canceled save world as.')

    def openWorld(self):
        '''Open existing world project'''
        fileLocation, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open file')
        if not fileLocation:
            self.statusBar().showMessage('Canceled open world.')
            return

        if tables.isHDF5File(fileLocation) < 0 :
            self.statusBar().showMessage(fileLocation + ' does not exist')
            return
        elif tables.isHDF5File(fileLocation) == 0 :
            self.statusBar().showMessage(fileLocation + ' is not valid')
            return

        h5file = tables.openFile(fileLocation, mode='r')
        
        # restore our world settings
        settings = dict(h5file.root.settings.read())
        #self.newWorld(int(settings['width']))  # reset data 
        self.mapSize = (int(settings['width']), int(settings['height']))
        self.algorithm=settings['algorithm']
        self.roughness=settings['roughness']
        self.hemisphere=settings['hemisphere']         
        self.avgLandmass=settings['avgLandmass']
        self.avgElevation=settings['avgElevation']
        self.hasMountains=settings['hasMountains']
        
        # restore our numpy datasets
        self.resetDatasets()
        for array in h5file.walkNodes("/", "Array"):
            exec('self.' + array.name + '= array.read()')
        
        # print h5file
        # print dict(h5file.root.settings.read())
        
        h5file.close()
        self.fileLocation = fileLocation
        del h5file
        
        #print self.elevation[0]
        
        self.updateWorld()
        self.statusBar().showMessage('Imported world.')
        self.viewHeightMap()

    def importWorld(self):
        '''Eventually allow importing from all formats, but initially only heightmap
        from greyscale png'''
        files = "Images ("
        for file in QtGui.QImageReader.supportedImageFormats():
            files += "*."+str(file)+" "
        files += ")"
        fileLocation, _ = QtGui.QFileDialog.getOpenFileName(self, caption='Import world from...', filter=files)
        if not fileLocation:
            self.statusBar().showMessage('Aborted.') 
            return
        image = QtGui.QImageReader(fileLocation)
        heightmap = image.read()
        print fileLocation, heightmap.depth()
        width, height = heightmap.size().width(), heightmap.size().height()
        imgarr = numpy.ndarray(shape=(width,height), dtype=numpy.uint8, buffer=heightmap.bits())
        heightmap = imgarr.astype(numpy.float) / (2 ** heightmap.depth())
        
        #import png, itertools
        #width, height, pixels, meta = png.Reader(str(fileLocation)).asFloat(1.0)
        #print width, height, meta
        #print pixels
        #heightmap = numpy.vstack(itertools.imap(numpy.float64, pixels)).reshape((width, height))

        #print heightmap[0]
        self.elevation = numpy.flipud(numpy.rot90(heightmap.copy())) # massage data back into place
        self.viewHeightMap()
        self.statusBar().showMessage('Successfully imported a heightmap!')        
        

    def exportWorld(self):
        '''Eventually allow exporting to all formats, but initially only heightmap
        as 16-bit greyscale png'''
        import png
        fileLocation, _ = QtGui.QFileDialog.getSaveFileName(self, 'Export heightmap as...')
        width, height = self.mapSize
        heightmap = self.elevation.copy() * 65535
        heightmap = numpy.flipud(numpy.rot90(heightmap)).astype(numpy.uint16) # massage data
        
        print heightmap[0]
        
        # png heightmap
        pngObject = png.Writer(width, height, greyscale=True, bitdepth=16)
        fileObject = open(fileLocation + '.png', 'wb')
        pngObject.write(fileObject, heightmap)
        fileObject.close()

        # raw heightmap
        heightmap.flatten('C').tofile(fileLocation + '.raw', format='C')
        # heightmap.flatten( 'F' ).tofile( fileLocation+'.raw', format = 'F' )

        # csv heightmap
        heightmap.flatten('C').tofile(fileLocation + '.csv', sep=",")
        # heightmap.flatten( 'F' ).tofile( fileLocation+'.csv', sep = "," )

    def aboutApp(self):
        '''All about the application'''
        pass

def main():
    from sys import argv
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--profile", help="profile/benchmark process", 
                        action="store_true")
    parser.add_argument("-d", "--debug", help="debug mode",
                        action="store_true")
    parser.add_argument("-v", "--verbosity", help="increase output verbosity",
                        action="store_true")
    args = parser.parse_args()
    
    if args.verbosity:
        print "verbosity turned on"
    if args.debug:
        print "debug turned on"
        debug=True
    else:
        debug=False
    
    app = QtGui.QApplication(argv)
    if args.profile:
        import cProfile
        cProfile.run('ex = MapGen()')
    else:
        ex = MapGen(debug=debug)
    exit(app.exec_())

if __name__ == '__main__':
    main()
