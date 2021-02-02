import bot as Bot
import pygame
import random
import explorerBot as eb
import refPointBot as rpb
import measuringBot as mb

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
    nbStepsStraight = 4
    nbStepsRight = 4
    nbSteps = nbStepsStraight+nbStepsRight
    objectives = [[None for i in range(nbRefPointBots)] for j in range(nbSteps)]
    objectivesMeasuringBot = [None for j in range(nbSteps+1)]
    for i in range(nbRefPointBots):
        refPointBots.append(rpb.RefPointBot(100 + (i//2)*distRefPointBots[0], 100 + (i%2)*distRefPointBots[1] , radius, room,color=(0,0,255), objective=None, haveObjective=False))
    
    for j in range (nbStepsStraight):
        for i in range(nbRefPointBots):
            if j%(nbRefPointBots//2) == i//2:
                objectives[j][i] = (100 + (nbRefPointBots//2)*distRefPointBots[0] + j*distRefPointBots[0],
                     100 + (i%2)*distRefPointBots[1])
        objectivesMeasuringBot[j]=(100 + 3*distRefPointBots[0]/2 + distRefPointBots[0]*(j), 100 + distRefPointBots[1]/2)
    objectivesMeasuringBot[nbStepsStraight]=(100 + 3*distRefPointBots[0]/2 + distRefPointBots[0]*(nbStepsStraight), 100 + distRefPointBots[1]/2)



    for j in range (nbStepsStraight, nbStepsStraight + nbStepsRight):
        for i in range(nbRefPointBots):
            if j%(nbRefPointBots//2) == i//2:
                objectives[j][i] = ((nbStepsStraight+nbRefPointBots//2)*distRefPointBots[0] - (i%2)*distRefPointBots[0],
                     100 + distRefPointBots[1]*((nbRefPointBots//2)+j-nbStepsStraight-1))
        objectivesMeasuringBot[j+1]=(100 +(nbStepsStraight)*distRefPointBots[0] + 3*distRefPointBots[0]/2, 100 + distRefPointBots[1]*((nbRefPointBots//2)+j-nbStepsStraight-2) + distRefPointBots[1]/2)
    



    room.addObjects(refPointBots)
    measurerBot = mb.MeasuringBot(100 + 3*distRefPointBots[0]/2, 100 + distRefPointBots[1]/2 , 20, room, color =(255, 0, 0), objective=None, haveObjective=False)
    ExplorerBots = [eb.ExplorerBot(300 + 60*i,  350 , radius, room, [300 + 60*i, 700], randomObjective = True, randomInterval =1, color=(0, 255, 0)) for i in range(3)]
    room.addObjects(ExplorerBots)
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
                    # room.objects[-1].defineObjective((100 + 3*distRefPointBots[0]/2 + distRefPointBots[0]*(step), 100 + distRefPointBots[1]/2))
                    room.objects[-1].defineObjective(objectivesMeasuringBot[step])
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
            if isinstance(obj, Bot.Bot) or (isinstance(obj, Bot.Obstacle) and obj.movable):
                obj.move(surface1)
        win.blit(surface1, (0,0))
        pygame.display.update() 
        t+=1

def demos(nb = 1):

    if nb == 1 :
        Bots = [Bot.Bot(x, y + i*100 , radius, room, [x + 1150, y + i*50], randomObjective = True, randomInterval =10) for i in range(20)]

        room.addObjects(Bots)

    elif nb == 2 :
        Bots = [Bot.Bot(x+350, y +300 + i*50 , radius, room, [x + 1100, y + 50 + i*50], randomObjective = False, radiusDetection=400) for i in range(1)]
        obstacles = [Bot.Obstacle(x+ 300 +50*i , y , 20, room) for i in range(6)]
        obstacles2 = [Bot.Obstacle(x+ 300 +50*i , y+450 , 20, room) for i in range(6)]
        obstacles3 = [Bot.Obstacle(x+ 600 , y+i*50, 20, room) for i in range(10)]

        room.addObjects(Bots + obstacles + obstacles2 + obstacles3)

    elif nb == 3 :
        Bot = Bot.Bot(x, y , radius, room, [x + 1150, y+650], showDetails = True)
        # Bot2 = Bot.Bot(x+1150, y +650, radius, room, [x, y+100])
        # Bot3 = Bot.Bot(x+1150, y +100, radius, room, [x, y+650])
        # Bot4 = Bot.Bot(x, y +650, radius, room, [x + 1150, y+100])
        Bots = [Bot]
        obstacles = [Bot.Obstacle(random.randrange(150, 1100) , random.randrange(0, 650), 20, room) for i in range(40)]
        room.addObjects(Bots + obstacles)

    elif nb == 4 :
        Bots = [Bot.Bot(x, y + i*100 , radius, room, [random.randrange(150, 1100),random.randrange(0, 650)], randomObjective = True, randomInterval = 10) for i in range(5)]
        obstacles = [Bot.Obstacle(x + 300, y + 300, 50, room, movable = True) for i in range(1)]

        room.addObjects(Bots + obstacles)
    
    elif nb == 5 :
        Bots = [Bot.Bot(x, y + 50, radius, room, [x+1100,y])]
        obstacles = [Bot.Obstacle(x + 200 + i*50, y, 20, room) for i in range(10)]
        obstacles2 = [Bot.Obstacle(x + 200 + i*50, y+50, 20, room) for i in range(10)]
        obstacles3 = [Bot.Obstacle(x + 200 + i*50, y+100, 20, room) for i in range(10)]

        room.addObjects(Bots + obstacles + obstacles2+ obstacles3)
    
    elif nb == 6 :
        Bots = [Bot.Bot(x+500, y +300 + i*50 , radius, room, [x + 1100, y + 50 + i*50], randomObjective = False) for i in range(1)]

        for j in range(3):
            obstacles = [Bot.Obstacle(x+ 300 +50*i , y+250*j , 20, room) for i in range(6)]
            obstacles2 = [Bot.Obstacle(x+ 300 +50*i , y+250 +250*j , 20, room) for i in range(3)]
            obstacles3 = [Bot.Obstacle(x+ 600 , y+i*50 +250*j, 20, room) for i in range(10)]

            room.addObjects(obstacles + obstacles2 + obstacles3)
        room.addObjects(Bots)

    run = True 
    while run:
        clock.tick(hz)
        redrawGameWindow(win, surface1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        for obj in room.objects:
            if isinstance(obj, Bot.Bot) or (isinstance(obj, Bot.Obstacle) and obj.movable):
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
