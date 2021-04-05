import pygame
import random

import bot
import bot as b
import explorerBot as eb
import refPointBot as rpb
import measuringBot as mb
import swarmControl as sc
import swarmExploration as se

from room import*


def scenario2():

    pygame.init()

    winWidth = 1600
    winHeight = 900
    win = pygame.display.set_mode((winWidth,winHeight))
    surface1 = pygame.Surface((winWidth,winHeight),  pygame.SRCALPHA) 

    clock = pygame.time.Clock()
    hz = 60

    x = 60
    y = 60
    radius = 10
    vel = 5*(60/hz)


    room = Room(winWidth, winHeight, win)

    nbRefPointBots = 6

    refPointBots = []

    for i in range(nbRefPointBots):
        refPointBots.append(rpb.RefPointBot(random.randrange(0,winWidth), random.randrange(0,winHeight) , radius, room,color=(0,0,255), objective=None, haveObjective=False))
    measurerBot = mb.MeasuringBot(200, 400 , 15, room, color =(255, 0, 0), objective=None, haveObjective=False)

    room.addObjects(refPointBots + [measurerBot])
    ExplorerBots = [eb.ExplorerBot(300 + 60*i,  350 , radius, room, [300 + 60*i, 700], randomObjective = True, randomInterval =1, color=(0, 255, 0)) for i in range(3)]
    room.addObjects(ExplorerBots)

    SC = sc.SwarmController(surface1, measurerBot, refPointBots, distRefPointBots=[100, 100])
    SE = se.RoomExplorator(room,SC)

    SC.initMove()

    run = True 
    while run:
        clock.tick(hz)
        redrawGameWindow(room, win, surface1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        SC.move()
        # SC.draw()
        # room.draw()
        SE.draw(win)
        for obj in room.objects:
            if isinstance(obj, eb.ExplorerBot) or isinstance(obj, rpb.RefPointBot) or isinstance(obj, mb.MeasuringBot) or (isinstance(obj, bot.Obstacle) and obj.movable):
                obj.move(surface1)
        win.blit(surface1, (0,0))
        pygame.display.update() 


def scenario():

    pygame.init()

    winWidth = 1600
    winHeight = 900

    win = pygame.display.set_mode((winWidth,winHeight))
    surface1 = pygame.Surface((winWidth,winHeight),  pygame.SRCALPHA) 

    pygame.display.set_caption("First Game")
    room = Room(winWidth, winHeight, win)


    clock = pygame.time.Clock()
    hz = 144

    x = 60
    y = 60
    radius = 15
    vel = 5*(60/hz)


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
        redrawGameWindow(room, win, surface1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        
        # room.draw()
        for obj in room.objects:
            if isinstance(obj, eb.ExplorerBot) or (isinstance(obj, bot.Obstacle) and obj.movable):
                obj.move(surface1)
        win.blit(surface1, (0,0))
        pygame.display.update() 
        t+=1


def demos(room, nb = 1):

    pygame.init()

    winWidth = 1600
    winHeight = 900
    win = pygame.display.set_mode((winWidth,winHeight))
    surface1 = pygame.Surface((winWidth,winHeight),  pygame.SRCALPHA) 

    pygame.display.set_caption("First Game")

    clock = pygame.time.Clock()
    hz = 60

    x = 60
    y = 60
    radius = 15
    vel = 5*(60/hz)


    room.objects = []

    if nb == 1 :
        Bots = [eb.ExplorerBot(x, y + i*100 , radius, room, [x + 1150, y + i*50], randomObjective = True, randomInterval =10) for i in range(20)]

        room.addObjects(Bots)

    elif nb == 2 :
        Bots = [eb.ExplorerBot(x+350, y +300 + i*50 , radius, room, [x + 1100, y + 50 + i*50],showDetails = True, randomObjective = False, radiusDetection=150) for i in range(1)]
        obstacles = [bot.Obstacle(x+ 300 +50*i , y , 20, room) for i in range(6)]
        obstacles2 = [bot.Obstacle(x+ 300 +50*i , y+450 , 20, room) for i in range(6)]
        obstacles3 = [bot.Obstacle(x+ 600 , y+i*50, 20, room) for i in range(10)]

        room.addObjects(Bots + obstacles + obstacles2 + obstacles3)

    elif nb == 3 :
        Bot = eb.ExplorerBot(x, y , radius, room, [x + 1150, y+650], showDetails = True)
        # Bot2 = eb.ExplorerBot(x+1150, y +650, radius, room, [x, y+100])
        # Bot3 = eb.ExplorerBot(x+1150, y +100, radius, room, [x, y+650])
        # Bot4 = eb.ExplorerBot(x, y +650, radius, room, [x + 1150, y+100])
        Bots = [Bot]
        obstacles = [b.Obstacle(random.randrange(150, 1100) , random.randrange(0, 650), 20, room) for i in range(60)]
        room.addObjects(Bots + obstacles)

    elif nb == 4 :
        Bots = [eb.ExplorerBot(x, y + i*100 , radius, room, [random.randrange(150, 1100),random.randrange(0, 650)], randomObjective = True, randomInterval = 10) for i in range(5)]
        obstacles = [bot.Obstacle(x + 300, y + 300, 50, room, movable = True) for i in range(1)]

        room.addObjects(Bots + obstacles)
    
    elif nb == 5 :
        Bots = [eb.ExplorerBot(x, y + 50, radius, room, [x+1100,y], showDetails = True)]
        obstacles = [bot.Obstacle(x + 200 + i*50, y, 20, room) for i in range(10)]
        obstacles2 = [bot.Obstacle(x + 200 + i*50, y+50, 20, room) for i in range(10)]
        obstacles3 = [bot.Obstacle(x + 200 + i*50, y+100, 20, room) for i in range(10)]

        room.addObjects(Bots + obstacles + obstacles2+ obstacles3)
    
    elif nb == 6 :
        Bots = [eb.ExplorerBot(x+500, y +300 + i*50 , radius, room, [x + 1100, y + 50 + i*50], randomObjective = False) for i in range(1)]

        for j in range(3):
            obstacles = [bot.Obstacle(x+ 300 +50*i , y+250*j , 20, room) for i in range(6)]
            obstacles2 = [bot.Obstacle(x+ 300 +50*i , y+250 +250*j , 20, room) for i in range(3)]
            obstacles3 = [bot.Obstacle(x+ 600 , y+i*50 +250*j, 20, room) for i in range(10)]

            room.addObjects(obstacles + obstacles2 + obstacles3)
        room.addObjects(Bots)

    run = True 
    while run:
        clock.tick(hz)
        redrawGameWindow(room, win, surface1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        for obj in room.objects:
            if isinstance(obj, eb.ExplorerBot) or (isinstance(obj, bot.Obstacle) and obj.movable):
                obj.move(surface1)
        win.blit(surface1, (0,0))
        pygame.display.update() 


def redrawGameWindow(room, background, surface1):
    
    ### surface1 : surface pour tous les objets : robots et murs
    # mise à jour des robots
    for obj in room.objects:
        obj.draw(surface1)
    # mise à jour des murs
    room.draw_walls(surface1)

    ### surface2 : surface pour la visualisation de l'exploration
    # room.updateExploration(surface2)

    ### Composition de la scène
    # on choisit et on applique la couleur de l'arrière plan de la simulation
    background.fill((64,64,64))
    # ajout des murs et robots au dessus de l'arrière plan
    background.blit(surface1, (0,0))
    # ajout d'une surcouche transparente zones déjà explorées et opacifiantes dans les zones non explorées
    # background.blit(surface2, (0,0))

    ### mise à jour de l'affichage
    pygame.display.update() 
    


if __name__ == "__main__":
    # demos(3)
    # demos(2)
    scenario2()


    
    
pygame.quit()