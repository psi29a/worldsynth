#!/usr/bin/python
# Requirements: 
#  - pyPNG @ http://pypng.googlecode.com

import math, random, sys
from numpy import *

class MDA():
    def __init__(self, width, height, roughness):
        self.size = width+height
        self.width = width
        self.height = height
        self.roughness = roughness
        self.heightmap = empty((self.width,self.height))

    def run(self):
        c1 = random.random()
        c2 = random.random()
        c3 = random.random()
        c4 = random.random()
        self.divideRect(0, 0, self.width, self.height, c1, c2, c3, c4)            

    def normalize(self, point): # +/- infinity are reset to 1 and 1 values
        if point < 0.0:
            point = 0.0
        elif point > 1.0:
            point = 1.0
        return point
        
    def displace(self, small_size):
        maxd = small_size / self.size * self.roughness
        return (random.random() - 0.5) * maxd
        
    def divideRect(self, x, y, width, height, c1, c2, c3, c4):
        new_width = math.floor(width / 2)
        new_height = math.floor(height / 2)
        
        if (width > 1 or height > 1):
            # average of all the points and normalize in case of "out of bounds" during displacement
            mid = self.normalize(self.normalize(((c1 + c2 + c3 + c4) / 4) + self.displace(new_width + new_height)))
           
            # midpoint of the edges is the average of its two endpoints
            edge1 = self.normalize((c1 + c2) / 2)
            edge2 = self.normalize((c2 + c3) / 2)
            edge3 = self.normalize((c3 + c4) / 2)
            edge4 = self.normalize((c4 + c1) / 2)
            
            # recursively go down the rabbit hole
            self.divideRect(x, y, new_width, new_height, c1, edge1, mid, edge4)
            self.divideRect(x + new_width, y, new_width, new_height, edge1, c2, edge2, mid)
            self.divideRect(x + new_width, y + new_height, new_width, new_height, mid, edge2, c3, edge3)
            self.divideRect(x, y + new_height, new_width, new_height, edge4, mid, edge3, c4)
            
        else:
            c = (c1 + c2 + c3 + c4) / 4
                         
            x = int(x)
            y = int(y)

            self.heightmap[x][y] = c
            
            if (width == 2):
                self.heightmap[x + 1][y] = c
            if (height == 2):
                self.heightmap[x][y + 1] = c
            if (width == 2 and height == 2):
                self.heightmap[x + 1][y + 1] = c
                
    def savePNG(self):
        colors = []
        row = []
        for x in range(0, self.width):
            for y in range(0, self.height):
                row.append(int(self.heightmap[x][y] * 255))
            colors.append(tuple(row))
            row = []

        f = open('terrain.png', 'wb')
        w = png.Writer(self.width, self.height, greyscale=True)
        w.write(f, colors)
        f.close()

    def savecPNG(self):
        colors = []
        row = []
        for x in range(0, self.width):
            for y in range(0, self.height):
                rgb = self.map_to_terraing(int(self.heightmap[x][y] * 255))
                row.append(rgb[0])
                row.append(rgb[1])
                row.append(rgb[2])            
            colors.append(tuple(row))
            row = []

        f = open('terrain.png', 'wb')
        w = png.Writer(self.width, self.height)
        w.write(f, colors)
        f.close()

    def map_to_terrain(self, h):   
        if h > 200:  
            r = h 
            g = h  
            b = h  
        elif h <= 200 and h > 100:  
            r = 86
            g = 150 
            b = 17
        elif h <= 100 and h > 70:  
            r = 0  
            g = 100  
            b = 0  
        elif h <= 70 and h > 50:  
            r = 96  
            g = 51  
            b = 17  
        elif h <= 50 and h > 20:  
            r = 0  
            g = 128  
            b = 255  
        else:  
            r = 0  
            g = 0  
            b = 200
        return r,g,b

    def map_to_terraing(self, h):   
        if h >= 200:  
            height = (h - 200) / 55.0  
            r = int(height * (255 - 86) + 86)  
            g = int(height * (255 - 150) + 150)  
            b = int(height * (255 - 15) + 15)  
        elif h < 200 and h >= 100:  
            height = (h - 100) / 100.0  
            r = int(height * 86)  
            g = int(height * (150 - 100) + 100)  
            b = int(height * 17)  
        elif h < 100 and h >= 70:  
            height = (h - 70) / 30.0  
            r = int((1.0 - height) * 96)  
            g = int(height * (100 - 51) + 51)  
            b = int((1.0 - height) * 17)  
        elif h < 70 and h >= 50:  
            height = (h - 50) / 20.0;  
            r = int(height * 96)  
            g = int((1.0 - height) * (128 - 51) + 51)  
            b = int((1.0 - height) * (255 - 17) + 17)  
        elif h < 50 and h > 20:  
            height = (h - 20) / 30.0
            r = 0  
            g = int(height * 128)  
            b = 255  
        else:  
            r = 0  
            g = 0  
            b = 255
        return r,g,b


# runs the program
if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "You must pass a width, height, and roughness!"
        sys.exit()
    
    import png
    
    width = int(sys.argv[1])
    height = int(sys.argv[2])
    roughness = int(sys.argv[3])

    print "Setting things up..."
    mda = MDA(width, height, roughness)
    print "Thinking..."
    mda.run()
    mda.savecPNG()
    print "done!"
