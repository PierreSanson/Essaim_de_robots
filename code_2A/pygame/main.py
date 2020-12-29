import lidarBot as lb

import pygame

import random

pygame.init()

winWidth = 1920
winHeight = 1080
win = pygame.display.set_mode((winWidth,winHeight))
surface1 = pygame.Surface((winWidth,winHeight),  pygame.SRCALPHA) 

pygame.display.set_caption("First Game")

clock = pygame.time.Clock()
hz = 144

x = 60
y = 60
radius = 20
vel = 5*(60/hz)



class Room():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.objects = []
    
    def addObjects(self, objs):
        self.objects+=objs


room = Room(winWidth, winHeight)

def demos(nb = 1):

    if nb == 1 :
        lidarBots = [lb.LidarBot(x, y + i*100 , radius, room, [x + 1850, y + i*50], randomObjective = True, randomInterval = 5) for i in range(10)]

        room.addObjects(lidarBots)

    elif nb == 2 :
        lidarBots = [lb.LidarBot(x+350, y +300 + i*50 , radius, room, [x + 1800, y + 50 + i*50], randomObjective = False) for i in range(1)]
        obstacles = [lb.Obstacle(x+ 300 +50*i , y , 20, room) for i in range(6)]
        obstacles2 = [lb.Obstacle(x+ 300 +50*i , y+450 , 20, room) for i in range(6)]
        obstacles3 = [lb.Obstacle(x+ 600 , y+i*50, 20, room) for i in range(10)]

        room.addObjects(lidarBots + obstacles + obstacles2 + obstacles3)

    elif nb == 3 :
        lidarBot = lb.LidarBot(x, y , radius, room, [x + 1850, y+950])
        lidarBot2 = lb.LidarBot(x+1850, y +950, radius, room, [x, y+100])
        lidarBot3 = lb.LidarBot(x+1850, y +100, radius, room, [x, y+950])
        lidarBot4 = lb.LidarBot(x, y +950, radius, room, [x + 1850, y+100])
        lidarBots = [lidarBot, lidarBot2, lidarBot3, lidarBot4]
        obstacles = [lb.Obstacle(random.randrange(150, 1800) , random.randrange(0, 1050), 30, room) for i in range(50)]
        room.addObjects(lidarBots + obstacles)

    elif nb == 4 :
        lidarBots = [lb.LidarBot(x, y + i*100 , radius, room, [random.randrange(150, 1800),random.randrange(0, 1050)], randomObjective = True, randomInterval = 10) for i in range(5)]
        obstacles = [lb.Obstacle(x + 300, y + 300, 50, room, movable = True) for i in range(1)]

        room.addObjects(lidarBots + obstacles)




def redrawGameWindow(win, surface1):
    win.fill((0,0,0))
    surface1.fill((255,255,255,64))  
    for obj in room.objects:
        obj.draw(win, surface1)
    win.blit(surface1, (0,0))
    pygame.display.update() 


if __name__ == "__main__":
    demos(4)

    run = True 
    while run:
        clock.tick(hz)
        redrawGameWindow(win, surface1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        for obj in room.objects:
            if isinstance(obj, lb.LidarBot) or (isinstance(obj, lb.Obstacle) and obj.movable):
                obj.move(surface1)

    
    
pygame.quit()
