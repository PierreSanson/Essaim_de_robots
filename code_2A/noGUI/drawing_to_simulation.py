import os
import time

from tkinter import *
from tkinter.filedialog import askopenfilename

import sys
import pickle

import explorerBot as eb
import refPointBot as rpb
import measuringBot as mb
from room import *
import swarmExplorationUWBSLAM as seUWBSLAM
import time


def LoadFile(filePath):

    if filePath:
        file = open(filePath, "rb")
        colors = pickle.load(file)
        file.close()
        filePathList = filePath.split("/")
        fileName = filePathList[-1]

        return colors, fileName[8:-7]

    return None


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
                
                if potential_walls[r,:][0] == 0 and potential_walls[r,:][1] == 0 and not in_a_wall:
                    in_a_wall = True
                    new_wall = [[r,c],[r,c+1]]
                    length_wall = 1
                elif potential_walls[r,:][0] == 0 and potential_walls[r,:][1] == 0 and in_a_wall:
                    length_wall += 1
                elif (potential_walls[r,:][0] != 0 or potential_walls[r,:][1] != 0) and in_a_wall:
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
                if potential_walls[:,c][0] == 0 and potential_walls[:,c][1] == 0 and not in_a_wall:
                    in_a_wall = True
                    new_wall = [[r,c],[r+1,c]]
                    length_wall = 1
                elif potential_walls[:,c][0] == 0 and potential_walls[:,c][1] == 0 and in_a_wall:
                    length_wall += 1
                elif (potential_walls[:,c][0] != 0 or potential_walls[:,c][1] != 0) and in_a_wall:
                    in_a_wall = False
                    new_wall.append([r,c-1])
                    new_wall.append([r+1,c-1])
                    new_wall.append('h')
                    if length_wall > 2:
                        horizontal_walls_corners.append(new_wall)

    walls_corners = vertical_walls_corners + horizontal_walls_corners

    return walls_corners



def drawing_to_simulation(table,width,height,tileWidth):

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

    walls_corners = find_walls_corners(table)
    for i in range(len(walls_corners)):
        for j in range(4):
            walls_corners[i][j][0] = walls_corners[i][j][0]*scale + offset
            walls_corners[i][j][1] = walls_corners[i][j][1]*scale + offset

    for i in range(len(robots_centers)):
        robots_centers[i][0][0] = robots_centers[i][0][0]*scale  + offset
        robots_centers[i][0][1] = robots_centers[i][0][1]*scale  + offset

    # création de la salle
    room = Room(walls_corners,width,height)

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

    room.addBots(bots)

    SEUWBSLAM = seUWBSLAM.SwarmExploratorUWBSLAM(room, measuringBots[0], refPointBots, tileWidth)

    return room, SEUWBSLAM



def load_and_launch_single_simulation(filePath,tileWidth):

    table, fileName = LoadFile(filePath)

    if table is not None : # évite un crash si on ne sélectionne pas de fichier
        initStart = time.time()
        sw, sh = 1600, 900
        room, SEUWBSLAM = drawing_to_simulation(table, sw, sh, tileWidth)
        initDuration = (time.time()-initStart)

        simulationStart = time.time()
        run = True 
        ## Choix du type de déplacement
        control = SEUWBSLAM
        control.set_params([control.grid.origin,0])

        while run:
            
            # fin de la simulation (les robtos ont arrêté de bouger)
            if control.end_simulation == True:
                run = False

            ## Calcul des mvmts à effectuer
            t = time.time()
            control.move()

            ## Itération sur l'ensemble des robots pour les faire se déplacer
            for bot in room.bots:
                bot.move()




        # si la simulation s'est achevée, on affiche les métriques et on attend que l'utilisateur ferme la fenêtre
        simulationDuration = time.time() - simulationStart

        metrics = control.get_metrics()
        metrics["init_duration"] = initDuration
        metrics["sim_duration"] = simulationDuration
        
        dirname = os.path.dirname(__file__)
        file = open(os.path.join(dirname, "./results/",str(fileName)+"-noGUI-results.pickle"), "wb")
        pickle.dump(metrics, file)
        file.close()

        return initDuration + simulationDuration


def initialize_simulation(filePath,tileWidth):
    table, fileName = LoadFile(filePath)

    if table is not None : # évite un crash si on ne sélectionne pas de fichier
        sw, sh = 1600, 900
        room, SEUWBSLAM = drawing_to_simulation(table, sw, sh, tileWidth)
        
        return SEUWBSLAM, SEUWBSLAM.grid.inside, SEUWBSLAM.nbRefPointBots


def launch_parametered_simulation(control,params):

    control.set_params(params)

    simulationStart = time.time()
    run = True 

    while run:
        
        # fin de la simulation (les robtos ont arrêté de bouger)
        if control.end_simulation == True:
            run = False

        ## Calcul des mvmts à effectuer
        t = time.time()
        control.move()

        ## Itération sur l'ensemble des robots pour les faire se déplacer
        for bot in control.room.bots:
            bot.move()


    # si la simulation s'est achevée, on affiche les métriques et on attend que l'utilisateur ferme la fenêtre
    simulationDuration = time.time() - simulationStart
    metrics = control.get_metrics()
    metrics["sim_duration"] = simulationDuration
    
    return metrics
