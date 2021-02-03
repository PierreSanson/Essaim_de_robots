import pygame

class Room():
    def __init__(self, width, height, win):
        self.width = width
        self.height = height
        self.objects = []
        self.walls = []
        self.win = win
    
    def addObjects(self, objs):
        self.objects+=objs

    def addWall(self, startCoords, endCoords):
        self.walls.append([startCoords, endCoords])

    def draw(self):
        for line in self.walls:
            pygame.draw.line(self.win, (255,255,255), (line[0][0], line[0][1]), (line[1][0], line[1][1]))
