#!/usr/bin/env python

from numpy import *
from constants import *


class Biomes():

    def __init__(self, heightmap, rainmap, drainmap, temperature):
        self.heightmap = heightmap
        self.rainmap = rainmap
        self.drainmap = drainmap
        self.worldW = len(self.heightmap)
        self.worldH = len(self.heightmap[0])
        self.biome = zeros((self.worldW, self.worldH))
        self.biomeColourCode = zeros((self.worldW, self.worldH))

    def run(self):
        # setup or local variables
        steps = 0

        # calculate biome -- from scale of 0-400 ((oldValue-0) * (100-0)) / (400-0) + 0
        for x in range(0, self.worldW):
            for y in range(0, self.worldH):
                if self.heightmap[x, y] <= WGEN_SEA_LEVEL:    # Water: e0-99, rany, dany # 0.25 converted
                    self.biome[x, y] = BIOME_TYPE_WATER
                    self.biomeColourCode[x, y] = COLOR_BLUE
                elif self.heightmap[x, y] < 0.75 and self.rainmap[x, y] < 0.10 and self.drainmap[x, y] < 0.33:    # Desert (Sand): e100-299, r0-9, d0-32
                    self.biome[x, y] = BIOME_TYPE_DESERT_SAND
                    self.biomeColourCode[x, y] = COLOR_FLAX
                elif self.heightmap[x, y] < 0.75 and self.rainmap[x, y] < 0.10 and self.drainmap[x, y] < 0.50:    # Desert (Rock): e100-299, r0-9, d33-49
                    self.biome[x, y] = BIOME_TYPE_DESERT_ROCK
                    self.biomeColourCode[x, y] = COLOR_DARK_CHESTNUT
                elif self.heightmap[x, y] < 0.75 and self.rainmap[x, y] < 0.10 and self.drainmap[x, y] < 1.00:    # Desert (Badlands): e100-299, r0-9, d50-100
                    self.biome[x, y] = BIOME_TYPE_DESERT_BADLANDS
                    self.biomeColourCode[x, y] = COLOR_OLIVE
                elif self.heightmap[x, y] < 0.75 and self.rainmap[x, y] < 0.20 and self.drainmap[x, y] < 0.50:    # Grassland: e100-299, r10-19, d0-50
                    self.biome[x, y] = BIOME_TYPE_GRASSLAND
                    self.biomeColourCode[x, y] = COLOR_GREEN
                elif self.heightmap[x, y] < 0.75 and self.rainmap[x, y] < 0.33 and self.drainmap[x, y] < 0.50:    # Savanna: e100-299, r20-32, d0-50
                    self.biome[x, y] = BIOME_TYPE_SAVANNAH
                    self.biomeColourCode[x, y] = COLOR_GREEN_YELLOW
                elif self.heightmap[x, y] < 0.75 and self.rainmap[x, y] < 0.66 and self.drainmap[x, y] < 0.33:    # Marsh: e100-299, r33-65, d0-32
                    self.biome[x, y] = BIOME_TYPE_MARSH
                    self.biomeColourCode[x, y] = COLOR_FERN_GREEN
                elif self.heightmap[x, y] < 0.75 and self.rainmap[x, y] < 0.66 and self.drainmap[x, y] < 0.50:    # Shrubland: e100-299, r33-65, d33-49
                    self.biome[x, y] = BIOME_TYPE_SHRUBLAND
                    self.biomeColourCode[x, y] = COLOR_TAUPE_PALE
                elif self.heightmap[x, y] < 0.75 and self.rainmap[x, y] < 0.66 and self.drainmap[x, y] < 1.00:    # Hills: e100-299, r10-65, d50-100
                    self.biome[x, y] = BIOME_TYPE_HILLS
                    self.biomeColourCode[x, y] = COLOR_EMERALD
                elif self.heightmap[x, y] < 0.75 and self.rainmap[x, y] < 1.00 and self.drainmap[x, y] < 0.33:    # Swamp: e100-299, r66-100, d0-32
                    self.biome[x, y] = BIOME_TYPE_SWAMP
                    self.biomeColourCode[x, y] = COLOR_AMETHYST
                elif self.heightmap[x, y] < 0.75 and self.rainmap[x, y] < 1.00 and self.drainmap[x, y] < 1.00:    # Forest: e100-299, r66-100, d33-100
                    self.biome[x, y] = BIOME_TYPE_FOREST
                    self.biomeColourCode[x, y] = COLOR_DARK_GREEN
                elif self.heightmap[x, y] < 0.84:                                                               # Mountain (Low): e300-332, rany, dany
                    self.biome[x, y] = BIOME_TYPE_MOUNTAIN_LOW
                    self.biomeColourCode[x, y] = COLOR_GRAY
                elif self.heightmap[x, y] < 0.91:                                                               # Mountain: e333-365, rany, dany
                    self.biome[x, y] = BIOME_TYPE_MOUNTAIN
                    self.biomeColourCode[x, y] = COLOR_ASH_GRAY
                elif self.heightmap[x, y] < 0.95:                                                               # Mountain (High): e366-399, rany, dany
                    self.biome[x, y] = BIOME_TYPE_MOUNTAIN_HIGH
                    self.biomeColourCode[x, y] = COLOR_SILVER
                elif self.heightmap[x, y] == 1.00:                                                              # Mountain (Peak): e400, rany, dany
                    self.biome[x, y] = BIOME_TYPE_PEAK
                    self.biomeColourCode[x, y] = COLOR_CREAM
                else:
                    self.biome[x, y] = BIOME_TYPE_UNDEFINED
                    self.biomeColourCode[x, y] = COLOR_RED


if __name__ == '__main__':
    print "hello!"
