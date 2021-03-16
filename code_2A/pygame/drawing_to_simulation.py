import pygame as pg
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
import sys
import numpy as np
import pickle

import bot
import obstacle as obs
import explorerBot as eb
import refPointBot as rpb
import measuringBot as mb
from room import *
import swarmControl as sc
import swarmExploration as se
import swarmExplorationUWBSLAM as seUWBSLAM


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


def drawing_to_simulation(table,surface):
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

    # création de la salle
    room = Room(surface)

    for corners in walls_corners:
        room.addWall(corners)

    room.defineObstaclesFromWalls()

    measuringBots = []
    explorerBots = []
    refPointBots = []
    
    for bot in robots_centers:
        botType = bot.pop()
        if botType == 1:
            measuringBots.append(mb.MeasuringBot(bot[0][0], bot[0][1], 10, room, objective = None, haveObjective = False, showDetails=True))
        elif botType == 2:
            explorerBots.append(eb.ExplorerBot(bot[0][0], bot[0][1], 8, room, objective = [0, 0], randomObjective = True, randomInterval =1, showDetails = True))
        elif botType == 3:
            refPointBots.append(rpb.RefPointBot(bot[0][0], bot[0][1], 6, room, objective = None, haveObjective = False, showDetails = True))

            
    bots = measuringBots + explorerBots + refPointBots

    room.addObjects(bots)

    SC = sc.SwarmController(surface, measuringBots[0], refPointBots, distRefPointBots=[60,60])
    SE = se.RoomExplorator(surface,room,SC)
    SEUWBSLAM = seUWBSLAM.SwarmExploratorUWBSLAM(surface, room, measuringBots[0], refPointBots)

    SC.initMove()

    return room, SC,SE,SEUWBSLAM, measuringBots, explorerBots, refPointBots,


def redrawGameWindow(room, background):
    
    room.surface1.fill((64,64,64))
    ### surface1 : surface pour tous les objets : robots et murs
    # mise à jour des robots
    for obj in room.objects:
        if not isinstance(obj, obs.Obstacle):
            obj.draw()
    # mise à jour des murs, surface1 est un des attributs dae room
    room.draw_walls()

    ### surface2 : surface pour la visualisation de l'exploration
    # room.updateExploration(surface2)

    ### Composition de la scène
    # on choisit et on applique la couleur de l'arrière plan de la simulation
    background.fill((64,64,64))
    # ajout des murs et robots au dessus de l'arrière plan
    background.blit(room.surface1, (0,0))
    # ajout d'une surcouche transparente zones déjà explorées et opacifiantes dans les zones non explorées
    # background.blit(surface2, (0,0))

    ### mise à jour de l'affichage
    ### En l'état du simulateur on ne peut pas appeler la mise à jour ici, car il y a des affichages supllémentaires réglés à la main dans la boucle
    #pygame.display.update() 


def load_and_launch_simulation():

    table = LoadFile()

    sw, sh = 1600, 900
    background = pg.display.set_mode((sw, sh))
    surface1 = pygame.Surface((sw,sh),  pygame.SRCALPHA)

    room, SC, SE, SEUWBSLAM, measuringBots, explorerBots, refPointBots = drawing_to_simulation(table,surface1)

    clock = pygame.time.Clock()
    hz = 60

    run = True 
    while run:
        clock.tick(hz)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False  

        ## Choix du type de déplacement (move) et des affichages supplémentaires associés (draw + blit)
        # SC.move()     # premiere version avec l'essaim qui fait la chenille
        # SE.move()     # exploration d'une salle connue
        # SE.draw()
        # background.blit(SE.surface,(0,0))
        SEUWBSLAM.move()  # methode de Raul avec dispersion initiale des points de repère
        SEUWBSLAM.draw()
        background.blit(SEUWBSLAM.surface,(0,0))

        # mise à jour affichage
        pygame.display.update()

        ## Itération sur l'ensemble des robots pour les faire se déplacer
        for obj in room.objects:
            if isinstance(obj, eb.ExplorerBot) or isinstance(obj, rpb.RefPointBot) or isinstance(obj, mb.MeasuringBot) or (isinstance(obj, obs.Obstacle) and obj.movable):
                obj.move()

        redrawGameWindow(room, background)      
