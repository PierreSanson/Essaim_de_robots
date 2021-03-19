import pygame

from utilities import createPolygonMask
from copy import deepcopy

class Obstacle():
    def __init__(self, x, y, radius, room, color = (100,100,100), movable = False, vel = 2, margin = 2, isWall = False, positionInWall = None):
        self.isWall = isWall
        self.positionInWall = positionInWall
        self.room = room
        self.color = color
        self.x = x
        self.y = y
        self.radius = radius
        self.vel = vel
        self.movable = movable
        self.margin = margin
        self.polygonPointsAbsolute = createPolygonMask([0, 0], 10, self.radius + self.margin)
        self.polygonPoints = deepcopy(self.polygonPointsAbsolute)

        for i in range(len(self.polygonPoints)):
            self.polygonPoints[i][0] = self.polygonPointsAbsolute[i][0] + self.x
            self.polygonPoints[i][1] = self.polygonPointsAbsolute[i][1] + self.y

        self.seen = False


    def move(self, surface1):
        keys = pygame.key.get_pressed()
    
        if keys[pygame.K_LEFT] and self.x > self.vel + self.radius: 
            self.x -= self.vel

        if keys[pygame.K_RIGHT] and self.x < surface1.get_width() - self.vel - self.radius:  
            self.x += self.vel

        if keys[pygame.K_UP] and self.y > self.vel + self.radius: 
            self.y -= self.vel

        if keys[pygame.K_DOWN] and self.y < surface1.get_height() - self.radius - self.vel:
            self.y += self.vel
        
        for i in range(len(self.polygonPoints)):
            self.polygonPoints[i][0] = self.polygonPointsAbsolute[i][0] + self.x
            self.polygonPoints[i][1] = self.polygonPointsAbsolute[i][1] + self.y



    def draw(self):
        surface = self.room.surface1
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)