#!/usr/bin/env python

import random, sys, os, getopt
import pygame.display
from numpy import *
from pygame.locals import *
from library.popup_menu import PopupMenu
from library.midpointDisplacement import *
from library.diamondSquare import *
from library.temperature import *
from library.windAndRain import *
from library.riversAndLakes import *
from library.biomes import *

class mapGen():
    """Our game object! This is a fairly simple object that handles the
    initialization of pygame and sets up our game to run."""

    def __init__(self, size=512, debug=False):
        """Called when the the Game object is initialized. Initializes
        pygame and sets up our pygame window and other pygame tools
        that we will need for more complicated tutorials."""
        pygame.init()
        pygame.display.set_icon(pygame.image.load("data/images/icon.png"))

        # create our window
        self.height = size
        self.width = size
        self.window = pygame.display.set_mode((self.width, self.height))

        # do some defines
        self.debug = debug

        # world data
        self.elevation = None
        self.wind = None
        self.rainfall = None
        self.temperature = None
        self.rivers = None
        self.contiguous = None
        self.biome = None
        self.biomeColour = None

        # clock for ticking
        self.clock = pygame.time.Clock()

        # set the window title
        pygame.display.set_caption("World Generator - Setup")

        # tell pygame to only pay attention to certain events
        # we want to know if the user hits the X on the window, and we
        # want keys so we can close the window with the esc key
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP, MOUSEBUTTONDOWN])

        # make background and blit the background onto the window
        self.background = pygame.Surface(self.window.get_size(), depth=32)
        self.background.fill((0, 0, 0))

        # Show are initial text
        font = pygame.font.Font(None, 36)
        text = font.render("Click for menu.", 1, (255, 255, 255))
        textpos = text.get_rect()
        textpos.centerx = self.background.get_rect().centerx
        self.background.blit(text, textpos)

        # update the display so the background is on there
        self.window.blit(self.background, (0,0))
        pygame.display.update()

        # create menues
        self.actionMenu = (
            'Action Menu',
            (
                'Actions',
                'Heightmap',
                'Temperature',
                'WindAndRain',
                'Drainage',
                'Rivers',
                'Biomes',
            ),
            (
                'Size',
                'Tiny',
                'Small',
                'Medium',
                'Large',
            ),
            'Save',
            'Reset',
            'Quit',
        )
        self.viewMenu = (
            'View Menu',
            'Height Map',
            'Sea Level',
            'Elevation',
            'Heat Map',
            'Raw Heat Map',
            'Wind Map',
            'Rain Map',
            'Wind and Rain Map',
            'Drainage Map',
            'River Map',
            'Biome Map'
        )


    def handleMenu(self,e):
        print 'Menu event: %s.%d: %s' % (e.name,e.item_id,e.text)
        if e.name == 'Action Menu':
            if e.text == 'Quit':
                quit()
            elif e.text == 'Reset':
                self.__init__()

        elif e.name == 'Actions...':
            if e.text == 'Heightmap':
                self.createHeightmap()
            elif e.text == 'Temperature':
                self.createTemperature()
            elif e.text == 'WindAndRain':
                self.createWindAndRain()
            elif e.text == 'Drainage':
                self.createDrainage()
            elif e.text == 'Rivers':
                self.createRiversAndLakes()
            elif e.text == 'Biomes':
                self.createBiomes()

        elif e.name == 'Size...':
            if e.text == 'Tiny':
                self.__init__(size=128)
            if e.text == 'Small':
                self.__init__(size=256)
            elif e.text == 'Medium':
                self.__init__(size=512)
            elif e.text == 'Large':
                self.__init__(size=1024)

        elif e.name == 'View Menu':
            if e.text == 'Height Map':
                self.showMap('heightmap')
            elif e.text == 'Sea Level':
                self.showMap('sealevel')
            elif e.text == 'Elevation':
                self.showMap('elevation')
            elif e.text == 'Heat Map':
                self.showMap('heatmap')
            elif e.text == 'Raw Heat Map':
                self.showMap('rawheatmap')
            elif e.text == 'Wind Map':
                self.showMap('windmap')
            elif e.text == 'Rain Map':
                self.showMap('rainmap')
            elif e.text == 'Wind and Rain Map':
                self.showMap('windandrainmap')
            elif e.text == 'Drainage Map':
                self.showMap('drainagemap')
            elif e.text == 'River Map':
                self.showMap('rivermap')
            elif e.text == 'Biome Map':
                self.showMap('biomemap')

    def run(self):
        """Runs the game. Contains the game loop that computes and renders
        each frame."""

        # check for debugging
        if self.debug:
            print "Going on full autopilot..."
            self.createHeightmap()
            #self.createTemperature()
            #self.createWindAndRain()
            self.createRiversAndLakes()
            #self.createDrainage()
            #self.createBiomes()

        print 'Starting Event Loop'
        running = True
        # run until something tells us to stop
        while running:

            # tick pygame clock
            # you can limit the fps by passing the desired frames per seccond to tick()
            self.clock.tick(60)

            # handle pygame events -- if user closes game, stop running
            running = self.handleEvents()

            # update the title bar with our frames per second
            pygame.display.set_caption('World Generator - %d fps' % self.clock.get_fps())

            # blit the dirty areas of the screen
            pygame.display.update()
            #pygame.display.flip()

        print 'Closing '


    def handleEvents(self):
        """Poll for PyGame events and behave accordingly. Return false to stop
        the event loop and end the game."""

        # poll for pygame events
        for event in pygame.event.get():
            if event.type == QUIT:
                return False

            # handle user input
            elif event.type == KEYDOWN:
                # if the user presses escape, quit the event loop.
                if event.key == K_ESCAPE:
                    return False

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    print 'Show action menu: '
                    PopupMenu(self.actionMenu)
                elif event.button == 3:
                    print 'Show view menu: '
                    PopupMenu(self.viewMenu)

            elif event.type == USEREVENT:
                if event.code == 'MENU':
                    self.handleMenu(event)

        self.window.blit(self.background, (0,0)) # blit to screen our background
        pygame.display.update() # update our screen after event

        return True


    def showMap(self,mapType):
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
                    elif self.rivers[x,y] > 0:
                        hexified = "0x%02x%02x%02x" % (255, 0, 0) # R,G,B
                    else:
                        hexified = "0x%02x%02x%02x" % (colour, colour, colour)

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

        #print len(background),len(self.elevation)

        background = array(background,dtype="int32").reshape(self.width,self.height)
        pygame.surfarray.blit_array(self.background, background)
        pygame.display.update()
        #print len(background),background
        del background

    def createHeightmap(self):
        mda = MDA(self.width, self.height, roughness=5)
        found = False
        while not found: # loop until we have something workable
            mda.run(globe=True,seaLevel=WGEN_SEA_LEVEL-0.1)
            self.elevation = mda.heightmap
            self.showMap('heightmap')
            if self.landMassPercent() < 0.15:
                print "Rejecting map: to little landmass"
            elif self.landMassPercent() > 0.85:
                print "Rejecting map: to much landmass"
            elif self.averageElevation() < 0.2:
                print "Rejecting map: average elevation is too low"
            elif self.averageElevation() > 0.8:
                print "Rejecting map: average elevation is too high"
            elif self.hasNoMountains():
                print "Rejecting map: not enough mountains"
            elif self.landTouchesEastWest():
                print "Rejecting map: cannot wrap around a sphere."
            else:
                print "Success! We have found an usable map."
                found = True
            pygame.display.set_caption('World Generator - %d fps' % self.clock.get_fps())
            self.window.blit(self.background, (0,0))
            pygame.display.update()
        del mda
        self.showMap('heightmap')

    def createTemperature(self):
        if self.elevation == None:
            print "Error: You have not yet generated a heightmap."
            return
        tempObject = Temperature(self.elevation,2)
        tempObject.run()
        self.temperature = tempObject.temperature
        del tempObject
        self.showMap('rawheatmap')

    def createWindAndRain(self):
        if self.elevation == None:
            print "Error: No heightmap!"
            return
        if self.temperature == None:
            print "Error: No temperature map!"
            return
        warObject = WindAndRain(self.elevation, self.temperature)
        warObject.run()
        self.wind = warObject.windMap
        self.rainfall = warObject.rainMap
        del warObject
        self.showMap('windandrainmap')

    def createDrainage(self):
        drainObject = MDA(self.width, self.height, 10)
        drainObject.run()
        self.drainage = drainObject.heightmap
        del drainObject
        self.showMap('drainagemap')

    def createBiomes(self):
        if self.elevation == None:
            print "Error: No heightmap!"
            return
        if self.temperature == None:
            print "Error: No temperature map!"
            return
        if self.drainage == None:
            print "Error: No drainage map!"
            return
        if self.rainfall == None:
            print "Error: No rainfall map!"
            return
        biomeObject = Biomes(self.elevation, self.rainfall, self.drainage, self.temperature)
        biomeObject.run()
        self.biome = biomeObject.biome
        self.biomeColour = biomeObject.biomeColourCode
        del biomeObject
        self.showMap('biomemap')

    def createRiversAndLakes(self):
        riversObject = Rivers(self.elevation, None)
        riversObject.run()
        self.rivers = riversObject.riverMap
        del riversObject
        self.showMap('rivermap')

    def landMassPercent(self):
        return self.elevation.sum() / (self.width * self.height)

    def averageElevation(self):
        return average(self.elevation)

    def hasNoMountains(self):
        if self.elevation.max() > BIOME_ELEVATION_MOUNTAIN:
            return False
        return True

    def landTouchesEastWest(self):
        for x in range(0,1):
            for y in range(0,self.height):
                if self.elevation[x,y] > WGEN_SEA_LEVEL or \
                    self.elevation[self.width-1-x,y] > WGEN_SEA_LEVEL:
                    return True

        return False

    def landTouchesMapEdge(self):
        result = False

        for x in range(4,self.width-4):
            if self.elevation[x,4] > WGEN_SEA_LEVEL or self.elevation[x,self.height-4] > WGEN_SEA_LEVEL:
                result = True
                break

        for y in range(4,self.height-4):
            if self.elevation[4,y] > WGEN_SEA_LEVEL or self.elevation[self.width-4,y] > WGEN_SEA_LEVEL:
                result = True
                break

        return result

