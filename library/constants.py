#!/usr/bin/python
#
# Constants for world generation that typically are used across multiple modules
# the main code itself.
#
#


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
