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
from PySide import QtGui

# mapGen libraries
from library.constants import *
from library.render import render
from library.midpointDisplacement import *
from library.temperature import *

class MapGen(QtGui.QMainWindow):
    
    def __init__(self, size=512, debug=False, load=False):
        '''Attempt to allocate the necessary resources'''
        super(MapGen, self).__init__()
        
        # application variables
        self.height = self.width = size
           
        # setup our working directories
        self.homeDir = os.environ['HOME']+os.sep+'.mapGen'
        if not os.path.exists(self.homeDir):
            os.makedirs(self.homeDir)  
           
        # world data
        self.elevation = zeros((self.width, self.height))
        self.wind = zeros((self.width, self.height))
        self.rainfall = zeros((self.width, self.height))
        self.temperature = zeros((self.width, self.height))
        self.rivers = zeros((self.width, self.height))
        self.lakes = zeros((self.width, self.height))
        self.drainage = zeros((self.width, self.height))
        self.biome = zeros((self.width, self.height))
        self.biomeColour = zeros((self.width, self.height))
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
        
    def initUI(self):
        '''Initialize the GUI for usage'''
        
        fileExitAction = QtGui.QAction('Exit', self)
        fileExitAction.setShortcut('Ctrl+Q')
        fileExitAction.setStatusTip('Exit application')
        fileExitAction.triggered.connect(self.close)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(fileExitAction)
        
        genHeightMapAction = QtGui.QAction('Heightmap', self)
        genHeightMapAction.setStatusTip('Generate a heightmap and display it.')
        genHeightMapAction.triggered.connect(self.genHeightMap)        
        
        genHeatMapAction = QtGui.QAction('Heatmap', self)
        genHeatMapAction.setStatusTip('Generate a heatmap and display it.')
        genHeatMapAction.triggered.connect(self.genHeatMap)         
        
        generateMenu = menubar.addMenu('&Generate')
        generateMenu.addAction(genHeightMapAction)
        generateMenu.addAction(genHeatMapAction)

        viewHeightMapAction = QtGui.QAction('Raw Heightmap', self)
        viewHeightMapAction.setStatusTip('Display raw heightmap.')
        viewHeightMapAction.triggered.connect(self.viewHeightMap)   
        viewSeaLevelAction = QtGui.QAction('Sea Level', self)
        viewSeaLevelAction.setStatusTip('Display sea level view.')
        viewSeaLevelAction.triggered.connect(self.viewSeaLevel) 
        viewElevationAction = QtGui.QAction('Elevation', self)
        viewElevationAction.setStatusTip('Display elevation.')
        viewElevationAction.triggered.connect(self.viewElevation)         

        viewMenu = menubar.addMenu('&View')
        viewMenu.addAction(viewHeightMapAction)
        viewMenu.addAction(viewElevationAction)        
        viewMenu.addAction(viewSeaLevelAction)

        helpAboutAction = QtGui.QAction('About', self)
        helpAboutAction.setStatusTip('About the Map Generator')
        helpAboutAction.triggered.connect(self.aboutApp)

        helpMenu = menubar.addMenu('&Help')
        helpMenu.addAction(helpAboutAction)

        self.mainImage = QtGui.QLabel(self)
        self.setCentralWidget(self.mainImage)
        
        self.setGeometry(300, 300, self.width, self.height+32)
        self.setWindowTitle('Map Generator')  
        self.statusBar()  
        self.show()

    def genHeightMap(self):
        '''Generate our heightmap'''
        self.statusBar().showMessage('Generating heightmap...')
        mda = MDA(self.width, self.height, roughness=15)
        found = False
        while not found: # loop until we have something workable
            mda.run(globe=True,seaLevel=WGEN_SEA_LEVEL-0.1)
            if mda.landMassPercent() < 0.15:
                self.statusBar().showMessage('Rejecting map: to little land mass')
            elif mda.landMassPercent() > 0.85:
                self.statusBar().showMessage('Rejecting map: to much land mass')
            elif mda.averageElevation() < 0.2:
                self.statusBar().showMessage('Rejecting map: average elevation is too low')
            elif mda.averageElevation() > 0.8:
                self.statusBar().showMessage('Rejecting map: average elevation is too high')
            elif mda.hasNoMountains():
                self.statusBar().showMessage('Rejecting map: not enough mountains')
            elif mda.landTouchesEastWest():
                self.statusBar().showMessage('Rejecting map: cannot wrap around a sphere.')
            else:
                found = True
        self.elevation = mda.heightmap        
        del mda
        self.viewHeightMap()        
        self.statusBar().showMessage('Successfully generated a heightmap!')

    def viewHeightMap(self):
        self.updateWorld()
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(render(self.world).convert('heightmap')))

    def viewElevation(self):
        self.updateWorld()
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(render(self.world).convert('elevation')))
        self.statusBar().showMessage('Viewing elevation...')
        
    def viewSeaLevel(self):
        self.updateWorld()
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(render(self.world).convert('sealevel')))    
        self.statusBar().showMessage('Viewing sealevel...')            

    def genHeatMap(self):
        '''Generate a heatmap based on heightmap'''
        self.statusBar().showMessage('Generating heatmap...')
        if self.elevation == None:
            self.statusBar().showMessage('Error: You have not yet generated a heightmap.')
            return
        hemisphere = random.randint(1,3)
        tempObject = Temperature(self.elevation,hemisphere)
        tempObject.run()
        self.temperature = tempObject.temperature
        del tempObject
        self.viewHeatMap()
        self.statusBar().showMessage('Successfully generated a heatmap!')
        
    def viewHeatMap(self):
        self.updateWorld()
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(render(self.world).convert('heatmap')))        

    def updateWorld(self):
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

    def importWorld(self):
        h5file = tables.openFile(self.homeDir+os.sep+'worldData.h5', mode='r')
        for k in self.world:
            exec('self.'+k+' = h5file.getNode("/",k).read()') # read object out of pytables
        h5file.close()
        self.updateWorld()
        self.showMap('biomemap')
        
    def exportWorld(self):
        '''Dump all data to disk.'''
        filter = tables.Filters(complevel=9, complib='zlib', fletcher32=True)
        h5file = tables.openFile(self.homeDir+os.sep+'worldData.h5', mode='w', title="worldData", filters=filter)
        root = h5file.root
        for k in self.world:
            exec('h5file.createArray(root,k,self.world["'+k+'"])')
        h5file.close()        
        
    def aboutApp(self):
        '''All about the application'''
        pass
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = MapGen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()    