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
import sys, constants
from numpy import zeros

class Biomes():

    def __init__(self, *args, **kwargs):
        if len(args) == 0:
            pass
        elif len(args) == 4:
            self.heightmap = args[0]
            self.rainmap = args[1]
            self.drainmap = args[2]
            self.worldW = len(self.heightmap)
            self.worldH = len(self.heightmap[0])
            self.biome = zeros((self.worldW, self.worldH))
            self.biomeColourCode = zeros((self.worldW, self.worldH))
        else:
            sys.exit('0 or 4 arguments only')

    def run(self):
        # calculate biome -- from scale of 0-400 ((oldValue-0) * (100-0)) / (400-0) + 0
        for x in xrange(self.worldW):
            for y in xrange(self.worldH):
                
                # new way
                # for debugging, all areas are set to undefined
                self.biome[x, y] = constants.BIOME_TYPE_UNDEFINED
                self.biomeColourCode[x, y] = constants.COLOR_RED                
                
                # basic biome information based on elevation
                if self.heightmap[x,y] <= constants.WGEN_SEA_LEVEL:       
                    self.biome[x, y] = constants.BIOME_TYPE_WATER         # Sealevel: e1-99 (0-98)
                    self.biomeColourCode[x, y] = constants.COLOR_BLUE
                elif self.heightmap[x, y] > 0.75 and self.heightmap[x, y] <= 0.83:                     
                    self.biome[x, y] = constants.BIOME_TYPE_MOUNTAIN_LOW  # Mountain (Low): e300-332
                    self.biomeColourCode[x, y] = constants.COLOR_GRAY
                elif self.heightmap[x, y] > 0.83 and self.heightmap[x, y] <= 0.91:            
                    self.biome[x, y] = constants.BIOME_TYPE_MOUNTAIN      # Mountain: e333-365
                    self.biomeColourCode[x, y] = constants.COLOR_ASH_GRAY
                elif self.heightmap[x, y] > 0.91 and self.heightmap[x, y] <= 1.00:               
                    self.biome[x, y] = constants.BIOME_TYPE_MOUNTAIN_HIGH # Mountain (High): e366-400
                    self.biomeColourCode[x, y] = constants.COLOR_IVORY
                else: # all other biomes are between elevations of 100 and 299 (25-74)
                    if self.rainmap[x, y] < 0.10: # all rainfall between 0 and 9
                        if self.drainmap[x, y] < 0.33:    # Desert (Sand): d0-32
                            self.biome[x, y] = constants.BIOME_TYPE_DESERT_SAND
                            self.biomeColourCode[x, y] = constants.COLOR_GOLDEN_YELLOW
                        elif self.drainmap[x, y] < 0.50:    # Desert (Rock): d33-49
                            self.biome[x, y] = constants.BIOME_TYPE_DESERT_ROCK
                            self.biomeColourCode[x, y] = constants.COLOR_DARK_CHESTNUT
                        else: # Desert (Badlands): r0-9, d50-100
                            self.biome[x, y] = constants.BIOME_TYPE_DESERT_BADLANDS
                            self.biomeColourCode[x, y] = constants.COLOR_TAUPE_PALE
                    elif self.rainmap[x, y] >= 0.10 and self.rainmap[x, y] < 0.20:
                        if self.drainmap[x, y] < 0.51:    # Grassland: r10-19, d0-50
                            self.biome[x, y] = constants.BIOME_TYPE_GRASSLAND
                            self.biomeColourCode[x, y] = constants.COLOR_GREEN
                        else: # Hills: r10-65, d50-100
                            self.biome[x, y] = constants.BIOME_TYPE_HILLS
                            self.biomeColourCode[x, y] = constants.COLOR_EMERALD                            
                    elif self.rainmap[x, y] >= 0.20 and self.rainmap[x, y] < 0.33:
                        if self.drainmap[x, y] < 0.50:    # Savanna: r20-32, d0-50
                            self.biome[x, y] = constants.BIOME_TYPE_SAVANNA
                            self.biomeColourCode[x, y] = constants.COLOR_GREEN_YELLOW
                        elif self.drainmap[x, y] < 0.80: # Hills: r10-65, d50-100
                            self.biome[x, y] = constants.BIOME_TYPE_HILLS
                            self.biomeColourCode[x, y] = constants.COLOR_EMERALD
                        else:
                            self.biome[x, y] = constants.BIOME_TYPE_FOREST
                            self.biomeColourCode[x, y] = constants.COLOR_DARK_GREEN                                                          
                    elif self.rainmap[x, y] >= 0.33 and self.rainmap[x, y] < 0.66:
                        if self.drainmap[x, y] < 0.33:    # Marsh: r33-65, d0-32
                            self.biome[x, y] = constants.BIOME_TYPE_MARSH
                            self.biomeColourCode[x, y] = 0x2B2E26
                        elif self.drainmap[x, y] < 0.50:    # Shrubland: r33-65, d33-49
                            self.biome[x, y] = constants.BIOME_TYPE_SHRUBLAND
                            self.biomeColourCode[x, y] = constants.COLOR_FERN_GREEN
                        elif self.drainmap[x, y] < 0.80:
                            self.biome[x, y] = constants.BIOME_TYPE_HILLS
                            self.biomeColourCode[x, y] = constants.COLOR_EMERALD
                        else: # Hills: r10-65, d50-100                       
                            self.biome[x, y] = constants.BIOME_TYPE_FOREST
                            self.biomeColourCode[x, y] = constants.COLOR_DARK_GREEN                            
                    else: # all other rainfall amounts (0.66 - 1.00)
                        if self.drainmap[x, y] < 0.33:    # Swamp: r66-100, d0-32
                            self.biome[x, y] = constants.BIOME_TYPE_SWAMP
                            self.biomeColourCode[x, y] = constants.COLOR_AMETHYST
                        else:  # Forest: r66-100, d33-100
                            self.biome[x, y] = constants.BIOME_TYPE_FOREST
                            self.biomeColourCode[x, y] = constants.COLOR_DARK_GREEN                    
                                        
    def biomeType(self, biome):
        if biome == constants.BIOME_TYPE_WATER: 
            result = "Water"
        elif biome == constants.BIOME_TYPE_GRASSLAND: 
            result = "Grassland"
        elif biome == constants.BIOME_TYPE_DESERT_SAND: 
            result = "Sandy Desert"
        elif biome == constants.BIOME_TYPE_DESERT_ROCK: 
            result = "Rocky Desert"
        elif biome == constants.BIOME_TYPE_MOUNTAIN_LOW: 
            result = "Low Mountain"
        elif biome == constants.BIOME_TYPE_MOUNTAIN_HIGH: 
            result = "High Mountain"
        elif biome == constants.BIOME_TYPE_SAVANNA: 
            result = "Savanna"
        elif biome == constants.BIOME_TYPE_MARSH: 
            result = "Marsh"
        elif biome == constants.BIOME_TYPE_SHRUBLAND: 
            result = "Shrubland"
        elif biome == constants.BIOME_TYPE_HILLS: 
            result = "Hill"
        elif biome == constants.BIOME_TYPE_SWAMP: 
            result = "Swamp"
        elif biome == constants.BIOME_TYPE_FOREST:
            result = "Forest"
        elif biome == constants.BIOME_TYPE_DESERT_BADLANDS: 
            result = "Badland"
        elif biome == constants.BIOME_TYPE_MOUNTAIN: 
            result = "Mountain"                    
        elif biome == constants.BIOME_TYPE_UNDEFINED:
            result = "Undefined"
        else:
            result = "No, really... Undefined"
        return result


if __name__ == '__main__':
    biomes = Biomes()
    print biomes
