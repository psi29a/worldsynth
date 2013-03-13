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

from PySide import QtGui

class Menu():
    '''Abstracted menu system for worldgenerator'''

    def __init__( self, mapGen ):
        ''' initialization of menu through mapGen object '''
        menuBar = mapGen.menuBar

        # File actions
        fileExitAction = QtGui.QAction( 'Exit', mapGen )
        fileExitAction.setShortcut( 'Ctrl+Q' )
        fileExitAction.setStatusTip( 'Exit application' )
        fileExitAction.triggered.connect( mapGen.close )
        fileNewAction = QtGui.QAction( 'New', mapGen )
        fileNewAction.setStatusTip( 'New world' )
        fileNewAction.triggered.connect( mapGen.newWorld )        
        fileOpenAction = QtGui.QAction( 'Open', mapGen )
        fileOpenAction.setStatusTip( 'Open world' )
        fileOpenAction.triggered.connect( mapGen.openWorld )
        fileSaveAction = QtGui.QAction( 'Save', mapGen )
        fileSaveAction.setStatusTip( 'Save world' )
        fileSaveAction.triggered.connect( mapGen.saveWorld )
        fileSaveAsAction = QtGui.QAction( 'Save as', mapGen )
        fileSaveAsAction.setStatusTip( 'Save world as...' )
        fileSaveAsAction.triggered.connect( mapGen.saveWorldAs )             
        fileImportAction = QtGui.QAction( 'Import', mapGen )
        fileImportAction.setStatusTip( 'Import world' )
        fileImportAction.triggered.connect( mapGen.importWorld )
        fileExportAction = QtGui.QAction( 'Export', mapGen )
        fileExportAction.setStatusTip( 'Export world' )
        fileExportAction.triggered.connect( mapGen.exportWorld )
        fileMenu = menuBar.addMenu( '&File' )
        fileMenu.addAction( fileNewAction )
        fileMenu.addAction( fileOpenAction )
        fileMenu.addAction( fileSaveAction )
        fileMenu.addAction( fileSaveAsAction )          
        fileMenu.addAction( fileImportAction )
        fileMenu.addAction( fileExportAction )
        fileMenu.addSeparator()
        fileMenu.addAction( fileExitAction )
        
        #editWorldAction = QtGui.QAction( 'World Settings', mapGen )
        #editWorldAction.setStatusTip( 'Configure your world settings.' )
        #editWorldAction.triggered.connect( mapGen.newWorld )  
        #editMenu = menuBar.addMenu( '&Edit' )      
        #editMenu.addAction( editWorldAction )
        
        # Generate actions
        genHeightMapAction = QtGui.QAction( 'Heightmap', mapGen )
        genHeightMapAction.setStatusTip( 'Generate a heightmap and display it.' )
        genHeightMapAction.triggered.connect( mapGen.genHeightMap )
        genHeatMapAction = QtGui.QAction( 'Heatmap', mapGen )
        genHeatMapAction.setStatusTip( 'Generate a heatmap and display it.' )
        genHeatMapAction.triggered.connect( mapGen.genHeatMap )
        genWeatherAction = QtGui.QAction( 'Weather', mapGen )
        genWeatherAction.setStatusTip( 'Generate weather and display it.' )
        genWeatherAction.triggered.connect( mapGen.genWeatherMap )
        genDrainageAction = QtGui.QAction( 'Drainage', mapGen )
        genDrainageAction.setStatusTip( 'Generate drainage and display it.' )
        genDrainageAction.triggered.connect( mapGen.genDrainageMap )
        genBiomesAction = QtGui.QAction( 'Biomes', mapGen )
        genBiomesAction.setStatusTip( 'Generate biomes and display it.' )
        genBiomesAction.triggered.connect( mapGen.genBiomeMap )
        genRiversAction = QtGui.QAction( 'Rivers', mapGen )
        genRiversAction.setStatusTip( 'Generate rivers/lakes and display it.' )
        genRiversAction.triggered.connect( mapGen.genRiverMap )
        genWorldAction = QtGui.QAction( 'Auto Generate', mapGen )
        genWorldAction.setStatusTip( 'Generate world.' )
        genWorldAction.triggered.connect( mapGen.genWorld )        
        generateMenu = menuBar.addMenu( '&Generate' )
        generateMenu.addAction( genHeightMapAction )
        generateMenu.addAction( genHeatMapAction )
        generateMenu.addAction( genWeatherAction )
        generateMenu.addAction( genDrainageAction )
        generateMenu.addAction( genBiomesAction )
        generateMenu.addAction( genRiversAction )
        generateMenu.addSeparator()
        generateMenu.addAction( genWorldAction )
        

        # View actions
        viewHeightMapAction = QtGui.QAction( 'Raw Heightmap', mapGen )
        viewHeightMapAction.setStatusTip( 'Display raw heightmap.' )
        viewHeightMapAction.triggered.connect( mapGen.viewHeightMap )
        viewSeaLevelAction = QtGui.QAction( 'Sea Level', mapGen )
        viewSeaLevelAction.setStatusTip( 'Display sea level view.' )
        viewSeaLevelAction.triggered.connect( mapGen.viewSeaLevel )
        viewElevationAction = QtGui.QAction( 'Elevation', mapGen )
        viewElevationAction.setStatusTip( 'Display elevation.' )
        viewElevationAction.triggered.connect( mapGen.viewElevation )
        
        viewRawHeatMapAction = QtGui.QAction( 'Raw Heat Map', mapGen )
        viewRawHeatMapAction.setStatusTip( 'Display raw temperature.' )
        viewRawHeatMapAction.triggered.connect( mapGen.viewRawHeatMap )
        viewHeatMapAction = QtGui.QAction( 'Heat Map', mapGen )
        viewHeatMapAction.setStatusTip( 'Display temperature.' )
        viewHeatMapAction.triggered.connect( mapGen.viewHeatMap )
        viewWeatherAction = QtGui.QAction( 'Weather (Rain and Wind)', mapGen )
        viewWeatherAction.setStatusTip( 'Display weather conditions.' )
        viewWeatherAction.triggered.connect( mapGen.viewWeatherMap )
        viewWindMapAction = QtGui.QAction( 'Wind Map', mapGen )
        viewWindMapAction.setStatusTip( 'Display wind map.' )
        viewWindMapAction.triggered.connect( mapGen.viewWindMap )
        viewPrecipitationAction = QtGui.QAction( 'Precipitation', mapGen )
        viewPrecipitationAction.setStatusTip( 'Display precipitation.' )
        viewPrecipitationAction.triggered.connect( mapGen.viewPrecipitation )
        viewDrainageAction = QtGui.QAction( 'Drainage', mapGen )
        viewDrainageAction.setStatusTip( 'Display drainage map.' )
        viewDrainageAction.triggered.connect( mapGen.viewDrainageMap )
        viewRiverMapAction = QtGui.QAction( 'River Map', mapGen )
        viewRiverMapAction.setStatusTip( 'Display river map.' )
        viewRiverMapAction.triggered.connect( mapGen.viewRiverMap )
        viewBiomeMapAction = QtGui.QAction( 'Biome Map', mapGen )
        viewBiomeMapAction.setStatusTip( 'Display biome map.' )
        viewBiomeMapAction.triggered.connect( mapGen.viewBiomeMap )
        viewErosionMapAction = QtGui.QAction( 'Erosion Map', mapGen )
        viewErosionMapAction.setStatusTip( 'Display erosion map.' )
        viewErosionMapAction.triggered.connect( mapGen.viewErosionMap )
        viewErosionAppliedMapAction = QtGui.QAction( 'Erosion Applied', mapGen )
        viewErosionAppliedMapAction.setStatusTip( 'Display applied erosion map.' )
        viewErosionAppliedMapAction.triggered.connect( mapGen.viewErosionAppliedMap )                
        
        viewMenu = menuBar.addMenu( '&View' )
        viewHeightmapMenu = viewMenu.addMenu( '&Heightmap' )
        viewHeightmapMenu.addAction( viewHeightMapAction )
        viewHeightmapMenu.addAction( viewElevationAction )
        viewHeightmapMenu.addAction( viewSeaLevelAction )
        viewWeatherMenu = viewMenu.addMenu( '&Weather' )
        viewWeatherMenu.addAction( viewRawHeatMapAction )
        viewWeatherMenu.addAction( viewHeatMapAction )
        viewWeatherMenu.addAction( viewWeatherAction )
        viewWeatherMenu.addAction( viewWindMapAction )
        viewWeatherMenu.addAction( viewPrecipitationAction )
        viewGeographyMenu = viewMenu.addMenu( '&Geography' )
        viewGeographyMenu.addAction( viewDrainageAction )
        viewGeographyMenu.addAction( viewRiverMapAction )
        viewGeographyMenu.addAction( viewBiomeMapAction )
        viewGeographyMenu.addAction( viewErosionMapAction )
        viewGeographyMenu.addAction( viewErosionAppliedMapAction )    
        

        # Help actions
        helpAboutAction = QtGui.QAction( 'About', mapGen )
        helpAboutAction.setStatusTip( 'About the Map Generator' )
        helpAboutAction.triggered.connect( mapGen.aboutApp )
        helpMenu = menuBar.addMenu( '&Help' )
        helpMenu.addAction( helpAboutAction )
