'''Simple data loader module.

Loads data files from the "data" directory shipped with a game.

Enhancing this to handle caching etc. is left as an exercise for the reader.
'''

import os
from os.path import join as join_path

data_py = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(join_path(data_py, '..', 'data'))
path = dict(
    font  = join_path(data_dir, 'font'),
    image = join_path(data_dir, 'image'),
    map   = join_path(data_dir, 'map'),
    sound = join_path(data_dir, 'sound'),
    text  = join_path(data_dir, 'text'),
)

def filepath(typ, filename):
    '''Determine the path to a file in the data directory.
    '''
    return join_path(path[typ], filename)

def load(typ, filename, mode='rb'):
    '''Open a file in the data directory.

    "mode" is passed as the second arg to open().
    '''
    return open(filepath(typ, filename), mode)

def load_font(filename):
    return load('font', filename)

def load_image(filename):
    return load('image', filename)

def load_map(filename):
    return load('map', filename)

def load_sound(filename):
    return load('sound', filename)

def load_text(filename):
    return load('text', filename, 'r')
