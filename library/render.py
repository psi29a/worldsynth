from constants import *
from numpy import *
from PySide import QtGui
from PySide.QtGui import QImage

class render():
    '''Transform the numpy data into a renderable image suitable for screen'''
    
    def __init__(self, world):
        self.world = world
        for k in self.world:
            exec('self.'+k+' = self.world["'+k+'"]')
            
        self.width = len(self.elevation)
        self.height = self.width
        self.image = QImage(self.width, self.height, QImage.Format_RGB32)
       
    def convert(self, mapType):
        
        background = []
        if mapType == "heightmap":
            heightmap = self.elevation*255 # convert to greyscale
            for x in xrange(self.width):
                for y in xrange(self.height):
                    gValue = heightmap[x,y]
                    self.image.setPixel(x,y,QtGui.QColor(gValue,gValue,gValue).rgb())            

        elif mapType == "sealevel":
            for x in xrange(self.width):
                for y in xrange(self.height):
                    elevation = self.elevation[x,y]
                    gValue = elevation*255
                    if elevation <= WGEN_SEA_LEVEL: # sealevel
                        self.image.setPixel(x,y,QtGui.QColor(0,0,gValue).rgb())
                    else:
                        self.image.setPixel(x,y,QtGui.QColor(gValue,gValue,gValue).rgb())

        elif mapType == "elevation":
            for x in xrange(self.width):
                for y in xrange(self.height):
                    elevation = self.elevation[x,y]
                    if elevation <= WGEN_SEA_LEVEL: # sealevel
                        self.image.setPixel(x,y,QtGui.QColor(0, 0, 128).rgb())
                    elif elevation < BIOME_ELEVATION_HILLS: # grasslands
                        self.image.setPixel(x,y,QtGui.QColor(128, 255, 0).rgb())
                    elif elevation < BIOME_ELEVATION_MOUNTAIN_LOW: # mountains
                        self.image.setPixel(x,y,QtGui.QColor(90, 128, 90).rgb())
                    else:
                        self.image.setPixel(x,y,QtGui.QColor(255, 255, 255).rgb())

        elif mapType == "heatmap":
            for x in xrange(self.width):
                for y in xrange(self.height):
                    gValue = self.temperature[x,y]
                    self.image.setPixel(x,y,QtGui.QColor(gValue*255,gValue*128,(1-gValue)*255).rgb())   

        elif mapType == "rawheatmap":
            for x in self.temperature:
                for y in x:
                    colour = int(y*255)
                    hexified = "0x%02x%02x%02x" % (colour,colour,colour)
                    background.append(int(hexified,0))

        elif mapType == 'windmap':
            for x in self.wind:
                for y in x:
                    hexified = "0x%02x%02x%02x" % (0,255*y,0)
                    background.append(int(hexified,0))

        elif mapType == 'rainmap':
            for x in self.rainfall:
                for y in x:
                    hexified = "0x%02x%02x%02x" % (100*y,100*y,255*y)
                    background.append(int(hexified,0))

        elif mapType == 'windandrainmap':
            for x in range(0,self.width):
                for y in range(0,self.height):
                    wind = int(255*min(self.wind[x,y],1.0))
                    rain = int(255*min(self.rainfall[x,y],1.0))
                    hexified = "0x%02x%02x%02x" % (0,wind,rain)
                    background.append(int(hexified,0))

        elif mapType == 'drainagemap':
            for x in self.drainage:
                for y in x:
                    colour = int(y*255)
                    hexified = "0x%02x%02x%02x" % (colour,colour,colour)
                    background.append(int(hexified,0))

        elif mapType == 'rivermap':
            for x in range(0,self.width):
                for y in range(0,self.height):
                    colour = int(self.elevation[x,y]*255)

                    if self.elevation[x,y] <= WGEN_SEA_LEVEL: # sealevel
                        hexified = "0x%02x%02x%02x" % (0, 0, 255*self.elevation[x,y])
                    else:
                        hexified = "0x%02x%02x%02x" % (colour, colour, colour)
                        if self.rivers[x,y] > 0.0:
                            hexified = COLOR_COBALT
    
                        if self.lakes[x,y] > 0.0:
                            hexified = COLOR_AZURE

                    if isinstance(hexified,int):
                        background.append(hexified)
                    else:
                        background.append(int(hexified,0))

        elif mapType == 'biomemap':
            for x in range(0,self.width):
                for y in range(0,self.height):
                    hexified = self.biomeColour[x,y]
                    background.append(hexified)

        else: # something bad happened...
            print "did not get a valid map type, check your bindings programmer man!"
            print len(background),background, mapType
            background = zeros((self.width,self.height),dtype="int32")
            
        return self.image