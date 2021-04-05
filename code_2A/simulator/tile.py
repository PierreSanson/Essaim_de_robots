from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

class Tile():
    def __init__(self, x, y, width, seen = 0, covered = 0, obstacle = 0, measured = 0):
        self.x = x # 
        self.y = y # coordonnées du coin supérieur gauche (cf. origine des axes dans pygame)
        self.width = width
        self.height = width # square tiles
        self.center = (self.x + width//2, self.y + height//2)

        self.polygon = 

        self.seen = seen
        self.covered = covered
        self.obstacle = obstacle
        self.measured = measured
        self.state = ''.join(str(e) for e in [self.seen,self.covered,self.obstacle,self.measured]) # on stocke l'état sous la forme d'une châine de caractères
        self.color = (0,0,0,0) # transparent

        #################################################################################################################
        # CATALOGUE DES ETATS #                                                                                         #
        #######################                                                                                         #
        #                                                                                                               #
        # 00-- : non vu, non couvert (UWB)                      couleur : transparent (invisible)   (0,0,0,0)           #
        # 01-- : non vu, couvert (UWB)                          couleur : gris                      (200,200,200,40)    #
        # 100- : vu, non couvert (UWB), pas d'obstacle          couleur : orange                    (200,100,0,100)     #
        # 101- : vu, non couvert (UWB), obstacle                couleur : rouge                     (200,0,0,100)       #
        # 111- : vu et couvert, obstacle                        couleur : rouge                     (200,0,0,100)       #
        # 1100 : vu et couvert, pas d'obstacle, pas mesuré      couleur : jaune                     (200,200,0,100)     #
        # 1101 : vu et couvert, pas d'obstacle, mesuré          couleur : vert                      (0,200,0,100)       #
        #                                                                                                               #
        #################################################################################################################

        ### Probablement à sortir de cet objet qui va être créé plein de fois
        self.color_dictionary = {
            '0000' : (0,0,0,0),
            '0001' : (0,0,0,0),
            '0010' : (0,0,0,0),
            '0011' : (0,0,0,0),
            '0100' : (200,200,200,40),
            '0101' : (200,200,200,40),
            '0110' : (200,200,200,40),
            '0111' : (200,200,200,40),
            '1000' : (200,100,0,100),
            '1001' : (200,100,0,100),
            '1010' : (200,0,0,100),
            '1011' : (200,0,0,100),
            '1110' : (200,0,0,100),
            '1111' : (200,0,0,100),
            '1100' : (200,200,0,100),
            '1101' : (0,200,0,100)
        }





    def update(self,surfaceToCheck,polygonUWB,room):
        # On vérifie si la case a été vue. Si oui, elle restera vue.
        if not self.seen:
            if surfaceToCheck.get_at(self.center) == (0,0,0,0):
                self.seen = 1

        # On vérifie si la case est couverte
        point = Point(self.center[0],self.center[1])
        if polygonUWB.contains(point):
            self.covered = 1
        else:
            self.covered = 0

        # On vérifie si la case contient un obstacle
        # Si la case contient un mur, ça ne vas pas changer.
        if not self.containsWall:
            for bot in room.bots:
                point = Point(bot.x,bot.y)
                if self.polygon.contains(point):
                    self.obstacle = 1

        # Pour ce qui est de la mesure, le changement de valeur doit venir du robot mesureur.

        self.state = ''.join(str(e) for e in [self.seen,self.covered,self.obstacle,self.measured])

        # mise à jour de la couleur
        self.color = self.color_dictionary[self.state]

