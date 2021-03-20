import pygame
import numpy as np

import obstacle as obs
import measuringBot as mb
from utilities import distObj


class Wall():
    def __init__(self, corners):

        self.obstacles = []
        self.obstacles_seen = []
        self.Xs = []
        self.Ys = []
        
        orientation = corners.pop()
        self.corners = corners
        
        self.x_start = corners[0][1] # on fait bien attention entre x et y au sens d'un graphe Vs row et col pour numpy
        self.y_start = corners[0][0]


        ### ATTENTION : A CE MOMENT, LES COINS SONT ENCORE AU FORMAT  (ROW,COL)
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

        ### UNE FOIS LE TRAITEMENT EFFECTUE, ON REVIENT AU FORMAT (X,Y)
        for corner in self.corners:
            corner.reverse()


    def visibleForBot(self,bot):
        for obstacle in self.obstacles :
            if distObj(obstacle,bot) <= bot.radiusDetection:
                return True
        return False


    def saveObstaclesMainCoord(self):
        # on cherche toutes les coordonnées uniques
        tempXs = []
        tempYs = []
    
        for obstacle in self.obstacles:
            x = obstacle.x
            y = obstacle.y

            if not x in tempXs:
                tempXs.append(x)

            if not y in tempYs:
                tempYs.append(y)

        self.Xs = [min(tempXs),max(tempXs)]
        self.Ys = [min(tempYs),max(tempYs)]
        

    
        


class Room():
    def __init__(self, walls_corners, surface1, surface2):
        self.walls = []
        self.defWalls(walls_corners)

        self.bots = []

        self.surface1 = surface1
        self.surface2 = surface2
        # surface2 va représenter les parties explorées ou non de la carte
        self.surface2.fill((0,0,0,200))

        self.width = surface1.get_width()
        self.height = surface1.get_height()

        obstacles = self.defineObstaclesFromWalls()
        self.obstacles = obstacles

        self.objects = self.bots + self.obstacles

        for wall in self.walls:
            wall.saveObstaclesMainCoord()



    def addBots(self,bots):
        self.bots += bots 
        self.objects += bots

    def defWalls(self, walls_corners):
        for corners in walls_corners:
            self.walls.append(Wall(corners))

    def draw_walls(self):
        for wall in self.walls:
            pygame.draw.rect(self.surface1, (0,0,0), (wall.x_start, wall.y_start, wall.width, wall.height)) # mur non vu : noir (0,0,0)

            for obstacle in wall.obstacles_seen:
                x = obstacle.x
                y = obstacle.y
                length = 15
                if obstacle.isWall == 'x':
                    pygame.draw.rect(self.surface1, (200,200,200), (x-length//2, y, length, 1)) # mur vu : gris clair (200,200,200)
                elif obstacle.isWall == 'y':
                    pygame.draw.rect(self.surface1, (200,200,200), (x, y-length//2, 1, length)) # mur vu : griselement clair (200,200,200)
                

    def defineObstaclesFromWalls(self):

        obstacles = []
        radiusObstacles = 2
        spaceBetweenObstaclesCenter = 15

        
        for wall in self.walls: 
            wall_obstacles = [] 

            top_line = [[wall.x_start, wall.y_start],[wall.x_start+wall.width-1, wall.y_start]]
            left_line = [[wall.x_start, wall.y_start],[wall.x_start, wall.y_start + wall.height-1]]
            right_line = [[wall.x_start + wall.width-1, wall.y_start],[wall.x_start + wall.width-1, wall.y_start + wall.height-1]]
            bot_line = [[wall.x_start, wall.y_start+wall.height-1],[wall.x_start+wall.width-1, wall.y_start + wall.height-1]]
            
            y = top_line[0][1]
            for x in range(top_line[0][0] + radiusObstacles, top_line[1][0], spaceBetweenObstaclesCenter):
                wall_obstacles.append(obs.Obstacle(x, y, radiusObstacles, self,isWall='x', spacing = spaceBetweenObstaclesCenter, positionInWall='top'))

            y = bot_line[0][1]
            for x in range(bot_line[0][0] + radiusObstacles, bot_line[1][0], spaceBetweenObstaclesCenter):
                wall_obstacles.append(obs.Obstacle(x, y, radiusObstacles, self,isWall='x', spacing = spaceBetweenObstaclesCenter, positionInWall='bot'))
                
            x = left_line[0][0]
            for y in range(left_line[0][1] + radiusObstacles, left_line[1][1], spaceBetweenObstaclesCenter):
                wall_obstacles.append(obs.Obstacle(x, y, radiusObstacles, self,isWall='y', spacing = spaceBetweenObstaclesCenter, positionInWall='left'))

            x = right_line[0][0]
            for y in range(right_line[0][1] + radiusObstacles, right_line[1][1], spaceBetweenObstaclesCenter):
                wall_obstacles.append(obs.Obstacle(x, y, radiusObstacles, self, isWall='y', spacing = spaceBetweenObstaclesCenter, positionInWall='right'))

            obstacles += wall_obstacles
            wall.obstacles = wall_obstacles
    
        return obstacles


    def updateExploration(self):
        for bot in self.bots:
            # détection des murs et des zones visibles
            wallsInView, obstaclesInView, visibleSurface = bot.vision()

            # affichage de la vision
            self.surface2.blit(visibleSurface, (0,0), special_flags=pygame.BLEND_RGBA_MIN)

            for wall in wallsInView:
                for obstacle in obstaclesInView[wall]:
                    if obstacle not in wall.obstacles_seen :
                        wall.obstacles_seen.append(obstacle)       