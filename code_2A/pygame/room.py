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

    def addWall(self, corners):
        self.walls.append(corners)

    def draw_walls(self):
        for corners in self.walls:
            orientation = corners.pop()

            x_start = corners[0][1] # on fait bien attention entre x et y au sens d'un graphe Vs row et col pour numpy
            y_start = corners[0][0]

            if orientation == 'v':
                width = corners[1][1] - corners[0][1]
                height = corners[3][0] - corners[0][0]
            elif orientation == 'h':
                width = corners[3][1] - corners[0][1]
                height = corners[1][0] - corners[0][0]
            
            pygame.draw.rect(self.win, (255,100,100), x_start, y_start, width, height)
