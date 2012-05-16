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

import sys
from PySide import QtGui
from PySide.QtGui import QImage

from numpy import *

from library.constants import *
from library.midpointDisplacement import *

class MapGen(QtGui.QMainWindow):
    
    def __init__(self, size=512, debug=False, load=False):
        super(MapGen, self).__init__()
        
        # application variables
        self.height = self.width = size
           
        # world data
        self.elevation = zeros((self.width, self.height))

        self.initUI()
        
    def initUI(self):

                         
        exitAction = QtGui.QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        genHeightMapAction = QtGui.QAction('Heightmap', self)
        genHeightMapAction.setStatusTip('Generate a heightmap and display it.')
        genHeightMapAction.triggered.connect(self.genHeightMap)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        generateMenu = menubar.addMenu('&Generate')
        generateMenu.addAction(genHeightMapAction)

        self.mapGenImageQT = QImage(self.width, self.height, QImage.Format_RGB32)
        self.mainImage = QtGui.QLabel(self)
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(self.mapGenImageQT))
        self.setCentralWidget(self.mainImage)
        
        self.setGeometry(300, 300, self.width, self.height+32)
        self.setWindowTitle('Map Generator')  
        self.statusBar()  
        self.show()


    def genHeightMap(self):
        self.statusBar().showMessage('Generating heightmap...')
        mda = MDA(self.width, self.height, roughness=15)
        found = False
        while not found: # loop until we have something workable
            mda.run(globe=True,seaLevel=WGEN_SEA_LEVEL-0.1)
            found = True
        self.elevation = mda.heightmap*255 # convert to greyscale        
        del mda
        
        for x in xrange(self.width):
            for y in xrange(self.height):
                gValue = self.elevation[x,y]
                self.mapGenImageQT.setPixel(x,y,QtGui.QColor(gValue,gValue,gValue).rgb())
                
        self.mainImage.setPixmap(QtGui.QPixmap.fromImage(self.mapGenImageQT))
        self.statusBar().showMessage('Successfully generated a heightmap!')
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = MapGen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()    