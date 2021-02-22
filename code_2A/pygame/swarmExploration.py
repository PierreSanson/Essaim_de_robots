from utilities import *
import numpy as np
import math
import pygame
from igraph import *

class RoomExplorator():
    def __init__(self, room, swarmController):
        self.room = room
        self.SC = swarmController
        self.graph = {}
        self.graphParentsList = {}
        self.graphChildsList = {}
        self.MST = []
        self.MSTedges = []
        self.walls = []
        self.lineinters = []
        self.lineintersEB = []
        self.nbLinesAbove, self.nbLinesBelow, self.nbLines, self.nbColsLeft, self.nbColsRight, self.nbCols, self.initNodeLine, self.initNodeCol = self.maxGridComputation()
        self.graphConstruction()
    
    def maxGridComputation(self):
        ExtremePoints= [[-1, -1], [-1, -1]]
        distMaxX = -1
        distMaxY =  -1
        
        for wall in self.room.walls:
            
            self.walls.append([[wall.x_start, wall.y_start],[wall.x_start+wall.width, wall.y_start]])
            self.walls.append([[wall.x_start, wall.y_start],[wall.x_start, wall.y_start + wall.height]])
            self.walls.append([[wall.x_start + wall.width, wall.y_start],[wall.x_start + wall.width, wall.y_start + wall.height]])
            self.walls.append([[wall.x_start, wall.y_start+wall.height],[wall.x_start+wall.width, wall.y_start + wall.height]])

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
        childCount=[]
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
            childCount.append(0)
            if i == 0:
                for j in range(len(stepLineinters)-1):
                    if stepLineinters[j][0] < self.SC.initMeasurerPos[0] < stepLineinters[j+1][0]:
                        self.graph['0-0'] = [stepLineinters[j], stepLineinters[j+1]]
                        childCount[0] += 1
            else:
                for j in range(len(stepLineinters)-1):
                    if not self.checkIsWall(stepLineinters[j], stepLineinters[j+1]):
                        parents = self.determineParents(i, [stepLineinters[j], stepLineinters[j+1]])
                        if len(parents)>0:
                            childKey = str(i) + '-' + str(childCount[i])
                            self.graph[childKey] = [stepLineinters[j], stepLineinters[j+1]]
                            self.addChildsAndParents(parents, childKey)
                            childCount[i] += 1
        
        for i in range(1, self.nbLinesBelow):
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
            childCount.append(0)
            for j in range(len(stepLineinters)-1):
                if not self.checkIsWall(stepLineinters[j], stepLineinters[j+1]):
                    if i == 1:
                        parents = self.determineParents(i, [stepLineinters[j], stepLineinters[j+1]])
                    else :
                        parents = self.determineParents(i + self.nbLinesAbove, [stepLineinters[j], stepLineinters[j+1]])
                    if len(parents)>0:
                        childKey = str(i + self.nbLinesAbove) +'-' + str(childCount[i+self.nbLinesAbove-1])
                        self.graph[childKey] = [stepLineinters[j], stepLineinters[j+1]]
                        self.addChildsAndParents(parents, childKey)
                        childCount[i+self.nbLinesAbove-1] += 1
        for k in range (1):
            for i in range(self.nbLinesBelow - 2, -self.nbLinesAbove, -1):
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
                for j in range(len(stepLineinters)-1):
                    if not self.checkIsWall(stepLineinters[j], stepLineinters[j+1]):
                        if i > 0:
                            parents = self.determineParents(i + self.nbLinesAbove, [stepLineinters[j], stepLineinters[j+1]], backwards=True)
                            if len(parents)>0:
                                if not [stepLineinters[j], stepLineinters[j+1]] in list(self.graph.values()):
                                    childKey = str(i + self.nbLinesAbove) +'-' + str(childCount[i+self.nbLinesAbove-1])
                                    self.graph[childKey] = [stepLineinters[j], stepLineinters[j+1]]
                                    self.addChildsAndParents(parents, childKey)
                                    childCount[i+self.nbLinesAbove-1] += 1
                        else : 
                            parents = []
                            if i == 0:
                                parents = self.determineParents(i + self.nbLinesAbove, [stepLineinters[j], stepLineinters[j+1]], backwards=True)
                            else:
                                parents = self.determineParents(-i, [stepLineinters[j], stepLineinters[j+1]])
                            if len(parents)>0:
                                if not [stepLineinters[j], stepLineinters[j+1]] in list(self.graph.values()):
                                    childKey = str(-i) + '-' + str(childCount[-i])
                                    self.graph[childKey] = [stepLineinters[j], stepLineinters[j+1]]
                                    self.addChildsAndParents(parents, childKey)
                                    childCount[-i] += 1
                                else : 
                                    childKey = GetKey([stepLineinters[j], stepLineinters[j+1]], self.graph)
                                    self.addChildsAndParents(parents, childKey)

            for i in range(self.nbLinesAbove -1, -self.nbLinesBelow, -1):
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

                for j in range(len(stepLineinters)-1):
                    if not self.checkIsWall(stepLineinters[j], stepLineinters[j+1]):
                        if i >= 0:
                            parents = self.determineParents(i, [stepLineinters[j], stepLineinters[j+1]], backwards=True)
                            if len(parents)>0:
                                if not [stepLineinters[j], stepLineinters[j+1]] in list(self.graph.values()):
                                    childKey = str(i) + '-' +str(childCount[i])
                                    self.graph[childKey] = [stepLineinters[j], stepLineinters[j+1]]
                                    self.addChildsAndParents(parents, childKey)
                                    childCount[i] += 1
                        else : 
                            if i == -1:
                                parents = self.determineParents(i, [stepLineinters[j], stepLineinters[j+1]], backwards=True)
                            else:
                                parents = self.determineParents(-i + self.nbLinesAbove, [stepLineinters[j], stepLineinters[j+1]])
                            if len(parents)>0:
                                if not [stepLineinters[j], stepLineinters[j+1]] in list(self.graph.values()):
                                    childKey = str(-i + self.nbLinesAbove) + '-' + str(childCount[-i + self.nbLinesAbove -1])
                                    self.graph[childKey] = [stepLineinters[j], stepLineinters[j+1]]
                                    self.addChildsAndParents(parents, childKey)
                                    childCount[-i + self.nbLinesAbove -1] += 1
                                else : 
                                    childKey = GetKey([stepLineinters[j], stepLineinters[j+1]], self.graph)
                                    self.addChildsAndParents(parents, childKey)

        self.cleanGraph()
        
        print('GRAPH : ', self.graph)
        print('CHILDS GRAPH : ', self.graphChildsList)
        print('PARENTS GRAPH : ', self.graphParentsList)
        self.minimumSpanningTreeComputation()
        self.drawGraph()
    
    def cleanGraph(self):
        for key in self.graphChildsList:
            for value in self.graphChildsList[key]:
                if value in self.graphChildsList:
                    if key in self.graphChildsList[value]:
                        self.graphChildsList[value].remove(key)
        for key in self.graphParentsList:
            for value in self.graphParentsList[key]:
                if value in self.graphParentsList:
                    if key in self.graphParentsList[value]:
                        self.graphParentsList[value].remove(key)
    
    def addChildsAndParents(self, parents, childKey):
        for parent in parents:
            if parent[0] in self.graphChildsList and childKey not in self.graphChildsList[parent[0]]:
                self.graphChildsList[parent[0]].append(childKey)
            else : 
                self.graphChildsList[parent[0]] = [childKey]

            if childKey in self.graphParentsList and parent[0] not in self.graphParentsList[childKey]:
                self.graphParentsList[childKey].append(parent[0])
            else : 
                self.graphParentsList[childKey] = [parent[0]]

    def minimumSpanningTreeComputation(self):
        minHeap = {}
        self.MST = []
        self.MSTedges = []

        for v in self.graph:
            minHeap[v] = -1
        self.MST = ['0-0']
        minHeap.pop('0-0')
        chosenV = '0-0'

        def changeNeighboursWeight(v):
            if v in self.graphChildsList:
                for child in self.graphChildsList[v]:
                    if child in minHeap:
                        minHeap[child] = v
            if v in self.graphParentsList:
                for parent in self.graphParentsList[v]:
                    if parent in minHeap:
                        minHeap[parent] = v
                   
        def choseVertex():
            for v in minHeap:
                if minHeap[v] != -1:
                    return v
            
        
        while minHeap :
            changeNeighboursWeight(chosenV)
            chosenV = choseVertex()

            self.MSTedges.append([chosenV, minHeap[chosenV]])
            self.MST.append(chosenV)
            minHeap.pop(chosenV)
        
        # print('MST : ', self.MST)
        # print('EDGES MST : ',self.MSTedges)



        
        

    def dfsComputation(self):
        pass

    def checkColParents(self, newLine, parent, commonPart):
        yChild = newLine[0][1]
        yParent = parent[0][1]
        stepMB = self.SC.distRefPointBots
        radiusMB = self.SC.measurerBot.radius
        
        for x in range(int(commonPart[0] + radiusMB//2), int(commonPart[1] - radiusMB//2), int(stepMB[0])):
            pathExist = True
            for wall in self.walls:
                inter = lineSegmentInter([[0,1], [x, yChild]], wall)
                if inter is not None:
                    if (yChild <= inter[1] <= yParent) or (yParent <= inter[1] <= yChild):
                        pathExist = False
            if pathExist:
                return True
        return False
    
    def determineParents(self, i, newLine,  backwards = False):
        potentialParentsKey = []
        parentsKey = []
        stepMB = self.SC.distRefPointBots
        for key in self.graph:
            if backwards:
                if key.startswith(str(i+1)+'-'):
                    potentialParentsKey.append(key)
            else :
                if key.startswith(str(i-1)+'-'):
                    potentialParentsKey.append(key)
        for key in potentialParentsKey:
            parent = self.graph[key]
            commonPart = [max(self.graph[key][0][0], newLine[0][0]), min(parent[1][0],  newLine[1][0])]
            if commonPart[1] - commonPart[0] > stepMB[0]:
                existPath = self.checkColParents(newLine, parent, commonPart)
                if existPath:
                    parentsKey.append([key, commonPart])
        return parentsKey

    def checkIsWall(self, inter1, inter2):
        if distLists(inter1, inter2) < self.SC.measurerBot.radius:
            return True
        return False

    def draw(self, win):
        for i in range(self.nbLinesAbove):
            pygame.draw.line(win, (100,100,100), (0, self.SC.initMeasurerPos[1] - self.SC.distRefPointBots[1]*( i)), (self.room.width, self.SC.initMeasurerPos[1]  - self.SC.distRefPointBots[1]*(i)))

        for i in range(self.nbLinesBelow):
            pygame.draw.line(win, (100,100,100), (0, self.SC.initMeasurerPos[1]  + self.SC.distRefPointBots[1]*(i)), (self.room.width, self.SC.initMeasurerPos[1] + self.SC.distRefPointBots[1]*(i)))

        # for i in range(self.nbColsLeft):
        #     pygame.draw.line(win, (100,100,100), (self.SC.initMeasurerPos[0] - self.SC.distRefPointBots[0]*(1/2+ i), 0), (self.SC.initMeasurerPos[0]  - self.SC.distRefPointBots[0]*(1/2+ i), self.room.height))

        # for i in range(self.nbColsRight):
        #     pygame.draw.line(win, (100,100,100), (self.SC.initMeasurerPos[0] + self.SC.distRefPointBots[0]*(1/2+ i), 0), (self.SC.initMeasurerPos[0]  + self.SC.distRefPointBots[0]*(1/2+ i), self.room.height))

        for inters in self.lineinters:
            for coord in inters:
                pygame.draw.circle(win, (255,0,0), coord, 2)
        pygame.font.init()
        myfont = pygame.font.SysFont('Arial', 20)
        for key in self.graph:
            pos = ((self.graph[key][0][0] +self.graph[key][1][0])/2 - 10 , (self.graph[key][0][1] +self.graph[key][1][1])/2 - 10)
            textsurface = myfont.render(key, False, (255, 255, 255))
            win.blit(textsurface,pos)
            

        # for intersEB in self.lineintersEB:
        #     for coord in intersEB:
        #         pygame.draw.circle(win, (0,0,255), coord, 2)
    
    def drawGraph(self):
        g = Graph()
        gMST = Graph()
        g.add_vertices(len(self.graph))
        gMST.add_vertices(len(self.graph))
        g.vs["name"] = list(self.graph.keys())
        gMST.vs["name"] = list(self.graph.keys())
        for parent in self.graphChildsList:
            for child in self.graphChildsList[parent]:
                parentIndex = g.vs['name'].index(parent)
                childIndex = g.vs['name'].index(child)
                g.add_edge(parentIndex, childIndex)
        g.vs["label"] = g.vs["name"]
        gMST.vs["label"] = gMST.vs["name"]
        for e in self.MSTedges:
            g.es.select(_source = g.vs['name'].index(e[0]), _from = g.vs['name'].index(e[1]))["color"] = "green"
            gMST.add_edge(e[0], e[1])
        layout = g.layout("rt", root=0)
        layoutMST = gMST.layout("rt", root=0)
        # layout = g.layout("fr")
        plot(g, layout = layout)
        plot(gMST, layout = layoutMST)
