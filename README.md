WorldSynth: Synthesizing Worlds

WorldSynth uses procedural techniques to simulate real world phenomenon and render usable maps in different formats.

Version: 0.11  
License: LGPL v2 (See COPYRIGHT for more information)  
Website: http://www.mindwerks.net/projects/worldsynth  

FEATURES:
* Heightmap: generation with several algorithms
* Heatmap: based on full hemisphere or half-hemisphere (north or south)
* Wind: wind direction and strength influenced by geography
* Precipitation: based on terrain and wind currents
* Drainage: how fast water can be absorbed by terrain
* Rivers: based on rainfall and terrain
* Biomes: taking into account everything above to give natural zones of nature

REQUIREMENTS:
* Python:   >= 2.7
* PySide:   http://qt-project.org/wiki/PySide
* NumPy:    http://www.numpy.org/
* PyTables: http://www.pytables.org/
* PyPNG:    http://pythonhosted.org/pypng/index.html

INSTALLATION:
* Verify that all requirements above are met
* pip install pypng
* Untar/unzip and run worldsynth.py

CHANGELOG:

0.11.0
* Improved New/Open/Save World.
* Configuration is saved and can be read back from 'Open' World file.
* Improved Import/Export: Open any image as heightmap, export as 16-bit greyscale PNG.
* Introduce masks for various effects such as: islands.
* Python3 compatibility.
* De-couple application globals and make them configurable: sea-level can be adjusted.

0.10.0  
* Just-in-time library loading: lazy loading libraries as necessary
* Try to reduce the number of dependancies necessary to start and be able to use base functions
* Add accumulating erosion model to prevent original heightmap from being modified
* Add overflow flag to models where maps could be seamless to help 'overflow'
* Rivers can flow through edges of maps, overflow into other side
* Initial changelog
