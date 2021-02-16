from utilities import *
import numpy as np
import math
import pygame

class RoomExplorator():
    def __init__(self, room, swarmController):
        self.room = room
        self.SC = swarmController
        self.graph = {}
        self.minimumSpanningTree = {}
        self.walls = []
        self.lineinters = []
        self.lineintersEB = []
        self.nbLinesAbove, self.nbLinesBelow, self.nbLines, self.nbColsLeft, self.nbColsRight, self.nbCols, self.initNodeLine, self.initNodeCol = self.maxGridComputation()
        self.graphConstruction()
    
    def maxGridComputation(self):
        ExtremePoints= [[-1, -1], [-1, -1]]
        distMaxX = -1
        distMaxY =  -1
        
        for corners in self.room.walls:
            orientation = corners[-1]

            x_start = corners[0][1] # on fait bien attention entre x et y au sens d'un graphe Vs row et col pour numpy
            y_start = corners[0][0]

            if orientation == 'v':
                width = corners[1][1] - corners[0][1]
                height = corners[3][0] - corners[0][0]
            elif orientation == 'h':
                width = corners[3][1] - corners[0][1]
                height = corners[1][0] - corners[0][0]
            
            self.walls.append([[x_start, y_start],[x_start+width, y_start]])
            self.walls.append([[x_start, y_start],[x_start, y_start + height]])
            self.walls.append([[x_start + width, y_start],[x_start + width, y_start + height]])
            self.walls.append([[x_start, y_start+height],[x_start+width, y_start + height]])

        for i in range(len(self.walls)):
            for j in range (i+1, len(self.walls)):
                distMax = distMaxXY2Segments(self.walls[i], self.walls[j])
                if distMax[0] > distMaxX:
                    distMaxX = distMax[0]
                    ExtremePoints[0] = distMax[2][0]
                if distMax[1] > distMaxY:
                    distMaxY = distMax[1]
                    ExtremePoints[1] = distMax[2][1]

        nbLinesAbove = math.ceil(abs(ExtremePoints[1][0] - (self.SC.measurerBot.y- self.SC.distRefPointBots[1]/2))/self.SC.distRefPointBots[1])
        nbLinesBelow = math.ceil(abs(ExtremePoints[1][1] - (self.SC.measurerBot.y+ self.SC.distRefPointBots[1]/2))/self.SC.distRefPointBots[1])
        nbColsLeft = math.ceil(abs(ExtremePoints[0][0] - (self.SC.measurerBot.x- self.SC.distRefPointBots[0]/2))/self.SC.distRefPointBots[0])
        nbColsRight = math.ceil(abs(ExtremePoints[0][1] - (self.SC.measurerBot.x+ self.SC.distRefPointBots[0]/2))/self.SC.distRefPointBots[0])
        initNodeLine = nbLinesBelow
        nbLines = nbLinesBelow + nbLinesAbove
        initNodeCol = nbColsLeft
        nbCols = nbColsLeft + nbColsRight
        return (nbLinesAbove, nbLinesBelow, nbLines, nbColsLeft, nbColsRight, nbCols, initNodeLine, initNodeCol)
    
    def graphConstruction(self):
        # initLineinters=[]
        # for wall in self.walls:
        #     inter = lineSegmentInter([[1,0], [self.SC.initMeasurerPos[0], self.SC.initMeasurerPos[1]]], wall)
        #     if inter != None:
        #         initLineinters.append(inter)
        # self.lineinters.append(initLineinters)
        # self.graph[0] = [[0, self.SC.initMeasurerPos[1], self.room.width, self.SC.initMeasurerPos[1]]]
        for i in range(self.nbLinesAbove):
            stepLineinters = []
            stepLineintersEB = []
            for wall in self.walls:
                inter = lineSegmentInter([[1,0], [self.SC.initMeasurerPos[0] , self.SC.initMeasurerPos[1] - self.SC.distRefPointBots[1]*i]], wall)
                interEB = lineSegmentInter([[1,0], [self.SC.initMeasurerPos[0] , self.SC.initMeasurerPos[1] - self.SC.distRefPointBots[1]*(i+1/2)]], wall)
                if inter != None:
                    stepLineinters.append(inter)
                if interEB != None:
                    stepLineintersEB.append(interEB)
            self.lineinters.append(stepLineinters)
            self.lineintersEB.append(stepLineintersEB)
            for j in range(len(stepLineinters)):
                self.graph[str(i) + str(j)] = [[0, self.SC.initMeasurerPos[1], self.room.width, self.SC.initMeasurerPos[1]]]

        for i in range(self.nbLinesBelow):
            stepLineinters = []
            stepLineintersEB = []
            for wall in self.walls:
                inter = lineSegmentInter([[1,0], [self.SC.initMeasurerPos[0] , self.SC.initMeasurerPos[1] + self.SC.distRefPointBots[1]*i]], wall)
                interEB = lineSegmentInter([[1,0], [self.SC.initMeasurerPos[0] , self.SC.initMeasurerPos[1] + self.SC.distRefPointBots[1]*(i+1/2)]], wall)
                if inter != None:
                    stepLineinters.append(inter)
                if interEB != None:
                    stepLineintersEB.append(interEB)
            self.lineinters.append(stepLineinters)
            self.lineintersEB.append(stepLineintersEB)
            self.graph[i + self.nbLinesAbove] = [[0, self.SC.initMeasurerPos[1], self.room.width, self.SC.initMeasurerPos[1]]]


    def minimumSpanningTreeComputation(self):
        pass

    def dfsComputation(self):
        pass

    def draw(self, win):
        for i in range(self.nbLinesAbove):
            pygame.draw.line(win, (100,100,100), (0, self.SC.initMeasurerPos[1] - self.SC.distRefPointBots[1]*(1/2+ i)), (self.room.width, self.SC.initMeasurerPos[1]  - self.SC.distRefPointBots[1]*(1/2+ i)))

        for i in range(self.nbLinesBelow):
            pygame.draw.line(win, (100,100,100), (0, self.SC.initMeasurerPos[1]  + self.SC.distRefPointBots[1]*(1/2+ i)), (self.room.width, self.SC.initMeasurerPos[1] + self.SC.distRefPointBots[1]*(1/2+ i)))

        for i in range(self.nbColsLeft):
            pygame.draw.line(win, (100,100,100), (self.SC.initMeasurerPos[0] - self.SC.distRefPointBots[0]*(1/2+ i), 0), (self.SC.initMeasurerPos[0]  - self.SC.distRefPointBots[0]*(1/2+ i), self.room.height))

        for i in range(self.nbColsRight):
            pygame.draw.line(win, (100,100,100), (self.SC.initMeasurerPos[0] + self.SC.distRefPointBots[0]*(1/2+ i), 0), (self.SC.initMeasurerPos[0]  + self.SC.distRefPointBots[0]*(1/2+ i), self.room.height))

        for inters in self.lineinters:
            for coord in inters:
                pygame.draw.circle(win, (255,0,0), coord, 2)

        for intersEB in self.lineintersEB:
            for coord in intersEB:
                pygame.draw.circle(win, (0,0,255), coord, 2)
