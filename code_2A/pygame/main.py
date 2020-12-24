import lidarBot as lb

import pygame
pygame.init()

winWidth = 500
winHeight = 500
win = pygame.display.set_mode((winWidth,winHeight))
pygame.display.set_caption("First Game")

clock = pygame.time.Clock()
hz = 60

x = 50
y = 50
radius = 10
vel = 5*(60/hz)



class Room():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.objects = []
    
    def addObject(self, obj):
        self.objects.append(obj)


room = Room(winWidth, winHeight)

lidarBot = lb.LidarBot(x, y, radius, room)
obstacle = lb.Obstacle(x, y, radius, room)

room.addObject(lidarBot)

def redrawGameWindow(win):
    win.fill((0,0,0))
    for obj in room.objects:
        obj.draw(win)
    pygame.display.update() 

run = True 
while run:
    clock.tick(hz)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
  
    if keys[pygame.K_LEFT] and lidarBot.x > vel + radius: 
        lidarBot.x -= vel

    if keys[pygame.K_RIGHT] and lidarBot.x < 500 - vel - radius:  
        lidarBot.x += vel

    if keys[pygame.K_UP] and lidarBot.y > vel + radius: 
        lidarBot.y -= vel

    if keys[pygame.K_DOWN] and lidarBot.y < 500 - radius - vel:
        lidarBot.y += vel

    redrawGameWindow(win)
    
pygame.quit()
