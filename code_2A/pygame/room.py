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
        

    def visibleObstacles(self,bot):
        visibleObs = []
        visibleSides = []

        if bot.x > max(self.Xs):
            if not 'right' in visibleSides:
                visibleSides.append('right')
                #print('yo')

        if bot.x < min(self.Xs):
            if not 'left' in visibleSides:
                visibleSides.append('left')
                #print('wesh')

        # pour Y ce qui est écrit ici ne semble pas logique, mais en fait il faut se souvenir qu'on indexe depuis le coin en haut à gauche
        if bot.y > max(self.Ys):
            if not 'bot' in visibleSides:
                visibleSides.append('bot')
                #print('yep')

        if bot.y < min(self.Ys):
            if not 'top' in visibleSides:
                visibleSides.append('top')
                #print('alors')

        for obstacle in self.obstacles:
            if isinstance(bot,mb.MeasuringBot):
                #print('1:',obstacle.positionInWall in visibleSides,'2:',distObj(obstacle,bot) < bot.radiusDetection)
                #print(distObj(obstacle,bot))
                if obstacle.positionInWall in visibleSides and distObj(obstacle,bot) <= bot.radiusDetection:
                    visibleObs.append(obstacle)
        
        #print(visibleObs)
        return visibleObs
        


class Room():
    def __init__(self, walls_corners, surface1, surface2):
        self.walls = []
        self.defWalls(walls_corners)

        self.bots = []

        self.surface1 = surface1
        self.surface2 = surface2
        # surface2 va représenter les parties explorées ou non de la carte
        self.surface2.fill((0,0,0,200))

        obstacles = self.defineObstaclesFromWalls()
        self.obstacles = obstacles  # only the obstacles
        # self.obstacles_to_be_seen = obstacles
        # self.obstacles_seen = []

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
                wall_obstacles.append(obs.Obstacle(x, y, radiusObstacles, self, color=(255,0,0),isWall='x', positionInWall='top'))

            y = bot_line[0][1]
            for x in range(bot_line[0][0] + radiusObstacles, bot_line[1][0], spaceBetweenObstaclesCenter):
                wall_obstacles.append(obs.Obstacle(x, y, radiusObstacles, self, color=(0,255,0),isWall='x', positionInWall='bot'))
                
            x = left_line[0][0]
            for y in range(left_line[0][1] + radiusObstacles, left_line[1][1], spaceBetweenObstaclesCenter):
                wall_obstacles.append(obs.Obstacle(x, y, radiusObstacles, self, color=(0,0,255),isWall='y', positionInWall='left'))

            x = right_line[0][0]
            for y in range(right_line[0][1] + radiusObstacles, right_line[1][1], spaceBetweenObstaclesCenter):
                wall_obstacles.append(obs.Obstacle(x, y, radiusObstacles, self, isWall='y', positionInWall='right'))

            obstacles += wall_obstacles
            wall.obstacles = wall_obstacles
    
        return obstacles


    def updateExploration(self):
        for bot in self.bots:
            # affichage de la vision
            pygame.draw.circle(self.surface2,(0,0,0,0),(bot.x,bot.y),bot.radiusDetection)


            # détection des murs
            wallsInView, obstaclesInView = bot.vision()
            for wall in wallsInView:
                for obstacle in obstaclesInView[wall]:
                    wall.obstacles_seen.append(obstacle)       