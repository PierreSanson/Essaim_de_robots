import pygame as pg
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
import sys
import numpy as np
import pickle

import bot
import explorerBot as eb
import refPointBot as rpb
import measuringBot as mb
from room import*
import swarmControl as sc
from main import redrawGameWindow


def LoadFile():
    
    window = Tk()
    window.withdraw()
        
    availableFormats = [("Pickle dump", "*.pickle")]
    
    filename = askopenfilename(title="Open File", filetypes=availableFormats)
    filePath = filename[:]

    if filePath:
        file = open(filePath, "rb")
        colors = pickle.load(file)
        file.close()

        # convertir tableau numpy en simulateur
        
        filePathList = filePath.split("/")
        fileName = filePathList[-1]
        pg.display.set_caption("Simulation - " + fileName)

        return colors


def find_walls_corners(table):
    # trouver les murs verticaux
    vertical_walls_corners = []

    for c in range(len(table[0])-1):
        column = table[:,c]
        next_column = table[:,c+1]

        if 0 in column and 0 in next_column:
            potential_walls = table[:,c:c+2]
            
            r = 0
            in_a_wall = False
            for r in range(len(table)):
                
                if potential_walls[r,:][0] == 0 and potential_walls[r,:][1] == 0 and in_a_wall == False:
                    in_a_wall = True
                    new_wall = [[r,c],[r,c+1]]
                    length_wall = 1
                elif potential_walls[r,:][0] == 0 and potential_walls[r,:][1] == 0 and in_a_wall == True:
                    length_wall += 1
                elif (potential_walls[r,:][0] != 0 or potential_walls[r,:][1] != 0) and in_a_wall == True:
                    in_a_wall = False
                    new_wall.append([r-1,c])
                    new_wall.append([r-1,c+1])
                    new_wall.append('v')
                    if length_wall > 2:
                        vertical_walls_corners.append(new_wall)

    # trouver les murs horizontaux
    horizontal_walls_corners = []

    for r in range(len(table)-1):
        row = table[r,:]
        next_row = table[r+1,:]

        if 0 in row and 0 in next_row:
            potential_walls = table[r:r+2,:]
            
            c = 0
            in_a_wall = False
            for c in range(len(table[0])):
                if potential_walls[:,c][0] == 0 and potential_walls[:,c][1] == 0 and in_a_wall == False:
                    in_a_wall = True
                    new_wall = [[r,c],[r+1,c]]
                    length_wall = 1
                elif potential_walls[:,c][0] == 0 and potential_walls[:,c][1] == 0 and in_a_wall == True:
                    length_wall += 1
                elif (potential_walls[:,c][0] != 0 or potential_walls[:,c][1] != 0) and in_a_wall == True:
                    in_a_wall = False
                    new_wall.append([r,c-1])
                    new_wall.append([r+1,c-1])
                    new_wall.append('h')
                    if length_wall > 2:
                        horizontal_walls_corners.append(new_wall)

    walls_corners = vertical_walls_corners + horizontal_walls_corners

    return walls_corners


def drawing_to_simulation(table):
    walls_corners = find_walls_corners(table)

    robots_centers = []
    for row in range(len(table)):
        for col in range(len(table[0])):
            if table[row,col] in [1,2,3]:
                # juste par souci de compréhension
                y = row
                x = col
                robots_centers.append([[x,y],table[row,col]])

    # point de départ des tracés, pour ne pas être trop prêt du bord de l'écran
    offset = 10
    
    # facteur multiplicatif pour avoir des distances de l'ordre de la taille de l'écran (on part de 220x128 et on va vers 1600*900)
    scale = 7

    for i in range(len(walls_corners)):
        for j in range(4):
            walls_corners[i][j][0] = walls_corners[i][j][0]*scale + offset
            walls_corners[i][j][1] = walls_corners[i][j][1]*scale + offset

    for i in range(len(robots_centers)):
        robots_centers[i][0][0] = robots_centers[i][0][0]*scale  + offset
        robots_centers[i][0][1] = robots_centers[i][0][1]*scale  + offset

    # création de la salle, attention les dimensions sont fixées, peut-être à changer
    sw, sh = 1600, 900
    screen = pg.display.set_mode((sw, sh))
    room = Room(sw,sh,screen)

    for corners in walls_corners:
        room.addWall(corners)

    measuringBots = []
    explorerBots = []
    refPointBots = []
    
    for bot in robots_centers:
        botType = bot.pop()
        if botType == 1:
            measuringBots.append(mb.MeasuringBot(bot[0][0], bot[0][1], 15, room, objective = None, haveObjective = False, showDetails = True))
        elif botType == 2:
            explorerBots.append(eb.ExplorerBot(bot[0][0], bot[0][1], 10, room, objective = None, haveObjective = False))
        elif botType == 3:
            refPointBots.append(rpb.RefPointBot(bot[0][0], bot[0][1], 10, room, objective = None, haveObjective = False))
            
    bots = measuringBots + explorerBots + refPointBots

    room.addObjects(bots)

    SC = sc.SwarmController(screen, measuringBots[0], refPointBots)
    SC.initMove()

    return room, SC, measuringBots, explorerBots, refPointBots  


def load_and_launch_simulation():

    table = LoadFile()

    room, SC, measuringBots, explorerBots, refPointBots = drawing_to_simulation(table)

    sw, sh = 1600, 900
    win = pg.display.set_mode((sw, sh))
    surface1 = pygame.Surface((sw,sh),  pygame.SRCALPHA)

    clock = pygame.time.Clock()
    hz = 60

    run = True 
    while run:
        clock.tick(hz)
        redrawGameWindow(room, win, surface1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        SC.move()
        for obj in room.objects:
            if isinstance(obj, eb.ExplorerBot) or isinstance(obj, rpb.RefPointBot) or isinstance(obj, mb.MeasuringBot) or (isinstance(obj, bot.Obstacle) and obj.movable):
                obj.move(surface1)
        win.blit(surface1, (0,0))
        pygame.display.update()


# test = np.array([[1,0,0,4],[5,0,0,8],[5,0,0,8],[9,1,5,7]])
# print(test)
# print(find_walls_corners(test))
# print(test.transpose())
# print(find_walls_corners(test.transpose()))
