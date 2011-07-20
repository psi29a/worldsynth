#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Image, ImageDraw, ImageChops, ImageOps, ImageFilter
import pygame.display, pygame.image
import random
import sys
from math import ceil

class Planet():
    def __init__(self,mapSize = 512):
            self.percentWater = .70
            self.mapSize = mapSize #width (same as height) in pixels
            self.maxSize = 2.40 # 1 to 5 How big should the slices be cut, smaller slices create more islands
            self.shape = 1.40 # 1 has round continents .5 is twice as tall as it is wide, 2.0 is twice as wide as tall
            self.driftRate = .70 # As the world ages how much slower does it drift. 1 creates a more textured world but takes longer
            self.roughness = 1 #High numbers make a world faster, with more "ridges", but also makes things less "smooth"
            self.filename = 'heightmap.bmp'

            self.randType = random.uniform #change to alter variability
            self.xrand = lambda ms = self.mapSize*3: int(self.randType(0, ms))
            self.yrand = lambda ms = self.mapSize*2: int(self.randType(0-(ms/2), ms))
            

    def normalize(self, image): 
        image = image.filter(ImageFilter.BLUR)
        picture = ImageChops.blend(ImageOps.equalize(image), image, .5)
        return ImageChops.multiply(picture, picture)

    def finish(self, image): #called when window is closed, or iterations stop
        picture = self.normalize(image)
        picture.save(self.filename)
        pygame.quit()
        sys.exit();

    def drawPieSlices(self, oval, orig, action):
        fl = action[1]
        img = Image.new('L', (self.mapSize*2,self.mapSize))
        draw = ImageDraw.Draw(img)
        draw.pieslice([oval[0],oval[1],self.mapSize*4,oval[3]], 90, 270, fill=fl)
        del draw
        orig = action[0](orig, img)
        img = Image.new('L', (self.mapSize*2,self.mapSize))
        draw = ImageDraw.Draw(img)
        draw.pieslice([0-oval[0],oval[1],oval[2]-self.mapSize*2,oval[3]], 270, 90, fill=fl)
        del draw
        return action[0](orig, img)

    def drawOval(self, oval, orig, action):
        img = Image.new('L', (self.mapSize*2,self.mapSize))
        draw = ImageDraw.Draw(img)
        draw.ellipse(oval, fill=action[1])
        del draw
        return action[0](orig, img)

    def cutOval(self, orig, smallness=1):
        smallness = smallness ** self.driftRate
        landAction = lambda: (
            ImageChops.add, 
            ceil(self.randType(1,self.roughness*smallness*(self.percentWater)))
            )
        seaAction = lambda: (
            ImageChops.subtract, 
            ceil(self.randType(1,self.roughness*smallness*(1.0-self.percentWater)))
            )
        action = seaAction() if random.random() < self.percentWater else landAction()
        oval = [self.xrand(self.mapSize*2),self.yrand(self.mapSize),1,1] #x,y,x,y
        oval[2] = int(oval[0]+(self.mapSize*self.maxSize*self.shape)*smallness)
        oval[3] = int(oval[1]+(self.mapSize*self.maxSize)*smallness)
        if oval[2] > self.mapSize*2: #if x values cross our border, we needto wrap
            ret = self.drawPieSlices(oval, orig, action)
        else:
            ret = self.drawOval(oval, orig, action)
        return ret

    def highestPointOnSphere(self, sphere):
        extremes = sphere.getextrema()
        return extremes[0]/255.0 if self.percentWater > .5 else 1-(extremes[1]/255.0)

    def createSphere(self):
        #pygame.init() #Need this to render the output
        sphere = Image.new('L', (self.mapSize,self.mapSize))
        img = ImageDraw.Draw(sphere)
        baseline = (256*(1.0-(self.percentWater)))
        img.rectangle([0-self.mapSize,0,self.mapSize*4,self.mapSize], fill=baseline)
        del img
        return sphere

    def sphereToPicture(self, sphere):
        imageToPygame = lambda i: pygame.image.fromstring(i.tostring(), i.size, i.mode)
        picture = self.normalize(sphere)
        picture = ImageOps.colorize(picture, (0,0,0), (256,256,256))
        picture = imageToPygame(picture)
        return picture

    def generatePlanet(self, sphere, displayInterval = 50):
        extrema = self.highestPointOnSphere(sphere)
        i = 0
        picture = self.sphereToPicture(sphere)
        #pygame.display.set_mode(picture.get_size())
        #main_surface = pygame.display.get_surface()
        del picture
        while extrema > self.driftRate/(self.roughness*10*self.maxSize):
            sphere = self.cutOval(sphere, extrema)
            i = i+1
            #if displayInterval > 0 and i%displayInterval == 0:
            #    picture = self.sphereToPicture(sphere)
            #    main_surface.blit(picture, (0, 0))
            #    pygame.display.update()
            #    del picture

            #for event in pygame.event.get(): #When people close the window
            #    if event.type == pygame.QUIT:    
            #        return image
            extrema = self.highestPointOnSphere(sphere)
        return sphere
        
if __name__ == '__main__':
    sphere = Planet()
    sphere.finish(sphere.generatePlanet(sphere.createSphere(), 50))
    
