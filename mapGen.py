#!/usr/bin/env python

import random, sys, os, getopt
import pygame.display
from numpy import *
from pygame.locals import *
from library.gui import gui
from library.midpointDisplacement import *
from library.diamondSquare import *
from library.temperature import *
from library.windAndRain import *
from library.riversAndLakes import *
from library.biomes import *
from library.render import render

class mapGen():
    '''More than just a map generator but a world generator complete with
    oceans, rivers, forests and more.'''

    def __init__(self, size=512, debug=False):
        self.debug = debug
        pygame.init()
        pygame.display.set_icon(pygame.image.load("data"+os.sep+"images"+os.sep+"icon.png"))

        # create our window
        self.height = size
        self.width = size
        self.window = pygame.display.set_mode((self.width, self.height))

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
        
        self.world = {}    

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

        # initialize gui
        self.gui = gui()

        # update the display so the background is on there
        self.window.blit(self.background, (0,0))
        pygame.display.update()


    def run(self):
        """Runs the game. Contains the game loop that computes and renders
        each frame."""

        # check for debugging
        if self.debug:
            print "Going on full autopilot..."
            self.createHeightmap()
            self.createTemperature()
            self.createWindAndRain()
            self.createRiversAndLakes()
            self.createDrainage()
            self.createBiomes()

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

            # blit to screen our background
            self.window.blit(self.background, (0,0))         
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
                    self.gui.menu('actionMenu')
                elif event.button == 3:
                    print 'Show view menu: '
                    self.gui.menu('viewMenu')

            elif event.type == USEREVENT:
                if event.code == 'MENU':
                    callback = self.gui.handleMenu(event)
                    
                    # we did something...
                    if callback:
                        exec(callback)                        
        return True


    def showMap(self,mapType):     
        renderer = render(self.world)
        background = renderer.convert(mapType)

        #print len(background),len(self.elevation)
        #print background

        background = array(background,dtype="int32").reshape(self.width,self.height)
        pygame.surfarray.blit_array(self.background, background)
        pygame.display.update()
        #print len(background),background

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

    def createHeightmap(self):
        mda = MDA(self.width, self.height, roughness=15)
        found = False
        while not found: # loop until we have something workable
            mda.run(globe=True,seaLevel=WGEN_SEA_LEVEL-0.1)
            self.elevation = mda.heightmap
            #self.showMap('heightmap')
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
        del mda
        self.updateWorld()
        self.showMap('heightmap')

    def createTemperature(self):
        if self.elevation == None:
            print "Error: You have not yet generated a heightmap."
            return
        tempObject = Temperature(self.elevation,2)
        tempObject.run()
        self.temperature = tempObject.temperature
        del tempObject
        self.updateWorld()
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
        self.updateWorld()
        self.showMap('windandrainmap')

    def createDrainage(self):
        drainObject = MDA(self.width, self.height, 10)
        drainObject.run()
        self.drainage = drainObject.heightmap
        del drainObject
        self.updateWorld()
        self.showMap('drainagemap')

    def createBiomes(self):
        biomeObject = Biomes(self.elevation, self.rainfall, self.drainage, self.temperature)
        biomeObject.run()
        self.biome = biomeObject.biome
        self.biomeColour = biomeObject.biomeColourCode
        del biomeObject
        self.updateWorld()
        self.showMap('biomemap')

    def createRiversAndLakes(self):
        riversObject = Rivers(self.elevation, self.rainfall)
        riversObject.run()
        self.rivers = riversObject.riverMap
        self.lakes = riversObject.lakeMap
        del riversObject
        self.updateWorld()
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
