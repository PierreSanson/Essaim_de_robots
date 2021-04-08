import pygame

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class Tile():
    def __init__(self, x, y, width):
        self.x = x # 
        self.y = y # coordonnées du CENTRE
        self.center = (x,y)
        self.width = width
        self.height = width # square tiles

        self.corners = [[x-self.width//2,y-self.height//2],[x+self.width//2,y-self.height//2],[x+self.width//2,y+self.height//2],[x-self.width//2,y+self.height//2]]
        self.polygon = Polygon([[x-self.width//2,y-self.height//2],[x+self.width//2,y-self.height//2],[x+self.width//2,y+self.height//2],[x-self.width//2,y+self.height//2]])
        
        self.seen = 0
        self.covered = 0
        self.obstacle = 0
        self.measured = 0

        self.containsWall = 0

        self.state = ''.join(str(e) for e in [self.seen,self.covered,self.obstacle,self.measured]) # on stocke l'état sous la forme d'une châine de caractères
        self.color = (0,0,0,0) # transparent

        #################################################################################################################
        # CATALOGUE DES ETATS #                                                                                         #
        #######################                                                                                         #
        #                                                                                                               #
        # 00-- : non vu, non couvert (UWB)                      couleur : transparent (invisible)   (0,0,0,0)           #
        # 01-- : non vu, couvert (UWB)                          couleur : blanc                     (255,255,255,100)   #
        # 100- : vu, non couvert (UWB), pas d'obstacle          couleur : orange                    (200,100,0,100)     #
        # 101- : vu, non couvert (UWB), obstacle                couleur : rouge                     (200,0,0,100)       #
        # 111- : vu et couvert, obstacle                        couleur : rouge                     (200,0,0,100)       #
        # 1100 : vu et couvert, pas d'obstacle, pas mesuré      couleur : jaune                     (200,200,0,100)     #
        # 1101 : vu et couvert, pas d'obstacle, mesuré          couleur : vert                      (0,200,0,100)       #
        #                                                                                                               #
        #################################################################################################################

        ### Probablement à sortir de cet objet qui va être créé plein de fois
        





    def update(self,surfaceToCheck,polygonsUWB,bots,color_dictionary):
        self.state_has_changed = 0
        
        # On vérifie si la case a été vue. Si oui, elle restera vue.
        if not self.seen:
            if surfaceToCheck.get_at(self.center) == (0,0,0,0):
                self.seen = 1
            # Cas particulier : cases vues partiellement à cause d'un mur, on ne peut pas se contentet de regarder le centre
            if self.containsWall:
                for corner in self.corners:
                    if surfaceToCheck.get_at(corner) == (0,0,0,0):
                        self.seen = 1

        # On vérifie si la case est couverte
        point = Point(self.center)
        for poly in polygonsUWB:
            polygonUWB = Polygon(poly)
            if polygonUWB.contains(point):
                self.covered = 1
            else:
                self.covered = 0

        # On vérifie si la case contient un obstacle
        # Si la case contient un mur, ça ne vas pas changer.
        if not self.containsWall:    
            for bot in bots:
                point = Point(bot.x,bot.y)
                if self.polygon.contains(point):
                    self.obstacle = 1
                else:
                    self.obstacle = 0

        ###
        # Pour ce qui est de la mesure, le changement de valeur doit venir du robot mesureur.
        # A modifier avant de faire appel à cet update donc, sinon l'état de la case ne sera pas correctement mis à jour.
        ###

        self.state = ''.join(str(e) for e in [self.seen,self.covered,self.obstacle,self.measured])

        # mise à jour de la couleur
        self.color = color_dictionary[self.state]



class Grid():
    def __init__(self,room,xMeasurer,yMeasurer,tileWidth):
        self.room = room
        self.tileWidth = tileWidth
        self.tiles = {}
        
        # Construction de toute la grille une bonne fois pour toutes
        i = 0
        while xMeasurer - i*tileWidth > 0:
            self.tiles[(xMeasurer - i*tileWidth,yMeasurer)] = Tile(xMeasurer - i*tileWidth,yMeasurer,self.tileWidth)

            j = 0
            while yMeasurer - j*tileWidth > 0:
                self.tiles[(xMeasurer - i*tileWidth,yMeasurer - j*tileWidth)] = Tile(xMeasurer - i*tileWidth,yMeasurer - j*tileWidth,self.tileWidth)
                j += 1

            j = 1
            while yMeasurer + j*tileWidth < room.height:
                self.tiles[(xMeasurer - i*tileWidth,yMeasurer + j*tileWidth)] = Tile(xMeasurer - i*tileWidth,yMeasurer + j*tileWidth,self.tileWidth)
                j += 1

            i += 1

        i = 1
        while xMeasurer + i*tileWidth < room.width:
            self.tiles[(xMeasurer + i*tileWidth,yMeasurer)] = Tile(xMeasurer + i*tileWidth,yMeasurer,self.tileWidth)

            j = 1
            while yMeasurer - j*tileWidth > 0:
                self.tiles[(xMeasurer + i*tileWidth,yMeasurer - j*tileWidth)] = Tile(xMeasurer + i*tileWidth,yMeasurer - j*tileWidth,self.tileWidth)
                j += 1

            j = 1
            while yMeasurer + j*tileWidth < room.height:
                self.tiles[(xMeasurer + i*tileWidth,yMeasurer + j*tileWidth)] = Tile(xMeasurer + i*tileWidth,yMeasurer + j*tileWidth,self.tileWidth)
                j += 1

            i += 1

        

        # On cherche toutes les cases qui contiennent un mur
        obstacles = self.room.obstacles
        for tile in self.tiles.values():
            k = 0
            while not tile.containsWall and k < len(obstacles):
                obs = obstacles[k]
                point = Point([obs.x,obs.y])
                if tile.polygon.contains(point):
                    tile.containsWall = 1
                    tile.obstacle = 1
                k += 1

        # Dictionnaire des couleurs des cases en fonction des états
        self.color_dictionary = {
            '0000' : (0,0,0,0),
            '0001' : (0,0,0,0),
            '0010' : (0,0,0,0),
            '0011' : (0,0,0,0),
            '0100' : (255,255,255,100),
            '0101' : (255,255,255,100),
            '0110' : (255,255,255,100),
            '0111' : (255,255,255,100),
            '1000' : (200,100,0,100),
            '1001' : (200,100,0,100),
            '1010' : (200,0,0,100),
            '1011' : (200,0,0,100),
            '1110' : (200,0,0,100),
            '1111' : (200,0,0,100),
            '1100' : (200,200,0,100),
            '1101' : (0,200,0,100)
        }

        # Initialisation du graphe 
        ############
        
        ############


    def update(self,polygonUWB):
        for tile in self.tiles.values():
            tile.update(self.room.surface2,polygonUWB,self.room.bots,self.color_dictionary)
    
    def draw(self,surface):
        for tile in self.tiles.values():
            pygame.draw.rect(surface, tile.color, (tile.corners[0][0], tile.corners[0][1], tile.width, tile.height),width = 2)