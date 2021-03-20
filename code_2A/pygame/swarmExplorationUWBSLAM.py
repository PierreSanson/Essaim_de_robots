from token import SEMI
from igraph.drawing import graph

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

# à laisser en bas de la liste des import
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon



class SwarmExploratorUWBSLAM():
    def __init__(self, surface, room, measurerBot, refPointBots, distRefPointBots = [110, 110], initRadius=50) :
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
        self.surface = surface
        self.initCount = 0
        self.theta = 2*np.pi/self.nbRefPointBots
        self.refPointBotsVisibleBots = {}
        HSV_tuples = [(x*1.0/self.nbRefPointBots, 0.5, 0.5) for x in range(self.nbRefPointBots)]
        self.RGB_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))
        self.walls = []
        self.convexHull = []
        self.gridWidth = 60
        self.origin = (self.measurerBot.x, self.measurerBot.y)
        self.graph = {}
        self.graphLinks = []
        self.adjacencyList = {}
        self.hasObj = False
        self.mainPath = []
        self.mainPathIndex = 0
        self.lastObj = self.initMeasurerPos
        self.trajectory = []



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

        self.refPointBotsVisible = self.refPointBots.copy()
    
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

    def updatePolygon(self):
        self.refPointBotsVisible = {}
        for key in self.refPointBots:
            if self.check3RefPointBotsAvailable(key):
                self.refPointBotsVisible[key] = self.refPointBots[key]


    def move(self):
        # print(self.initCount, self.nbRefPointBots)
        
        if self.hasObj:
            step = self.goToObj()
            if step == "end":
                self.updatePolygon()
                refPointBotsPoints = list(chain.from_iterable([self.refPointBots[keyBot].polygonPoints for keyBot in self.refPointBotsVisible]))
                convexHullObstacles = ConvexHull(refPointBotsPoints)
                self.convexHull = [refPointBotsPoints[i] for i in list(convexHullObstacles.vertices)[:]]
                self.updateGrid()
                target = self.findFurthestPoint()
                if target is not None: 
                    self.mainPathIndex = 0
                    print(target)
                    source = self.lastObj
                    weight, self.mainPath = (self.djikstra(source, target))
                    self.addWeigthToPath()
                    self.lastObj = target
                    print(self.mainPath)
                else : 
                    self.hasObj = False
                    print(self.detectExplorablePart())
            elif step == "changedObj":
                self.updatePolygon()
                refPointBotsPoints = list(chain.from_iterable([self.refPointBots[keyBot].polygonPoints for keyBot in self.refPointBotsVisible]))
                convexHullObstacles = ConvexHull(refPointBotsPoints)
                self.convexHull = [refPointBotsPoints[i] for i in list(convexHullObstacles.vertices)[:]]
                self.updateGrid()
                target = self.findFurthestPoint()
                if target is not None: 
                    source = self.mainPath[self.mainPathIndex-1][0]
                    self.mainPathIndex = 0
                    print(target)
                    weight, self.mainPath = (self.djikstra(source, target))
                    self.addWeigthToPath()
                    self.lastObj = target
                    print(self.mainPath)
                else : 
                    self.hasObj = False
                    print(self.detectExplorablePart())
            elif step == "changed":
                self.updatePolygon()
                refPointBotsPoints = list(chain.from_iterable([self.refPointBots[keyBot].polygonPoints for keyBot in self.refPointBotsVisible]))
                convexHullObstacles = ConvexHull(refPointBotsPoints)
                self.convexHull = [refPointBotsPoints[i] for i in list(convexHullObstacles.vertices)[:]]
                self.updateGrid()
                target = self.lastObj
                source = self.mainPath[self.mainPathIndex-1][0]
                self.mainPathIndex = 0
                print(target)
                weight, self.mainPath = (self.djikstra(source, target))
                self.addWeigthToPath()
                self.lastObj = target
                print(self.mainPath)
            
        
        if self.initCount < self.nbRefPointBots:
            self.initMove()
        if self.initCount == self.nbRefPointBots:
            if not self.checkMovingRefPointBots()[0]:

                self.updatePolygon()
                refPointBotsPoints = list(chain.from_iterable([self.refPointBots[keyBot].polygonPoints for keyBot in self.refPointBotsVisible]))
                convexHullObstacles = ConvexHull(refPointBotsPoints)
                self.convexHull = [refPointBotsPoints[i] for i in list(convexHullObstacles.vertices)[:]]
                self.updateGrid()
                self.graph[self.origin] = 1
                self.createGraph()
                # self.drawGraph()
                print(self.graph)
                coords = self.getNeighbours(self.origin)
                self.updateNeighOneNode(self.origin)
                for coord in coords:
                    if coord not in self.graph or self.graph[coord] == 2 or self.graph[coord] == -1:
                        self.graph[coord] = 2
                    elif self.graph[coord] != 1 : 
                        self.graph[coord] = 0.5
                target = self.findFurthestPoint()
                source = (self.origin[0], self.origin[1])
                weight, self.mainPath = (self.djikstra(source, target))
                self.addWeigthToPath()
                self.lastObj = target
                self.hasObj = True
                self.initCount+=1
        
        self.createGrid()

    def addWeigthToPath(self):
        for i in range(len(self.mainPath)):
            self.mainPath[i] = [self.mainPath[i], self.graph[self.mainPath[i]]]

    def goToObj(self):
        if self.mainPathIndex < len(self.mainPath):
            if not self.checkMovingMeasurerBot():
                status = self.checkPathUpdates(self.mainPathIndex)
                if status == "ok":
                    obj = self.mainPath[self.mainPathIndex][0]
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
                    self.updateNeighOneNode(obj)
                    for coord in coords:
                        if coord not in self.graph or self.graph[coord] == 2 or self.graph[coord] == -1:
                            obs = False
                            print(len(self.room.obstacles))
                            for obstacle in self.room.obstacles_seen:
                                dist = distObjList(obstacle, coord)
                                if dist < self.gridWidth//2:
                                    print("Obstacleeee")
                                    obs = True
                                    break
                            if obs : 
                                self.graph[coord] = -1
                                self.removeNodeFromGraph(coord)

                            else :
                                self.graph[coord] = 2
                        elif self.graph[coord] != 1 : 
                            obs = False
                            print(len(self.room.obstacles))
                            for obstacle in self.room.obstacles_seen:
                                dist = distObjList(obstacle, coord)
                                if dist < self.gridWidth//2:
                                    print("Obstacleeee")
                                    obs = True
                                    break
                            if obs : 
                                self.graph[coord] = -1
                                self.removeNodeFromGraph(coord)
                            else :
                                self.graph[coord] = 0.5
                    self.mainPathIndex +=1
                return status
            return "moving"
        return "end"

    def removeNodeFromGraph(self, coord):
        self.adjacencyList[coord] = []
        neighbours = self.getNeighbours(coord)
        for neigh in neighbours:
            if neigh in self.adjacencyList:
                if coord in self.adjacencyList[neigh]:
                    self.adjacencyList[neigh].remove(coord)


    def findFurthestPoint(self):
        maxDist = 10000
        maxCoord = None
        for coord in self.graph:
            # if self.graph[coord] == 0 or self.graph[coord] == 0.5:
            if self.graph[coord] == 0.5:
                dist = distLists(self.lastObj, coord)
                if  dist < maxDist:
                    maxDist = dist
                    maxCoord = coord
        return maxCoord

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

    def checkPathUpdates(self, index):
        for element in self.mainPath[index:]:
            coord, weight = element[0], element[1]
            if self.graph[coord] == -1:
                if coord == self.lastObj:
                    return "changedObj"
                else:
                    return "changed"
        return "ok"

    def moveRefPointBotsStep(self):
        pass

    def detectExplorablePart(self):
        clusters = []
        for coord in self.graph:  
            if self.graph[coord] == 2:
                neighbours = self.getNeighbours(coord)
                neighInCluster = False
                for neigh in neighbours:
                    for cluster in clusters:
                        if neigh in cluster:
                            cluster.add(coord)
                            neighInCluster = True
                if not neighInCluster:
                    clusters.append({coord})
        
        # allInterNull = True
        index = 0
        i=1
        while index < len(clusters):
            while i < len(clusters):
                if i != index:
                    if len(clusters[index].intersection(clusters[i]))>0:
                        clusters[index] = clusters[index].union(clusters[i])
                        clusters.pop(i)
                    else :
                        i+=1
            index+=1
            i = index+1
        return clusters

    def getNeighbours(self, coord):
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
        coordsNeighbours = [coordLeft, coordRight, coordTop,coordBottom, coordTopLeft, coordTopRight, coordBottomRight, coordBottomLeft]
        return coordsNeighbours


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

    def updateGrid(self):
        polygonShapely = Polygon(self.convexHull)
        for x, y in self.graph:
            if self.graph[(x, y)] != 2:
                point = Point(x, y)
                if not polygonShapely.contains(point):
                    self.graph[(x, y)] = -1

    
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
    
    def updateNeighOneNode(self, coord):
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
                            

    def draw(self):
        refPointBotsPoints = list(chain.from_iterable([self.refPointBots[keyBot].polygonPoints for keyBot in self.refPointBotsVisible]))
        convexHullObstacles = ConvexHull(refPointBotsPoints)
        self.convexHull = [refPointBotsPoints[i] for i in list(convexHullObstacles.vertices)[:]]
        pygame.draw.polygon(self.surface, (0, 0, 100, 64), self.convexHull)
        for coord in self.graph:
            if self.graph[coord] == 1:
                pygame.draw.rect(self.surface, (0, 200, 0, 100), (coord[0]-self.gridWidth//2, coord[1] -self.gridWidth//2, self.gridWidth, self.gridWidth), width = 1)
            elif self.graph[coord] == -1:
                pygame.draw.rect(self.surface, (200, 0, 0, 100), (coord[0]-self.gridWidth//2, coord[1] -self.gridWidth//2, self.gridWidth, self.gridWidth), width = 1)
            elif self.graph[coord] == 2:
                pygame.draw.rect(self.surface, (200, 100, 0, 100), (coord[0]-self.gridWidth//2, coord[1] -self.gridWidth//2, self.gridWidth, self.gridWidth), width = 1)
            elif self.graph[coord] == 0.5:
                    pygame.draw.rect(self.surface, (200, 200, 0, 100), (coord[0]-self.gridWidth//2, coord[1] -self.gridWidth//2, self.gridWidth, self.gridWidth), width = 1)
            else:
                pygame.draw.rect(self.surface, (200, 200, 200, 40), (coord[0]-self.gridWidth//2, coord[1] -self.gridWidth//2, self.gridWidth, self.gridWidth), width = 1)
        for i in range(len(self.mainPath)-1):
            line = (self.mainPath[i][0], self.mainPath[i+1][0])
            if line not in self.trajectory:
                self.trajectory.append(line)
        for line in self.trajectory:
            pygame.draw.line(self.surface, (0, 0, 100, 200), line[0], line[1], 3)


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


                

