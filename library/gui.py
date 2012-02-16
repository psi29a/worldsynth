from popup_menu import PopupMenu

class gui():
    '''Abstracted gui for worldgenerator'''
    
    def __init__(self):
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
            (
                'Load',
                'Import',
            ),
            (
                'Save',
                'Export',
                'Images',
            ),
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
                return 'self.__init__()'

        elif e.name == 'Save...':
            if e.text == 'Export':
                return 'self.exportWorld()'
        
        elif e.name == 'Load...':
            if e.text == 'Import':
                return 'self.importWorld()'            

        elif e.name == 'Actions...':
            if e.text == 'Heightmap':
                return 'self.createHeightmap()'
            elif e.text == 'Temperature':
                return 'self.createTemperature()'
            elif e.text == 'WindAndRain':
                return 'self.createWindAndRain()'
            elif e.text == 'Drainage':
                return 'self.createDrainage()'
            elif e.text == 'Rivers':
                return 'self.createRiversAndLakes()'
            elif e.text == 'Biomes':
                return 'self.createBiomes()'

        elif e.name == 'Size...':
            if e.text == 'Tiny':
                return 'self.__init__(size=128)'
            if e.text == 'Small':
                return 'self.__init__(size=256)'
            elif e.text == 'Medium':
                return 'self.__init__(size=512)'
            elif e.text == 'Large':
                return 'self.__init__(size=1024)'

        elif e.name == 'View Menu':
            if e.text == 'Height Map':
                return "self.showMap('heightmap')"
            elif e.text == 'Sea Level':
                return "self.showMap('sealevel')"
            elif e.text == 'Elevation':
                return "self.showMap('elevation')"
            elif e.text == 'Heat Map':
                return "self.showMap('heatmap')"
            elif e.text == 'Raw Heat Map':
                return "self.showMap('rawheatmap')"
            elif e.text == 'Wind Map':
                return "self.showMap('windmap')"
            elif e.text == 'Rain Map':
                return "self.showMap('rainmap')"
            elif e.text == 'Wind and Rain Map':
                return "self.showMap('windandrainmap')"
            elif e.text == 'Drainage Map':
                return "self.showMap('drainagemap')"
            elif e.text == 'River Map':
                return "self.showMap('rivermap')"
            elif e.text == 'Biome Map':
                return "self.showMap('biomemap')"
                
    def menu(self,menuType):
        method = getattr(self,menuType)
        PopupMenu(method)
        