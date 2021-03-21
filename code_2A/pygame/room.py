import pygame
import numpy as np

import obstacle as obs
from utilities import distObj


class Wall():
    def __init__(self, corners):
        
        orientation = corners[-1]

        self.x_start = corners[0][1] # on fait bien attention entre x et y au sens d'un graphe Vs row et col pour numpy
        self.y_start = corners[0][0]

        if orientation == 'v':
                self.width = corners[1][1] - corners[0][1]
                self.height = corners[3][0] - corners[0][0]

                # lignes:
                X = list(range(corners[0][1], corners[1][1],10))
                if not corners[1][1] in X:
                    X.append(corners[1][1])
                   
                # colonnes:
                Y = list(range(corners[0][0], corners[2][0],10))
                if not corners[2][0] in Y:
                    Y.append(corners[2][0])


        elif orientation == 'h':
                self.width = corners[3][1] - corners[0][1]
                self.height = corners[1][0] - corners[0][0]

                # lignes:
                X = list(range(corners[0][1], corners[2][1],10))
                if not corners[2][1] in X:
                    X.append(corners[2][1])
                   
                # colonnes:
                Y = list(range(corners[0][0], corners[1][0],10))
                if not corners[1][0] in Y:
                    Y.append(corners[1][0])

    def addObstacles(self, objs):
        self.obstacles+=objs
        


class Room():
    def __init__(self, surface1, surface2):
        self.surface1 = surface1
        self.surface2 = surface2
        # surface2 va représenter les parties explorées ou non de la carte
        self.surface2.fill((0,0,0,200))
        self.objects = [] # bots and obstacles
        self.bots = [] # only the bots
        self.obstacles = [] # only the obstacles
        self.obstacles_to_be_seen = []
        self.obstacles_seen = []
        self.walls = []
    
    def addObjects(self, objs):
        self.objects+=objs
        self.bots += objs

    def addWall(self, corners):
        self.walls.append(Wall(corners))

    def draw_walls(self):
        for wall in self.walls:
            pygame.draw.rect(self.surface1, (0,0,0), (wall.x_start, wall.y_start, wall.width, wall.height)) # mur non vu : noir (0,0,0)

        for obstacle in self.obstacles_seen:
            x = obstacle.x
            y = obstacle.y
            length = 15
            radius = obstacle.radius
            if obstacle.isWall == 'x':
                pygame.draw.rect(self.surface1, (200,200,200), (x-length//2, y, length, 1)) # mur vu : gris clair (200,200,200)
            elif obstacle.isWall == 'y':
                pygame.draw.rect(self.surface1, (200,200,200), (x, y-length//2, 1, length)) # mur vu : griselement clair (200,200,200)  

    def defineObstaclesFromWalls(self):

        obstacles = []
        radiusObstacles = 7
        spaceBetweenObstaclesCenter = 30

        
        for wall in self.walls:  
            wallsForObstacles = []

            wallsForObstacles.append([[wall.x_start, wall.y_start],[wall.x_start+wall.width-1, wall.y_start]])
            wallsForObstacles.append([[wall.x_start, wall.y_start],[wall.x_start, wall.y_start + wall.height-1]])
            wallsForObstacles.append([[wall.x_start + wall.width-1, wall.y_start],[wall.x_start + wall.width-1, wall.y_start + wall.height-1]])
            wallsForObstacles.append([[wall.x_start, wall.y_start+wall.height-1],[wall.x_start+wall.width-1, wall.y_start + wall.height-1]])
            
            for element in wallsForObstacles:
                if element[0][1] == element[1][1]:
                    y = element[0][1]
                    for x in range(element[0][0] + radiusObstacles, element[1][0], spaceBetweenObstaclesCenter):
                        obstacles.append(obs.Obstacle(x, y, radiusObstacles, self, isWall='x'))

                elif element[0][0] == element[1][0]:
                    x = element[0][0]
                    for y in range(element[0][1] + radiusObstacles, element[1][1], spaceBetweenObstaclesCenter):
                        obstacles.append(obs.Obstacle(x, y, radiusObstacles, self, isWall='y'))

            self.obstacles += obstacles
    
        self.obstacles_to_be_seen = self.obstacles
        self.objects = self.bots + self.obstacles


    def updateExploration(self):
        for obj in self.objects:
            if not isinstance(obj, obs.Obstacle):
                pygame.draw.circle(self.surface2,(0,0,0,0),(obj.x,obj.y),obj.radiusDetection)

        for obstacle in self.obstacles_to_be_seen:
            for obj in self.bots:
                if not isinstance(obj,obs.Obstacle):
                    if distObj(obstacle,obj) <= obj.radiusDetection: ### faire une fonction spéciale qui prend en charge le fait qu'on ne voit pas au delà du mur, en regardant segmentlineinter sans 
                        self.obstacles_to_be_seen.remove(obstacle)
                        self.obstacles_seen.append(obstacle)