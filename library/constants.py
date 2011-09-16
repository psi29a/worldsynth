#!/usr/bin/python
#
# Constants for world generation that typically are used across multiple modules
# the main code itself.
#
#

BIOME_TYPE_UNDEFINED       = 0
BIOME_TYPE_WATER           = 1
BIOME_TYPE_GRASSLAND       = 2
BIOME_TYPE_FOREST          = 3
BIOME_TYPE_DESERT_SAND     = 4
BIOME_TYPE_DESERT_ROCK     = 5
BIOME_TYPE_MOUNTAIN_LOW    = 6
BIOME_TYPE_MOUNTAIN_HIGH   = 7
BIOME_TYPE_SAVANNAH        = 8
BIOME_TYPE_MARSH           = 9
BIOME_TYPE_SHRUBLAND       = 10
BIOME_TYPE_HILLS           = 11
BIOME_TYPE_SWAMP           = 12
BIOME_TYPE_DESERT_BADLANDS = 13
BIOME_TYPE_MOUNTAIN        = 14
BIOME_TYPE_MOUNTAIN_PEAK   = 15

WGEN_HEMISPHERE_NORTH   = 1
WGEN_HEMISPHERE_EQUATOR = 2
WGEN_HEMISPHERE_SOUTH   = 3

WGEN_SEA_LEVEL = 0.333

WIND_OFFSET = 180
WIND_PARITY = -1 # -1 or 1
WGEN_WIND_RESOLUTION = 4 # 1 is perfect, higher = rougher
WGEN_RAIN_FALLOFF = 0.2 # Default 0.2 - less for less rain, more for more rain
WGEN_WIND_GRAVITY = 0.975

TEMPERATURE_BAND_RESOLUTION = 2 # 1 is perfect, higher = rougher
