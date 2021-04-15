import numpy as np
import pygame

from igraph import *
from igraph.drawing import graph

from measuringBot import MeasuringBot

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
        self.has_changed = False

        self.state = ''.join(str(e) for e in [self.seen,self.covered,self.obstacle,self.measured]) # on stocke l'état sous la forme d'une châine de caractères
        self.color = (0,0,0,0) # transparent
        self.graph_status = 0

        # Metriques
        self.history = [(self.seen,self.covered,self.obstacle,self.measured)]
        self.nbVisits = 0




        #################################################################################################################
        # CATALOGUE DES ETATS #                                                                                         #
        #######################                                                                                         #
        #                                                                                                               #
        # 00-- : non vu, non couvert (UWB)                      couleur : transparent (invisible)   (0,0,0,0)           #
        # 01-- : non vu, couvert (UWB)                          couleur : blanc                     (255,255,255,100)   #
        # 1000 : vu, non couvert (UWB), pas d'obstacle          couleur : orange                    (200,100,0,100)     #
        # 101- : vu, non couvert (UWB), obstacle                couleur : rouge                     (200,0,0,100)       #
        # 111- : vu et couvert, obstacle                        couleur : rouge                     (200,0,0,100)       #
        # 1100 : vu et couvert, pas d'obstacle, pas mesuré      couleur : jaune                     (200,200,0,100)     #
        # 1101 : vu et couvert, pas d'obstacle, mesuré          couleur : vert                      (0,200,0,100)       #
        # 1001 : vu et plus couvert, déjà mesuré                couleur : vert                      (0,200,0,100)       #
        #                                                                                                               #
        #################################################################################################################



    def update(self,surfaceVision,surfaceUWB,bots,color_dictionary,graph_status_dictionary):

        self.has_changed = False
        oldState = self.state

        # On vérifie si la case a été vue. Si oui, elle restera vue.
        if not self.seen:
            if surfaceVision.get_at(self.center) == (0,0,0,0): # deuxième condition pour éviter cases jaunes au passage des bots UWB
                self.seen = 1
            # Cas particulier : cases vues partiellement à cause d'un mur, on ne peut pas se contenter de regarder le centre
            if self.containsWall:
                for corner in self.corners:
                    if surfaceVision.get_at(corner) == (0,0,0,0):
                        self.seen = 1

        # On vérifie si la case est couverte
        if surfaceUWB.get_at(self.center) == (0, 0, 200, 60): # cf fonction updateUWBcoverArea de la classe Room
            self.covered = 1
        else:
            self.covered = 0

        # On vérifie si la case contient un obstacle
        # Si la case contient un mur, ça ne vas pas changer.
        if not self.containsWall:
            if self.UWBbotInTile(bots): # coûteux ?
                self.obstacle = 1
            else:
                self.obstacle = 0

        self.history.append((self.seen,self.covered,self.obstacle,self.measured))
        self.state = ''.join(str(e) for e in [self.seen,self.covered,self.obstacle,self.measured])
        if self.state != oldState:
            self.has_changed = True

        # mise à jour de la couleur
        self.color = color_dictionary[self.state]
        self.graph_status = graph_status_dictionary[self.state]

    
    def UWBbotInTile(self,bots):
        for bot in bots:
            if not isinstance(bot,MeasuringBot):
                point = Point(bot.x,bot.y)
                if self.polygon.contains(point):
                    return True
        return False




