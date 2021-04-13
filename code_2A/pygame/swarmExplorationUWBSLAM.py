from itertools import chain
from heapq import *
from token import SEMI
import random
import time

from scipy.spatial import ConvexHull
import numpy as np

import pygame

from igraph import *
from igraph.drawing import graph

from utilities import *
from grid_and_graph import Tile, Grid


# à laisser en bas de la liste des import
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely.ops import nearest_points


class SwarmExploratorUWBSLAM():
    def __init__(self, surfaceUWB, surfaceGrid, surfaceReferenceBot, room, measurerBot, refPointBots, distRefPointBots = [110, 110], initRadius=50) :
        self.room = room
        self.distRefPointBots = distRefPointBots
        self.measurerBot = measurerBot
        self.refPointBots = {}
        self.nbRefPointBots = len(refPointBots)
        
        self.initMeasurerPos = (self.measurerBot.x, self.measurerBot.y)

        self.surfaceUWB = surfaceUWB
        self.surfaceGrid = surfaceGrid
        self.surfaceReferenceBot = surfaceReferenceBot

        self.theta = 2*np.pi/self.nbRefPointBots
        self.refPointBotsVisibleBots = {}
        self.walls = []
        
        self.hasObj = False
        self.mainPath = []
        self.mainPathIndex = 0
        self.lastObj = self.initMeasurerPos
        self.trajectory = []
        self.explorableClusters = []
        self.explorableClustersDict = {}
        self.nearestPoints = []
        self.nextRefStepGoals = {}
        self.nextRefStepGoal = None
        self.nextRefStepIndex = 0
        self.convexHull = []
        self.convexHulls = []
        self.polygons = []

        self.status = "init"
        self.initCount = 0
        self.moveMeasuringBotCount = 0
        self.moveRefPointBot = 0
        self.instantMoving = True
        self.time = 0
        self.updateUWBcoverArea = self.room.updateUWBcoverArea()

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
            #self.refPointBots[i].defineObjective(initObjectives[i])
            self.refPointBots[i].x, self.refPointBots[i].y = initObjectives[i]


        for wall in self.room.walls:
            self.walls.append([[wall.x_start, wall.y_start],[wall.x_start+wall.width, wall.y_start]])
            self.walls.append([[wall.x_start, wall.y_start],[wall.x_start, wall.y_start + wall.height]])
            self.walls.append([[wall.x_start + wall.width, wall.y_start],[wall.x_start + wall.width, wall.y_start + wall.height]])
            self.walls.append([[wall.x_start, wall.y_start+wall.height],[wall.x_start+wall.width, wall.y_start + wall.height]])

        self.refPointBotsVisible = self.refPointBots.copy()


        self.grid = Grid(self.room,self.measurerBot)


    
    # Initial move of the refPointBots
    def initMove(self):
        refPointBotsStatus = self.checkMovingRefPointBots()
        if not refPointBotsStatus[0]:
            self.updateUWBcoverArea = self.room.updateUWBcoverArea()
            #self.defineConvexHulls()
            self.refPointBots[self.initCount].defineObjective((self.measurerBot.x + 2000*np.cos(self.theta*self.initCount), self.measurerBot.y +2000*np.sin(self.theta*self.initCount)))
            self.initCount += 1

        else : # Si un point de repère ne voit plus trois autres points de repère, il s'arrête comme s'il avait rencontré un mur
            if not self.check3RefPointBotsAvailable(refPointBotsStatus[1]):
                self.refPointBots[refPointBotsStatus[1]].wallDetectionAction()

    # check if refPointBots are moving
    def checkMovingRefPointBots(self):
        for key in self.refPointBots:
            if self.refPointBots[key].haveObjective:
                return True, key
        return False, None

    # check if MeasurerBot is still moving
    def checkMovingMeasurerBot(self):
        if self.measurerBot.haveObjective:
            return True
        return False
    
    # check to see if the refPointBot "key" can see at least 3 other refpointBots
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

        ######################### AJOUT : prise en compte de la portée des balises UWB
        for keyAnchor in visibleBots:
                if distObj(self.refPointBots[keyAnchor],self.refPointBots[key]) > self.refPointBots[key].UWBradius :
                    countNotvisible+=1
                    visibleBots.remove(keyAnchor)
            
        self.refPointBotsVisibleBots[key] = visibleBots
        if self.nbRefPointBots - countNotvisible < 3:
            return False
            
        return True



    # principal move function
    def move(self):

        self.grid.update(self.surfaceUWB,self.status)

        #tMove = time.time()
        #print("########### duration of step : ", tMove - self.time)
        #self.time = tMove

        if self.status == "init":
            if self.initCount < self.nbRefPointBots:
                self.initMove()
                if self.initCount == self.nbRefPointBots:
                    self.status = "FirsttransferRefPointBotToMeasuringBot"
        
        if self.status == "movingRefPointBots":
            self.moveRefPointBotsStep()


        if self.status == "movingMeasuringBot":

            #tTot = time.time()
            if self.hasObj:
                step = self.goToObj()
                if step == "end":

                    target = self.findClosestCell()

                    if target is not None: 
                        self.mainPathIndex = 0
                        source = self.lastObj
                        # temporary solution!
                        # self.grid.updateNeighOneNode(target)
                        weight, self.mainPath = (self.djikstra(source, target))
                        self.addWeigthToPath()
                    else : 
                        self.hasObj = False
                        self.moveRefPointBotsStep()
                        self.status = "movingRefPointBots"
                elif step == "changedObj":
                    
                    target = self.findClosestCell()

                    if target is not None: 
                        source = self.mainPath[self.mainPathIndex-1][0]
                        self.mainPathIndex = 0
                        weight, self.mainPath = (self.djikstra(source, target))
                        self.addWeigthToPath()
                    else : 
                        self.hasObj = False
                        self.moveRefPointBotsStep()
                        self.status = "movingRefPointBots"

                elif step == "changed":

                    target = self.lastObj
                    source = self.mainPath[self.mainPathIndex-1][0]
                    self.mainPathIndex = 0
                    weight, self.mainPath = (self.djikstra(source, target))
                    self.addWeigthToPath()

                # print("duration of tTot : ", time.time() - tTot)

        if self.status == "FirsttransferRefPointBotToMeasuringBot":

            if not self.checkMovingRefPointBots()[0]:

                #self.updatePolygon()
                #self.defineConvexHulls()
                self.updateUWBcoverArea = self.room.updateUWBcoverArea()
                
                self.grid.graph[self.grid.origin] = [1]

                # self.drawGraph() # à commenter ou non pour afficher le graphe
                self.grid.updateNeighOneNode(self.grid.origin)
                target = self.findClosestCell()
                if target is not None:
                    source = (self.grid.origin[0], self.grid.origin[1])
                    weight, self.mainPath = (self.djikstra(source, target))
                    self.addWeigthToPath()
                    self.hasObj = True
                    self.status = "movingMeasuringBot"
                else:
                    self.hasObj = False
                    self.moveRefPointBotsStep()
                    self.status = "movingRefPointBots"

        if self.status == "transferRefPointBotToMeasuringBot":

            if not self.checkMovingRefPointBots()[0]:
                
                # self.draw()
                # self.grid.updateGraph()
                self.updateUWBcoverArea = self.room.updateUWBcoverArea()
                #self.updatePolygon()
                #self.defineConvexHulls()
                
                target = self.findClosestCell()
                if target is not None:
                    self.mainPathIndex = 0
                    source = self.lastObj
                    # temporary solution!
                    # self.grid.updateNeighOneNode(target)
                    weight, self.mainPath = (self.djikstra(source, target))
                    self.addWeigthToPath()
                    self.hasObj = True
                    self.status = "movingMeasuringBot"
                    self.initCount+=1
                else:
                    self.hasObj = False
                    self.moveRefPointBotsStep()
                    self.status = "movingRefPointBots"
                    self.initCount = len(self.refPointBots) + 2   

        #print("########### duration of move : ", time.time()- tMove)

    # find closest cell to define as objective for Djikstra    
    def findClosestCell(self):
        minDist = 10000
        minCoord = None
        for coord in self.grid.graph:
            if self.grid.graph[coord] == 0.5:
                dist = distObjList(self.measurerBot, coord)
                if dist < minDist:
                    minDist = dist
                    minCoord = coord
        return minCoord

    # add status of all the cells in the paths as info for dynamic Djikstra
    def addWeigthToPath(self):
        for i in range(len(self.mainPath)):
            self.mainPath[i] = [self.mainPath[i], self.grid.graph[self.mainPath[i]]]

   

    # attributes intermediary objectives to the measurerBot
    def goToObj(self):
        if self.mainPathIndex < len(self.mainPath):
            if not self.checkMovingMeasurerBot():
                status = self.checkPathUpdates(self.mainPathIndex)
                #print(status)
                if status == "ok":
                    obj = self.mainPath[self.mainPathIndex][0]
                    self.lastObj = obj
                    if self.instantMoving:
                        self.measurerBot.defineObjective(obj)
                        x, y = obj
                        self.measurerBot.x, self.measurerBot.y = obj
                    else:
                        self.measurerBot.defineObjective(obj)               

                    if self.grid.graph[obj] != 1:
                        self.grid.graph[obj] = 1
                    
                    x, y = obj
                    self.mainPathIndex +=1
                return status
            return "moving"
        return "end"


    def findFurthestCell(self):
        maxDist = 0
        maxCoord = None

        for coord in self.grid.graph:
            if self.grid.graph[coord] == 0.5:
                dist = distLists(self.lastObj, coord)
                if  dist > maxDist:
                    maxDist = dist
                    maxCoord = coord

        return maxCoord


    def djikstra(self, s, t):
        M = set()
        d = {s: 0}
        p = {}
        suivants = [(0, s)]

        while suivants != []:

            dx, x = heappop(suivants)
            if x in M:
                continue

            M.add(x)

            for y, w in self.grid.adjacencyList[x]:
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
            if x in p:
                x = p[x]
                path.insert(0, x)
            else:
                return None, None

        return d[t], path


    def checkPathUpdates(self, index):
        for element in self.mainPath[index:]:
            coord, weight = element[0], element[1]
            if self.grid.graph[coord] == -1:
                if coord == self.lastObj:
                    return "changedObj"
                else:
                    return "changed"
            
        return "ok"


    def findLeastUsefulBots(self):
        self.defineConvexHulls()
        self.polygons = []
        polygonsBot = []
        for hull in self.convexHulls:
            if len(hull)>=3:
                refPointBotsPoints = list(chain.from_iterable([[[self.refPointBots[keyBot].x, self.refPointBots[keyBot].y, keyBot]] for keyBot in hull]))
                coordList = [refPointBotsPoints[i][:2] for i in range(len(refPointBotsPoints))]
                convexHullObstacles = ConvexHull(coordList)
                polygon = [(coordList[i],refPointBotsPoints[i][2]) for i in list(convexHullObstacles.vertices)[:]]
                self.polygons.append(coordList)
                polygonsBot.append(polygon)
        leastUseful = (np.pi,0)
        for polygon in polygonsBot:
            for i in range(len(polygon)):
                selfCoord, selfKey = polygon[i]
                v1 = polygon[(i-1)%(len(polygon))][0]
                v2 = polygon[(i+1)%(len(polygon))][0]
                vect1 = (v1[0]-selfCoord[0], v1[1] - selfCoord[1])
                vect2 = (v2[0]-selfCoord[0], v2[1] - selfCoord[1])
                theta = signedAngle2Vects2(vect1, vect2)
                if abs(abs(theta)-np.pi) < leastUseful[0]:
                    leastUseful = (abs(abs(theta)-np.pi), selfKey)
        return leastUseful[1]


    def moveRefPointBotsStep(self):
        if not self.checkMovingRefPointBots()[0] and not self.checkMovingMeasurerBot():
            key = self.findLeastUsefulBots()
            for bot in self.refPointBots:
                self.refPointBots[bot].color = (0, 0, 255)
            self.refPointBots[key].color = (150, 0, 255)
            if self.nextRefStepIndex == 0:
                #self.defineConvexHulls()
                self.explorableClusters = []
                self.explorableClustersDict = {}
                self.nearestPoints = []
                self.nextRefStepGoals = {}
                self.nextRefStepGoal = None
                self.nextRefStepIndex = 0
                self.detectExplorablePart()
                self.defineGravityCenterExplorableClusters()
                nextGoal = None
                for goal in self.nextRefStepGoals:
                    nextGoal = goal
                    break
                if nextGoal!=None:
                    mindist = 10000
                    minBot = None
                    for bot in self.refPointBots:
                        dist = distObjList(self.refPointBots[bot], nextGoal)
                        if dist < mindist : 
                            mindist = dist
                            minBot = bot
                    minBot = key
                    self.nextRefStepGoal = [minBot, nextGoal]
                    self.refPointBots[minBot].defineObjective(nextGoal)
                    self.nextRefStepIndex += 1
            elif self.nextRefStepIndex == 1 :
                if distObjList(self.refPointBots[self.nextRefStepGoal[0]], self.nextRefStepGoal[1]) < 3:
                    self.refPointBots[self.nextRefStepGoal[0]].defineObjective(self.nextRefStepGoals[self.nextRefStepGoal[1]])
                    self.nextRefStepIndex = 0
                    self.status = "transferRefPointBotToMeasuringBot"
                else:
                    self.refPointBots[self.nextRefStepGoal[0]].defineObjective(self.nextRefStepGoal[1])
    

    def detectExplorablePart(self):
        for coord in self.grid.graph:  
            if self.grid.graph[coord] == 2:
                neighbours = self.getNeighbours(coord)
                neighInCluster = False
                for neigh in neighbours:
                    for cluster in self.explorableClusters:
                        if neigh in cluster:
                            cluster.add(coord)
                            neighInCluster = True
                if not neighInCluster:
                    self.explorableClusters.append({coord})
        
        # allInterNull = True
        index = 0
        i=1
        while index < len(self.explorableClusters):
            while i < len(self.explorableClusters):
                if i != index:
                    if len(self.explorableClusters[index].intersection(self.explorableClusters[i]))>0:
                        self.explorableClusters[index] = self.explorableClusters[index].union(self.explorableClusters[i])
                        self.explorableClusters.pop(i)
                    else :
                        i+=1
            index+=1
            i = index+1


    def defineGravityCenterExplorableClusters(self):
        for cluster in self.explorableClusters:
            l = len(cluster)
            avgx = 0
            avgy = 0
            for coord in cluster:
                x,y = coord
                avgx+=x
                avgy+=y
            avgx=avgx//l
            avgy= avgy//l
            self.explorableClustersDict[(avgx, avgy)]=cluster
        
        polygonShapely = Polygon(self.polygons[0])
        for polygon in self.polygons[1:]:
            polygonShapely = polygonShapely.union(Polygon(polygon))
        linestr = polygonShapely.boundary
        for point in self.explorableClustersDict:
            pointShapely = Point(point)
            npoint = nearest_points(pointShapely, linestr)
            line=[]
            for p in npoint:
                line.append(p.coords[:][0])
            vec = (line[0][0] - line[1][0], line[0][1] - line[1][1])
            nextGoal = (np.array(vec))*1000
            self.nearestPoints.append(line)
            self.nextRefStepGoals[point] = nextGoal


    def getNeighbours(self, coord):
        x,y = coord
        w = self.grid.tileWidth
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

      
    def defineConvexHulls(self):
        for key in self.refPointBots:
            self.check3RefPointBotsAvailable(key)
        convexHulls = []
        changed  = True
        while changed:
            changed = False
            for key in self.refPointBotsVisibleBots:
                noHullVisible = True
                for hull in convexHulls:
                    if key in hull:
                        noHullVisible = False
                    else:
                        hullVisible=True 
                        for bot in hull:
                            if bot not in self.refPointBotsVisibleBots[key]:
                                hullVisible=False
                                break
                        if hullVisible:
                            hull.append(key)
                            noHullVisible = False
                            changed = True
                if noHullVisible:
                    convexHulls.append([key])
                    changed = True

        self.convexHulls = convexHulls
    
   
    def draw(self):
        # on réinitialise les surfaces
        self.surfaceUWB.fill((0,0,0,0))
        self.surfaceGrid.fill((0,0,0,0))
        self.surfaceReferenceBot.fill((0,0,0,0))

        # on affiche la zone UWB et la grille
        # t = time.time()
        self.surfaceUWB.blit(self.updateUWBcoverArea,(0,0), special_flags=pygame.BLEND_RGBA_MAX)
        # print("duration of self.room.updateUWBcoverArea() : ", time.time() - t)
        self.grid.draw(self.surfaceGrid)      

                
        for i in range(len(self.mainPath)-1):
            line = (self.mainPath[i][0], self.mainPath[i+1][0])
            if line not in self.trajectory:
                self.trajectory.append(line)
        for line in self.trajectory:
            pygame.draw.line(self.surfaceReferenceBot, (0, 0, 100, 200), line[0], line[1], 3)
        for coord in self.explorableClustersDict:
            pygame.draw.circle(self.surfaceReferenceBot, (200, 100, 0, 200), coord, 4)
        for coord in self.nearestPoints:
            p1 = coord[0]
            p2 = coord[1]
            a = (p1[1]-p2[1])/(p1[0]-p2[0])
            b = p1[1]-a*p1[0]
            pygame.draw.line(self.surfaceReferenceBot, (200, 0, 200, 200),(0,int(b)), (1600,int(a*1600+b)) , 1)
        # print(self.grid.adjacencyList)