class Button(pygame.sprite.Sprite):
    """An extremely simple button sprite."""
    def __init__(self, xy, text):
        pygame.sprite.Sprite.__init__(self)
        self.xy = xy
        self.font = pygame.font.Font(None, 25)  # load the default font, size 25
        self.color = (0, 0, 0)         # our font color in rgb
        self.text = text
        self.generateImage() # generate the image

    def generateImage(self):
        # draw text with a solid background - about as simple as we can get
        self.image = self.font.render(self.text, True, self.color, (200,200,200))
        self.rect = self.image.get_rect()
        self.rect.center = self.xy

class TextSprite(pygame.sprite.Sprite):
    """An extremely simple text sprite."""

    def __init__(self, xy, text=''):
        pygame.sprite.Sprite.__init__(self)
        self.xy = xy    # save xy -- will center our rect on it when we change the text
        self.font = pygame.font.Font(None, 25)  # load the default font, size 25
        self.color = (255, 165, 0)         # our font color in rgb
        self.text = text
        self.generateImage() # generate the image

    def setText(self, text):
        self.text = text
        self.generateImage()

    def generateImage(self):
        """Updates the text. Renders a new image and re-centers at the initial coordinates."""
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = self.xy

# runs the program
if __name__ == '__main__':
    debug = False
    size = 512
    # parse our options and arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hds:")
    except getopt.GetoptError:
        #usage()
        print "Unable to parse arguments"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-d"):
            debug = True
            print "Debugging turned on."
        elif opt in ("-s"):
            size = int(arg)
        elif opt in ("-h", "--help"):
            #usage()
            print "No help for you..."
            sys.exit()

    world = mapGen(size=size,debug=debug)
    world.run()
