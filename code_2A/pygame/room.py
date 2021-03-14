import pygame
import numpy as np

import obstacle as obs


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
        


class Room():
    def __init__(self, width, height, win):
        self.width = width
        self.height = height
        self.objects = []
        self.walls = []
        self.obstaclesConstruction = []
        self.win = win
    
    def addObjects(self, objs):
        self.objects+=objs

    def addWall(self, corners):
        self.walls.append(Wall(corners))

    def draw_walls(self):
        for wall in self.walls:
            pygame.draw.rect(self.win, (200,200,200), (wall.x_start, wall.y_start, wall.width, wall.height))

    def defineObstaclesFromWalls(self):

        wallsForObstacles = []
        
        for wall in self.walls:  
            wallsForObstacles.append([[wall.x_start, wall.y_start],[wall.x_start+wall.width, wall.y_start]])
            wallsForObstacles.append([[wall.x_start, wall.y_start],[wall.x_start, wall.y_start + wall.height]])
            wallsForObstacles.append([[wall.x_start + wall.width, wall.y_start],[wall.x_start + wall.width, wall.y_start + wall.height]])
            wallsForObstacles.append([[wall.x_start, wall.y_start+wall.height],[wall.x_start+wall.width, wall.y_start + wall.height]])
            
        radiusObstacles = 2
        spaceBetweenObstaclesCenter = 15
        obstacles = []
        for wall in wallsForObstacles:
            if wall[0][1] == wall[1][1]:
                y = wall[0][1]
                for x in range(wall[0][0] + radiusObstacles, wall[1][0], spaceBetweenObstaclesCenter):
                    obstacles.append(obs.Obstacle(x, y, radiusObstacles, self, isWall='x'))

            elif wall[0][0] == wall[1][0]:
                x = wall[0][0]
                for y in range(wall[0][1] + radiusObstacles, wall[1][1], spaceBetweenObstaclesCenter):
                    obstacles.append(obs.Obstacle(x, y, radiusObstacles, self, isWall='y'))

        self.addObjects(obstacles)