class Grid():
    def __init__(self,room,measuringBot,tileWidth=50):
        self.room = room
        self.tileWidth = tileWidth
        self.tiles = {}

        self.measuringBot = measuringBot
        self.oldObjective = measuringBot.objective

        xMeasurer = measuringBot.x
        yMeasurer = measuringBot.y
        self.origin = (xMeasurer,yMeasurer)

        # Initialisation du graphe 
        self.graph = {}
        self.graphLinks = []
        self.adjacencyList = {}

        # Metriques
        self.surface = 0
        self.pathLength = 0

        
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
        for coord in self.tiles:
            k = 0
            while not self.tiles[coord].containsWall and k < len(obstacles):
                obs = obstacles[k]
                point = Point([obs.x,obs.y])
                if self.tiles[coord].polygon.contains(point):
                    self.tiles[coord].containsWall = 1
                    self.tiles[coord].obstacle = 1
                k += 1


        # On définit l'intérieur de la salle
        inside = self.findCluster(self.origin)        


        # On nettoie les objets Tile, pour ne pas conserver de cases inutiles (ie on supprime toutes les cases extérieures, mais on garde les murs pour affichage)
        # On crée un noeud dans le graphe pour toutes les cases d'intérieur
        coordinates = list(self.tiles.keys())
        for coord in coordinates:
            if coord in inside:
                self.graph[coord] = 0 # création des noeuds
                self.surface += 1
            else :
                if self.tiles[coord].containsWall == 0: # toute case qui ne sera pas un noeud du graphe et ne contient pas de mur est inutile
                    del self.tiles[coord]

        

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
            '1000' : (200,100,0,200),
            '1001' : (0,200,0,200),
            '1010' : (200,0,0,200),
            '1011' : (200,0,0,200),
            '1110' : (200,0,0,200),
            '1111' : (200,0,0,200),
            '1100' : (200,200,0,200),
            '1101' : (0,200,0,200)
        }

        # Dictionnaire des couleurs des cases en fonction des états
        self.graph_status_dictionary = {
            '0000' : 0,
            '0001' : 0,
            '0010' : 0,
            '0011' : 0,
            '0100' : 0,
            '0101' : 0,
            '0110' : 0,
            '0111' : 0,
            '1000' : 2,
            '1001' : 1,
            '1010' : -1,
            '1011' : -1,
            '1110' : -1,
            '1111' : -1,
            '1100' : 0.5,
            '1101' : 1
        }


    # Méthode pour récupérer les métriques à la fin
    def get_metrics(self):
        # Nombre de cases mesurées
        measuredTiles = 0

        # Longueur (en cases du parcours):
        pathLength = 0

        # Historique des états de chacune des cases :
        history = {}

        # Nombre de passages par case :
        visitsPerTile = {}

        # Calcul 
        for coord in self.tiles:
            if self.tiles[coord].measured == 1:
                measuredTiles += 1

            history[coord] = self.tiles[coord].history

            tmp = self.tiles[coord].nbVisits
            visitsPerTile[coord] = tmp
            pathLength += tmp

        return measuredTiles, self.surface, pathLength, history, visitsPerTile


    # Méthode utilisée pour détecter un ensemble de cases connectées (non interrompues par un mur)
    def findCluster(self,start):
        cluster = []
        neighbours = []

        straight, diag = self.getNeighbours(start)
        tmp = straight + diag
        for coord in tmp:
            if 0 <= coord[0] <= self.room.width and 0 <= coord[1] <= self.room.height and self.tiles[coord].containsWall == 0:
                neighbours.append(coord)
        
        while neighbours != []:
            current = neighbours.pop()
            cluster.append(current)
            straight, diag = self.getNeighbours(current)
            tmp = straight + diag
            for coord in tmp:
                if not coord in neighbours and not coord in cluster: 
                    if 0 <= coord[0] <= self.room.width and 0 <= coord[1] <= self.room.height and self.tiles[coord].containsWall == 0:
                        neighbours.append(coord)
        
        return cluster


    ### Méthodes pour la grille
    def update(self,surfaceUWB,status):
        # Pour ce qui est de la mesure, le changement de valeur doit venir du robot mesureur.
        # Une case a été mesurée si le robot a changé d'objectif
        if status == "movingMeasuringBot" and self.measuringBot.objective != None:
            if self.measuringBot.objective != self.oldObjective:
                self.tiles[tuple(self.measuringBot.objective)].measured = 1
                self.tiles[tuple(self.measuringBot.objective)].nbVisits += 1 ###### à vérifier, pathLength n'a pas la bonne valeur 

        self.oldObjective = self.measuringBot.objective        

        for coord in self.tiles:
            self.tiles[coord].update(self.room.surface2,surfaceUWB,self.room.bots,self.color_dictionary,self.graph_status_dictionary)
            self.graph[coord] = self.tiles[coord].graph_status
            if self.tiles[coord].has_changed:
                self.updateNeighOneNode(coord)
            if self.graph[coord] == -1:
                self.removeNodeFromGraph(coord)

    
    def draw(self,surface):
        for tile in self.tiles.values():
            pygame.draw.rect(surface, tile.color, (tile.corners[0][0], tile.corners[0][1], tile.width, tile.height),width = 1)


    ### Méthodes pour le graphe

    def getNeighbours(self, coord):
        x,y = coord
        w = self.tileWidth
        coordLeft = (x-w, y)
        coordRight = (x+w, y)
        coordTop = (x, y-w)
        coordBottom = (x, y+w)
        coordTopLeft = (x-w, y-w)
        coordTopRight = (x+w, y-w)
        coordBottomRight = (x+w, y+w)
        coordBottomLeft= (x-w, y+w)
        coordsStraight = [coordLeft, coordRight, coordTop,coordBottom]
        coordsDiag = [coordTopLeft, coordTopRight, coordBottomRight, coordBottomLeft]
        
        return coordsStraight,coordsDiag


    def updateNeighOneNode(self, coord):
        
        coordsStraight,coordsDiag = self.getNeighbours(coord)

        for neigh in coordsStraight:
            if neigh in self.graph:
                if self.graph[neigh] == 0.5 or self.graph[neigh] == 1:
                    if (coord, neigh) not in self.graphLinks and (neigh, coord) not in self.graphLinks:
                        self.graphLinks.append((coord, neigh))
                    if coord not in self.adjacencyList:
                        self.adjacencyList[coord] = [(neigh, 1)]
                    else:
                        if neigh not in self.adjacencyList[coord]:
                            self.adjacencyList[coord].append((neigh,1))
                    if neigh not in self.adjacencyList:
                        self.adjacencyList[neigh] = [(coord,1)]
                    else:
                        if coord not in self.adjacencyList[neigh]:
                            self.adjacencyList[neigh].append((coord,1))

        for neigh in coordsDiag:
            if neigh in self.graph:
                if self.graph[neigh] == 0.5 or self.graph[neigh] == 1:
                    if (coord, neigh) not in self.graphLinks and  (neigh, coord) not in self.graphLinks:
                        self.graphLinks.append((coord, neigh))
                    if coord not in self.adjacencyList:
                        self.adjacencyList[coord] = [(neigh, np.sqrt(2))]
                    else:
                        if neigh not in self.adjacencyList[coord]:
                            self.adjacencyList[coord].append((neigh,np.sqrt(2)))
                    if neigh not in self.adjacencyList:
                        self.adjacencyList[neigh] = [(coord,np.sqrt(2))]
                    else:
                        if coord not in self.adjacencyList[neigh]:
                            self.adjacencyList[neigh].append((coord,np.sqrt(2)))           


    def removeNodeFromGraph(self, coord):
        self.adjacencyList[coord] = []
        coordsStraight,coordsDiag = self.getNeighbours(coord)
        neighbours = coordsStraight + coordsDiag
        for neigh in neighbours:
            if neigh in self.adjacencyList:
                if coord in self.adjacencyList[neigh]:
                    self.adjacencyList[neigh].remove(coord)


    def drawGraph(self):
        g = Graph()
        g.add_vertices(len(self.graph))
        g.vs["name"] = list(self.graph.keys())
        for neighbours in self.graphLinks:
            v1 = g.vs['name'].index(neighbours[0])
            v2 = g.vs['name'].index(neighbours[1])
            g.add_edge(v1, v2)
        g.vs["label"] = g.vs["name"]

        layout = g.layout("fr")
        plot(g, layout = layout)
        