import pygame
import numpy as np


class Wall():
    def __init__(self, corners):
        
        orientation = corners[-1]

        self.x_start = corners[0][1] # on fait bien attention entre x et y au sens d'un graphe Vs row et col pour numpy
        self.y_start = corners[0][0]

        if orientation == 'v':
                self.width = corners[1][1] - corners[0][1]
                self.height = corners[3][0] - corners[0][0]

                self.borderPoints = []
                # lignes:
                X = list(range(corners[0][1], corners[1][1],10))
                if not corners[1][1] in X:
                    X.append(corners[1][1])

                for x in X:
                    self.borderPoints.append((x,corners[0][0]))
                    self.borderPoints.append((x,corners[2][0]))
                   
                # colonnes:
                Y = list(range(corners[0][0], corners[2][0],10))
                if not corners[2][0] in Y:
                    Y.append(corners[2][0])

                for y in Y:
                    self.borderPoints.append((corners[0][1],y))
                    self.borderPoints.append((corners[1][1],y))
                    
        elif orientation == 'h':
                self.width = corners[3][1] - corners[0][1]
                self.height = corners[1][0] - corners[0][0]

                self.borderPoints = []
                # lignes:
                X = list(range(corners[0][1], corners[2][1],10))
                if not corners[2][1] in X:
                    X.append(corners[2][1])

                for x in X:
                    self.borderPoints.append((x,corners[0][0]))
                    self.borderPoints.append((x,corners[1][0]))
                   
                # colonnes:
                Y = list(range(corners[0][0], corners[1][0],10))
                if not corners[1][0] in Y:
                    Y.append(corners[1][0])

                for y in Y:
                    self.borderPoints.append((corners[0][1],y))
                    self.borderPoints.append((corners[2][1],y))


    def distBotWall(self,bot):
        distances = []
        for point in self.borderPoints:
            distances.append([np.sqrt((bot.x-point[0])**2 + (bot.y-point[1])**2),point[0],point[1]])
        
        min_dist = min(distances, key=lambda x: x[0])
        self.dist_coll, self.x, self.y = min_dist[0], min_dist[1], min_dist[2]
        


class Room():
    def __init__(self, width, height, win):
        self.width = width
        self.height = height
        self.objects = []
        self.walls = []
        self.win = win
    
    def addObjects(self, objs):
        self.objects+=objs

    def addWall(self, corners):
        self.walls.append(Wall(corners))

    def draw_walls(self):
        for wall in self.walls:
            pygame.draw.rect(self.win, (200,200,200), (wall.x_start, wall.y_start, wall.width, wall.height))