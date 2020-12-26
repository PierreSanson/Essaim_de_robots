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

lidarBot = lb.LidarBot(x, y , radius, room, [x + 1850, y+950])
lidarBot2 = lb.LidarBot(x+1850, y +950, radius, room, [x, y+100])
lidarBot3 = lb.LidarBot(x+1850, y +100, radius, room, [x, y+950])
lidarBot4 = lb.LidarBot(x, y +950, radius, room, [x + 1850, y+100])

lidarBots = [lb.LidarBot(x, y + i*50 , radius, room, [x + 1850, y + i*50], randomObjective = True) for i in range(30)]

# obstacles = [lb.Obstacle(random.randrange(150, 1800) , random.randrange(0, 1050), 30, room, movable = True, vel = vel)]

# obstacles = [lb.Obstacle(random.randrange(150, 1800) , random.randrange(0, 1050), 30, room) for i in range(150)]
# obstacles2 = [lb.Obstacle(random.randrange(150, 1800) , random.randrange(0, 1050), 10, room) for i in range(100)]

# obstacles = [lb.Obstacle(x+ 100 +50*i , y , 20, room) for i in range(10)]
# obstacles2 = [lb.Obstacle(x+ 100 +50*i , y+450 , 20, room) for i in range(10)]
# obstacles3 = [lb.Obstacle(x+ 600 , y+i*50, 20, room) for i in range(10)]
# obstacles4 = [lb.Obstacle(x+ 100 +50*i , y+300 - i*20, 20, room) for i in range(4)]

# room.addObjects([lidarBot] + obstacles + obstacles2 + obstacles3 )
# room.addObjects([lidarBot,lidarBot2, lidarBot3, lidarBot4] + obstacles)

room.addObjects(lidarBots)

def redrawGameWindow(win, surface1):
    win.fill((0,0,0))
    surface1.fill((255,255,255,64))  
    for obj in room.objects:
        obj.draw(win, surface1)
    win.blit(surface1, (0,0))
    pygame.display.update() 


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
