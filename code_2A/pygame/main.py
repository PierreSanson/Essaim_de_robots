import lidarBot as lb
import pygame
import random

pygame.init()

winWidth = 1280
winHeight = 720
win = pygame.display.set_mode((winWidth,winHeight))
surface1 = pygame.Surface((winWidth,winHeight),  pygame.SRCALPHA) 

pygame.display.set_caption("First Game")

clock = pygame.time.Clock()
hz = 60

x = 60
y = 60
radius = 15
vel = 5*(60/hz)



class Room():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.objects = []
    
    def addObjects(self, objs):
        self.objects+=objs


room = Room(winWidth, winHeight)


def scenario():
    nbRefPointBots = 6
    distRefPointBots = [100, 110]
    refPointBots = []
    nbSteps = 10
    objectives = [[None for i in range(nbRefPointBots)] for j in range(nbSteps)]
    for i in range(nbRefPointBots):
        refPointBots.append(lb.LidarBot(100 + (i//2)*distRefPointBots[0], 100 + (i%2)*distRefPointBots[1] , radius, room,color=(0,0,255), objective=None, haveObjective=False))
    
    for j in range (nbSteps):
        for i in range(nbRefPointBots):
            if j%(nbRefPointBots//2) == i//2:
                objectives[j][i] = (100 + (nbRefPointBots//2)*distRefPointBots[0] + j*distRefPointBots[0],
                     100 + (i%2)*distRefPointBots[1])
    

    room.addObjects(refPointBots)
    measurerBot = lb.LidarBot(100 + 3*distRefPointBots[0]/2, 100 + distRefPointBots[1]/2 , 20, room, color =(255, 0, 0), objective=None, haveObjective=False)
    lidarBots = [lb.LidarBot(300 + 60*i,  350 , radius, room, [300 + 60*i, 700], randomObjective = True, randomInterval =1, color=(0, 255, 0)) for i in range(4)]
    room.addObjects(lidarBots)
    room.addObjects([measurerBot])
    

    run = True 
    t = 0 

    robotsWithObj = []
    checkedRobotWithObj = True
    init = False
    step = 0
    moveMeasuringBot = False
    while run:
        
        if t == 60:
            for i in range(nbRefPointBots):
                if objectives[0][i] != None:
                    room.objects[i].defineObjective(objectives[0][i])
                    room.objects[i].color = (0,255,255)
                    robotsWithObj.append(room.objects[i])
                else : 
                    room.objects[i].color = (0,0,255)
            init = True
            step+=1
            moveMeasuringBot = True

        if init and step < nbSteps:
            checkedRobotWithObj = True
            
            for robot in robotsWithObj:
                if not robot.ontoObjective:
                    checkedRobotWithObj = False
                elif robot.color == (0,255,255) : 
                    robot.color = (0,0,255)
            if checkedRobotWithObj:
                robotsWithObj = []
                if moveMeasuringBot:
                    robotsWithObj.append(room.objects[-1])
                    room.objects[-1].defineObjective((100 + 3*distRefPointBots[0]/2 + distRefPointBots[0]*(step), 100 + distRefPointBots[1]/2))
                    moveMeasuringBot = False
                else : 
                    for i in range(nbRefPointBots):
                        if objectives[step][i] != None:
                            room.objects[i].defineObjective(objectives[step][i])
                            if not room.objects[i].ontoObjective:
                                room.objects[i].color = (0,255,255)
                            robotsWithObj.append(room.objects[i])
                        else : 
                            room.objects[i].color = (0,0,255)
                    moveMeasuringBot = True
                    step+=1

            
        # for j in range(nbSteps):
        #     if t == 60 + j*500:
        #         for i in range(nbRefPointBots):
        #             if objectives[j][i] != None:
        #                 room.objects[i].defineObjective(objectives[j][i])
        #                 room.objects[i].color = (0,255,255)
        #             else : 
        #                 room.objects[i].color = (0,0,255)
        #     if t == 60 + 250 +500*j:
        #         room.objects[-1].defineObjective((100 + 3*distRefPointBots[0]/2 + distRefPointBots[0]*(j+1), 100 + distRefPointBots[1]/2))

                
        clock.tick(hz)
        redrawGameWindow(win, surface1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        

        for obj in room.objects:
            if isinstance(obj, lb.LidarBot) or (isinstance(obj, lb.Obstacle) and obj.movable):
                obj.move(surface1)
        win.blit(surface1, (0,0))
        pygame.display.update() 
        t+=1

def demos(nb = 1):

    if nb == 1 :
        lidarBots = [lb.LidarBot(x, y + i*100 , radius, room, [x + 1150, y + i*50], randomObjective = True, randomInterval =10) for i in range(20)]

        room.addObjects(lidarBots)

    elif nb == 2 :
        lidarBots = [lb.LidarBot(x+350, y +300 + i*50 , radius, room, [x + 1100, y + 50 + i*50], randomObjective = False, radiusDetection=400) for i in range(1)]
        obstacles = [lb.Obstacle(x+ 300 +50*i , y , 20, room) for i in range(6)]
        obstacles2 = [lb.Obstacle(x+ 300 +50*i , y+450 , 20, room) for i in range(6)]
        obstacles3 = [lb.Obstacle(x+ 600 , y+i*50, 20, room) for i in range(10)]

        room.addObjects(lidarBots + obstacles + obstacles2 + obstacles3)

    elif nb == 3 :
        lidarBot = lb.LidarBot(x, y , radius, room, [x + 1150, y+650], showDetails = True)
        # lidarBot2 = lb.LidarBot(x+1150, y +650, radius, room, [x, y+100])
        # lidarBot3 = lb.LidarBot(x+1150, y +100, radius, room, [x, y+650])
        # lidarBot4 = lb.LidarBot(x, y +650, radius, room, [x + 1150, y+100])
        lidarBots = [lidarBot]
        obstacles = [lb.Obstacle(random.randrange(150, 1100) , random.randrange(0, 650), 20, room) for i in range(40)]
        room.addObjects(lidarBots + obstacles)

    elif nb == 4 :
        lidarBots = [lb.LidarBot(x, y + i*100 , radius, room, [random.randrange(150, 1100),random.randrange(0, 650)], randomObjective = True, randomInterval = 10) for i in range(5)]
        obstacles = [lb.Obstacle(x + 300, y + 300, 50, room, movable = True) for i in range(1)]

        room.addObjects(lidarBots + obstacles)
    
    elif nb == 5 :
        lidarBots = [lb.LidarBot(x, y + 50, radius, room, [x+1100,y])]
        obstacles = [lb.Obstacle(x + 200 + i*50, y, 20, room) for i in range(10)]
        obstacles2 = [lb.Obstacle(x + 200 + i*50, y+50, 20, room) for i in range(10)]
        obstacles3 = [lb.Obstacle(x + 200 + i*50, y+100, 20, room) for i in range(10)]

        room.addObjects(lidarBots + obstacles + obstacles2+ obstacles3)
    
    elif nb == 6 :
        lidarBots = [lb.LidarBot(x+500, y +300 + i*50 , radius, room, [x + 1100, y + 50 + i*50], randomObjective = False) for i in range(1)]

        for j in range(3):
            obstacles = [lb.Obstacle(x+ 300 +50*i , y+250*j , 20, room) for i in range(6)]
            obstacles2 = [lb.Obstacle(x+ 300 +50*i , y+250 +250*j , 20, room) for i in range(3)]
            obstacles3 = [lb.Obstacle(x+ 600 , y+i*50 +250*j, 20, room) for i in range(10)]

            room.addObjects(obstacles + obstacles2 + obstacles3)
        room.addObjects(lidarBots)

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
        win.blit(surface1, (0,0))
        pygame.display.update() 

        



def redrawGameWindow(win, surface1):
    win.fill((0,0,0))
    surface1.fill((255,255,255,64))  
    for obj in room.objects:
        obj.draw(win, surface1)
    # win.blit(surface1, (0,0))
    # pygame.display.update() 
    


if __name__ == "__main__":
    # demos(3)
    # demos(2)
    scenario()


    
    
pygame.quit()
