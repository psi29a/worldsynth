from constants import *

class render():
    '''Transform the numpy data into a renderable form suitable for screen and
    exporting.'''
    
    def __init__(self, world):
        self.world = world
        for k in self.world:
            exec('self.'+k+' = self.world["'+k+'"]')
            
        self.width = len(self.elevation)
        self.height = self.width
       
    def convert(self, mapType):
        
        background = []
        if mapType == "heightmap":
            for x in self.elevation:
                for y in x:
                    colour = int(y*255)
                    hexified = "0x%02x%02x%02x" % (colour, colour, colour)
                    background.append(int(hexified,0))

        elif mapType == "sealevel":
            for x in self.elevation:
                for y in x:
                    colour = int(y*255)
                    if y <= WGEN_SEA_LEVEL: # sealevel
                        hexified = "0x%02x%02x%02x" % (0, 0, 255*y)
                    else:
                        hexified = "0x%02x%02x%02x" % (colour, colour, colour)
                    background.append(int(hexified,0))

        elif mapType == "elevation":
            for x in self.elevation:
                for y in x:
                    if y <= WGEN_SEA_LEVEL: # sealevel
                        hexified = "0x%02x%02x%02x" % (0, 0, 128)
                    elif y < BIOME_ELEVATION_HILLS: # grasslands
                        hexified = "0x%02x%02x%02x" % (128, 255, 0)
                    elif y < BIOME_ELEVATION_MOUNTAIN_LOW: # mountains
                        hexified = "0x%02x%02x%02x" % (90, 128, 90)
                    else:
                        hexified = "0x%02x%02x%02x" % (255, 255, 255)

                    background.append(int(hexified,0))

        elif mapType == "heatmap":
            for x in self.temperature:
                for y in x:
                    hexified = "0x%02x%02x%02x" % (255*y,128*y,255*(1-y))
                    background.append(int(hexified,0))

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

                    if self.rivers[x,y] > 0:
                        hexified = COLOR_COBALT

                    if self.lakes[x,y] > 0:
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
            print "did not get a map type, check your bindings programmer man!"
            print len(background),background
            background = zeros((self.width,self.height),dtype="int32")
            
        return background