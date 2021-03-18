from token import SEMI

import numpy as np
from utilities import *
from copy import deepcopy
import numpy as np
from scipy.spatial import ConvexHull
from itertools import chain
import colorsys
from igraph import *
from heapq import *
import random


from shapely.geometry import Point
from shapely.geometry.polygon import Polygon



class SwarmExploratorUWBSLAM():
    def __init__(self, win, room, measurerBot, refPointBots, distRefPointBots = [110, 110], initRadius=50) :
        self.room = room
        self.distRefPointBots = distRefPointBots
        self.measurerBot = measurerBot
        self.refPointBots = {}
        self.nbRefPointBots = len(refPointBots)
        self.orientation = 'h'
        self.status = 0
        # self.nextMoves = [['straight', 7], ['turnRight', 1],  ['turnRight', 1], ['straight', 8], ['turnLeft', 1], ['turnLeft', 1], ['straight',8]]
        # self.nextMoves = [['straight', 4], ['turnRight', 2]]
        self.actualSequenceLength = 0
        self.actualSequenceCount = 0
        self.actualOneStepCount = 0
        self.actualDeplacement = None
        self.maxOneStepCount = (self.nbRefPointBots//2 - 2)
        self.orientation = 'right'
        self.initMeasurerPos = (self.measurerBot.x, self.measurerBot.y)
        self.win = win
        self.initCount = 0
        self.theta = 2*np.pi/self.nbRefPointBots
        self.refPointBotsVisibleBots = {}
        HSV_tuples = [(x*1.0/self.nbRefPointBots, 0.5, 0.5) for x in range(self.nbRefPointBots)]
        self.RGB_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))
        self.walls = []
        self.convexHull = []
        self.gridWidth = 50
        self.origin = (self.measurerBot.x, self.measurerBot.y)
        self.graph = {}
        self.graphLinks = []
        self.adjacencyList = {}
        self.hasObj = False
        self.mainPath = []
        self.mainPathIndex = 0
        self.lastObj = self.initMeasurerPos



        initObjectives = []
        for i in range(self.nbRefPointBots):
            initObjectives.append((self.measurerBot.x + initRadius*np.cos(self.theta*i), self.measurerBot.y +initRadius*np.sin(self.theta*i)))
        
        robotsPlaced = []
        for i in range(self.nbRefPointBots):
            distMin = None
            minKey = -1
            for j in range (self.nbRefPointBots):
                if j not in robotsPlaced:
                    dist = distObjList(refPointBots[j], initObjectives[i])
                    if distMin == None or dist < distMin:
                        distMin = dist
                        self.refPointBots[i] = refPointBots[j]
                        minKey = j
            robotsPlaced.append(minKey)
        
        for i in range(self.nbRefPointBots):
            self.refPointBots[i].defineObjective(initObjectives[i])

        for wall in self.room.walls:
            self.walls.append([[wall.x_start, wall.y_start],[wall.x_start+wall.width, wall.y_start]])
            self.walls.append([[wall.x_start, wall.y_start],[wall.x_start, wall.y_start + wall.height]])
            self.walls.append([[wall.x_start + wall.width, wall.y_start],[wall.x_start + wall.width, wall.y_start + wall.height]])
            self.walls.append([[wall.x_start, wall.y_start+wall.height],[wall.x_start+wall.width, wall.y_start + wall.height]])
    
    def initMove(self):
        refPointBotsStatus = self.checkMovingRefPointBots()
        if not refPointBotsStatus[0]:
            # print("define Objective")
            self.refPointBots[self.initCount].defineObjective((self.measurerBot.x + 2000*np.cos(self.theta*self.initCount), self.measurerBot.y +2000*np.sin(self.theta*self.initCount)))
            self.initCount += 1
        # else :
        #     if not self.check3RefPointBotsAvailable(refPointBotsStatus[1]):
        #         self.refPointBots[refPointBotsStatus[1]].wallDetectionAction()


    def checkMovingRefPointBots(self):
        for key in self.refPointBots:
            if self.refPointBots[key].haveObjective:
                return True, key
        return False, None

    def checkMovingMeasurerBot(self):
        if self.measurerBot.haveObjective:
            return True
        return False
    
    def check3RefPointBotsAvailable(self, key):
        refPointBotMoving = self.refPointBots[key]
        countNotvisible = 0
        visibleBots = []
        for keyAnchor in self.refPointBots:
            visible=True
            refPointBot = self.refPointBots[keyAnchor]
            vectorDir = np.array([refPointBot.x - refPointBotMoving.x,refPointBot.y - refPointBotMoving.y])
            for wall in self.walls:
                inter = lineSegmentInter([vectorDir, [refPointBotMoving.x , refPointBotMoving.y]], wall)
                if inter != None:
                    vectorCol = np.array([inter[0] - refPointBotMoving.x, inter[1] - refPointBotMoving.y])
                    if np.dot(vectorDir, vectorCol)>0:
                        if np.linalg.norm(vectorCol) < np.linalg.norm(vectorDir):
                            visible = False
            if not visible:
                countNotvisible+=1
            else:
                visibleBots.append(keyAnchor)
            
        self.refPointBotsVisibleBots[key] = visibleBots
        if self.nbRefPointBots - countNotvisible < 3:
            return False
        return True


    def move(self):
        # print(self.initCount, self.nbRefPointBots)
        
        if self.hasObj:
            if not self.goToObj():
                target = self.findFurthestPoint()
                if target is not None: 
                    self.mainPathIndex = 0
                    print(target)
                    source = self.lastObj
                    weight, self.mainPath = (self.djikstra(source, target))
                    self.lastObj = target
                    print(self.mainPath)
                else : 
                    self.hasObj = False
        
        if self.initCount < self.nbRefPointBots:
            self.initMove()
        if self.initCount == self.nbRefPointBots:
            if not self.checkMovingRefPointBots()[0]:
                self.graph[self.origin] = 1
                self.createGraph()
                # self.drawGraph()
                print(self.graph)
                target = self.findFurthestPoint()
                source = (self.origin[0], self.origin[1])
                weight, self.mainPath = (self.djikstra(source, target))
                self.lastObj = target
                self.hasObj = True
                self.initCount+=1
        # key = 4
        # self.check3RefPointBotsAvailable(key)
        self.createGrid()

    def goToObj(self):
        if self.mainPathIndex < len(self.mainPath):
            if not self.checkMovingMeasurerBot():
                obj = self.mainPath[self.mainPathIndex]
                self.measurerBot.defineObjective(obj)
                self.graph[obj] = 1
                x, y = obj
                w = self.gridWidth
                coordLeft = (x-w, y)
                coordRight = (x+w, y)
                coordTop = (x, y-w)
                coordBottom = (x, y+w)
                coordTopLeft = (x-w, y-w)
                coordTopRight = (x+w, y-w)
                coordBottomRight = (x+w, y+w)
                coordBottomLeft= (x-w, y+w)
                coords = [coordLeft, coordRight, coordTop,coordBottom,coordTopLeft, coordTopRight, coordBottomRight, coordBottomLeft]
                for coord in coords:
                    self.graph[coord] = 1
                self.mainPathIndex +=1
            return True
        return False

    def findFurthestPoint(self):
        maxDist = 10000
        maxCoord = None
        for coord in self.graph:
            if self.graph[coord] == 0:
                dist = distLists(self.lastObj, coord)
                if  dist < maxDist:
                    maxDist = dist
                    maxCoord = coord
        return maxCoord


    def createGrid(self):
        polygonShapely = Polygon(self.convexHull)
        if len(self.convexHull)>0:
            xmin = int(min(self.convexHull, key=lambda x: x[0])[0])
            ymin = int(min(self.convexHull, key=lambda x: x[1])[1])
            xmax = int(max(self.convexHull, key=lambda x: x[0])[0])
            ymax = int(max(self.convexHull, key=lambda x: x[1])[1])

            for x in range (self.origin[0], xmax+self.gridWidth, self.gridWidth):
                for y in range(self.origin[1], ymax+self.gridWidth, self.gridWidth):
                    if (x, y) not in self.graph:
                        point = Point(x, y)
                        if polygonShapely.contains(point):
                            self.graph[(x, y)] = 0
                for y in range(self.origin[1]-self.gridWidth, ymin - self.gridWidth, -self.gridWidth):
                    if (x, y) not in self.graph:
                        point = Point(x, y)
                        if polygonShapely.contains(point):
                            self.graph[(x, y)] = 0
            for x in range (self.origin[0]-self.gridWidth, xmin -self.gridWidth, -self.gridWidth):
                for y in range(self.origin[1], ymax+self.gridWidth, self.gridWidth):
                    if (x, y) not in self.graph:
                        point = Point(x, y)
                        if polygonShapely.contains(point):
                            self.graph[(x, y)] = 0
                for y in range(self.origin[1]-self.gridWidth, ymin - self.gridWidth, -self.gridWidth):
                    if (x, y) not in self.graph:
                        point = Point(x, y)
                        if polygonShapely.contains(point):
                            self.graph[(x, y)] = 0
    
    def createGraph(self):
        for coord in self.graph:
            if self.graph[coord]!=-1:
                x,y = coord
                w = self.gridWidth
                coordLeft = (x-w, y)
                coordRight = (x+w, y)
                coordTop = (x, y-w)
                coordBottom = (x, y+w)
                coordTopLeft = (x-w, y-w)
                coordTopRight = (x+w, y-w)
                coordBottomRight = (x+w, y+w)
                coordBottomLeft= (x-w, y+w)
                coordsStraight = [coordLeft, coordRight, coordTop,coordBottom]
                coordsDiag = [coordTopLeft, coordTopRight, coordBottomRight, coordBottomLeft]
                for neigh in coordsStraight:
                    if neigh in self.graph:
                        if self.graph[neigh] != -1:
                            if (coord, neigh) not in self.graphLinks and (neigh, coord) not in self.graphLinks:
                                self.graphLinks.append((coord, neigh))
                            if coord not in self.adjacencyList:
                                self.adjacencyList[coord] = [(neigh, 1)]
                            else:
                                if neigh not in self.adjacencyList[coord]:
                                    self.adjacencyList[coord].append((neigh,1))
                            if neigh not in self.adjacencyList:
                                self.adjacencyList[neigh] = [(coord,1)]
                            else:
                                if coord not in self.adjacencyList[neigh]:
                                    self.adjacencyList[neigh].append((coord,1))
                for neigh in coordsDiag:
                    if neigh in self.graph:
                        if self.graph[neigh] != -1:
                            if (coord, neigh) not in self.graphLinks and (neigh, coord) not in self.graphLinks:
                                self.graphLinks.append((coord, neigh))
                            if coord not in self.adjacencyList:
                                self.adjacencyList[coord] = [(neigh, np.sqrt(2))]
                            else:
                                if neigh not in self.adjacencyList[coord]:
                                    self.adjacencyList[coord].append((neigh,np.sqrt(2)))
                            if neigh not in self.adjacencyList:
                                self.adjacencyList[neigh] = [(coord,np.sqrt(2))]
                            else:
                                if coord not in self.adjacencyList[neigh]:
                                    self.adjacencyList[neigh].append((coord,np.sqrt(2)))
                            

    def draw(self, surface1):
        key = 4
        refPointBotsPoints = list(chain.from_iterable([self.refPointBots[keyBot].polygonPoints for keyBot in self.refPointBots]))
        convexHullObstacles = ConvexHull(refPointBotsPoints)
        self.convexHull = [refPointBotsPoints[i] for i in list(convexHullObstacles.vertices)[:]]
        color = self.RGB_tuples[key]
        pygame.draw.polygon(surface1, (*color, 64), self.convexHull)
        for coord in self.graph:
            if self.graph[coord] == 1:
                pygame.draw.rect(surface1, (200, 200, 0, 100), (coord[0]-self.gridWidth//2, coord[1] -self.gridWidth//2, self.gridWidth, self.gridWidth))
            else:
                pygame.draw.rect(surface1, (200, 200, 200, 100), (coord[0]-self.gridWidth//2, coord[1] -self.gridWidth//2, self.gridWidth, self.gridWidth), width = 1)


    def drawGraph(self):
        g = Graph()
        g.add_vertices(len(self.graph))
        g.vs["name"] = list(self.graph.keys())
        for neighbours in self.graphLinks:
                v1 = g.vs['name'].index(neighbours[0])
                v2 = g.vs['name'].index(neighbours[1])
                g.add_edge(v1, v2)
        g.vs["label"] = g.vs["name"]

        layout = g.layout("fr")
        plot(g, layout = layout)

    def djikstra(self, s, t):
        M = set()
        d = {s: 0}
        p = {}
        suivants = [(0, s)] #Â tas de couples (d[x],x)

        while suivants != []:

            dx, x = heappop(suivants)
            if x in M:
                continue

            M.add(x)

            for y, w in self.adjacencyList[x]:
                if y in M:
                    continue
                dy = dx + w
                if y not in d or d[y] > dy:
                    d[y] = dy
                    heappush(suivants, (dy, y))
                    p[y] = x

        path = [t]
        x = t
        while x != s:
            x = p[x]
            path.insert(0, x)

        return d[t], path
                

