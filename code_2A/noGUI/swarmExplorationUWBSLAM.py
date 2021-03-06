from itertools import chain
from heapq import *
from token import SEMI
import random
import time

from scipy.spatial import ConvexHull
from scipy.spatial.qhull import QhullError
import numpy as np

from igraph import *
from igraph.drawing import graph

import refPointBot as refB
from utilities import *
from grid_and_graph import Tile, Grid


# à laisser en bas de la liste des import
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely.ops import nearest_points


class SwarmExploratorUWBSLAM():

    def __init__(self, room, measurerBot, refPointBots, tileWidth):
        self.room = room
        self.measurerBot = measurerBot

        self.grid = Grid(self.room,self.measurerBot,refPointBots,tileWidth)
        self.measurerBot.x, self.measurerBot.y = minDistObjList(self.measurerBot,self.grid.inside)

        self.refPointBots = {}
        self.nbRefPointBots = len(refPointBots)
        self.initRefPointBots = refPointBots
        self.initRadius = tileWidth//2
        
        self.initMeasurerPos = (self.measurerBot.x, self.measurerBot.y)

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
        self.clusterExclusionList = []
        self.RPBExclusionList = []
        self.thirdStepCount = 0

        self.RPBExclusionListWholeStep = []

        self.status = "init"
        self.initCount = 0
        self.moveMeasuringBotCount = 0
        self.moveRefPointBot = 0

        self.targetClusters = 2
        self.instantMoving = True
        self.targetHistory = []
        self.lastRPBBaseCell = None
        self.lastRPBTargetFull = []

        self.time = time.time()

        self.instantMovingRPB = True
        self.lastRPBTarget = [None]
        self.lastRPBMoved = None

        # infinite loop detection :
        self.infiniteLoopList = []
        self.infiniteLoopFirstElement = None
        self.infiniteLoopCount = 0
        self.infiniteLoopFirstIndex = None

        self.targetMethod = self.findTargetV3
        self.clusterExplorationMethod = self.findClosestClusterToOrigin
        # self.clusterExplorationMethod = self.findClosestClusterToMeasurerBot
        self.visitedClusterExplorationMethod = self.findClosestClusterToMeasurerBot
        self.RPBSelectionMethod = self.findLeastUsefulBots
        self.changeFirst = "cluster"
        self.antiLoopMethod = "aggressive"


        for wall in self.room.walls:
            self.walls.append([[wall.x_start, wall.y_start],[wall.x_start+wall.width, wall.y_start]])
            self.walls.append([[wall.x_start, wall.y_start],[wall.x_start, wall.y_start + wall.height]])
            self.walls.append([[wall.x_start + wall.width, wall.y_start],[wall.x_start + wall.width, wall.y_start + wall.height]])
            self.walls.append([[wall.x_start, wall.y_start+wall.height],[wall.x_start+wall.width, wall.y_start + wall.height]])

        self.refPointBotsVisible = self.refPointBots.copy()

        ############ Détection de la fin de la simulation
        self.end_simulation = False


    def set_params(self,params):
        start_pos, start_angle = params
        self.measurerBot.x, self.measurerBot.y = start_pos[0], start_pos[1]
        self.grid.origin = start_pos

        initObjectives = []
        for i in range(self.nbRefPointBots):
            initObjectives.append((self.measurerBot.x + self.initRadius*np.cos(start_angle + self.theta*i), self.measurerBot.y + self.initRadius*np.sin(start_angle + self.theta*i)))

        
        robotsPlaced = []
        for i in range(self.nbRefPointBots):
            distMin = None
            minKey = -1
            for j in range (self.nbRefPointBots):
                if j not in robotsPlaced:

                    dist = distObjList(self.initRefPointBots[j], initObjectives[i])
                    if distMin == None or dist < distMin:
                        distMin = dist
                        self.refPointBots[i] = self.initRefPointBots[j]

                        minKey = j
            robotsPlaced.append(minKey)
        
        for i in range(self.nbRefPointBots):
            #self.refPointBots[i].defineObjective(initObjectives[i])
            self.refPointBots[i].x, self.refPointBots[i].y = initObjectives[i]



    # Sortie du simulateur
    def get_metrics(self):

        measuredTiles, surface, pathLength, history, visitsPerTile = self.grid.get_metrics()

        metrics = { 'nbRefPointBots': self.nbRefPointBots,
                    'nbMeasurerBots': len(self.room.bots)-self.nbRefPointBots,
                    'mb_exp_method' : self.targetMethod.__name__,
                    'rpb_exp_method': self.clusterExplorationMethod.__name__ +" and "+ self.visitedClusterExplorationMethod.__name__,
                    'rpb_sel_method': self.findLeastUsefulBots.__name__,
                    'first_loop'    : self.changeFirst,
                    'measuredTiles' : measuredTiles,
                    'surface'       : surface,
                    'pathLength'    : pathLength,
                    'history'       : history,
                    'visitsPerTile' : visitsPerTile}

        return metrics



    # Initial move of the refPointBots
    def initMove(self):
        refPointBotsStatus = self.checkMovingRefPointBots()
        if not refPointBotsStatus[0]:

            #self.defineConvexHulls()
            if self.instantMovingRefPointBot:
                # if self.initCount == 2:
                #     target = self.instantMovingRefPointBot(self.initCount, (0, 1))
                # elif self.initCount == 6:
                #     target = self.instantMovingRefPointBot(self.initCount, (0, -1))
                # else :
                target = self.instantMovingRefPointBot(self.initCount, (np.cos(self.theta*self.initCount), np.sin(self.theta*self.initCount)))
                self.refPointBots[self.initCount].defineObjective(target)
                self.refPointBots[self.initCount].x, self.refPointBots[self.initCount].y = target
                self.refPointBots[self.initCount].wallDetectionAction()

            else:
                self.refPointBots[self.initCount].defineObjective((self.measurerBot.x + 2000*np.cos(self.theta*self.initCount), self.measurerBot.y +2000*np.sin(self.theta*self.initCount)))
            self.initCount += 1

        else : # Si un point de repère ne voit plus trois autres points de repère, il s'arrête comme s'il avait rencontré un mur
            if not self.check3RefPointBotsAvailable(refPointBotsStatus[1]):
                self.refPointBots[refPointBotsStatus[1]].wallDetectionAction()


    def instantMovingRefPointBot(self, key, vectorDir):
        bot = self.refPointBots[key]
        closest = 100000
        closestInter = None
        for wall in self.walls:
            inter = lineSegmentInter([vectorDir, [bot.x , bot.y]], wall)
            if inter != None:
                vectorCol = np.array([inter[0] - bot.x, inter[1] - bot.y])
                if np.dot(vectorDir, vectorCol)>=0:
                    dist = np.linalg.norm(vectorCol)
                    if dist < closest:
                        closest = dist
                        adjustment = (vectorCol*1/dist)*10
                        closestInter = (int(inter[0] - adjustment[0]), int(inter[1] - adjustment[1]))
        return closestInter


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

        self.grid.update(self.status)


        if self.status == "init":
            if self.initCount < self.nbRefPointBots:
                self.initMove()
                if self.initCount == self.nbRefPointBots:

                    self.status = "FirsttransferRefPointBotToMeasuringBot"      

        
        if self.status == "movingRefPointBot":
            if self.hasObj:
                step = self.goToObj(self.refPointBots[self.nextRefStepGoal[0]])
                if step == "end":
                    self.hasObj = False
                    self.status = "moveRefPointBot2ndStep"


        if self.status == "movingMeasuringBot":
            tTot = time.time()
            if self.hasObj:
                step = self.goToObj()
                if step == "end":
                    t = time.time()
                    self.target = None
                    self.mainPath = None
                    exclusionList = []
                    while self.mainPath is None:
                        target = self.targetMethod(exclusionList)
                        if target is not None: 
                            self.mainPathIndex = 0
                            source = self.lastObj
                            # temporary solution!
                            self.grid.updateNeighOneNode(target)

                            weight, self.mainPath = (self.djikstra(source, target))

                            if self.mainPath is None:
                                exclusionList.append(target)
                            else:
                                self.addWeigthToPath()
                                
                        else : 
                            self.hasObj = False
                            self.status = "moveRefPointBot1stStep"
                            break

                elif step == "changedObj":
                    
                    target = self.targetMethod()

                    if target is not None: 
                        source = self.mainPath[self.mainPathIndex-1][0]
                        self.mainPathIndex = 0
                        weight, self.mainPath = (self.djikstra(source, target))
                        self.addWeigthToPath()
                    else : 
                        self.hasObj = False
                        # self.moveRefPointBotsStep()
                        self.status = "moveRefPointBot1stStep"

                elif step == "changed":

                    target = self.lastObj
                    source = self.mainPath[self.mainPathIndex-1][0]
                    self.mainPathIndex = 0
                    weight, self.mainPath = (self.djikstra(source, target))
                    self.addWeigthToPath()

        if self.status == "FirsttransferRefPointBotToMeasuringBot":

            if not self.checkMovingRefPointBots()[0]:

                #self.updatePolygon()
                #self.defineConvexHulls()
                
                self.grid.graph[self.grid.origin] = 1


                self.grid.updateNeighOneNode(self.grid.origin)
                target = self.targetMethod()
                if target is not None:
                    source = (self.grid.origin[0], self.grid.origin[1])
                    weight, self.mainPath = (self.djikstra(source, target))
                    self.addWeigthToPath()
                    self.hasObj = True
                    self.status = "movingMeasuringBot"
                else:
                    self.hasObj = False
                    # self.moveRefPointBotsStep()
                    self.status = "moveRefPointBot1stStep"


        if self.status == "transferRefPointBotToMeasuringBot":
            if not self.checkMovingRefPointBots()[0]:

                for bot in self.refPointBots:
                    if isinstance(self.refPointBots[bot],refB.RefPointBot):
                        self.refPointBots[bot].isMoving = False


                #self.updatePolygon()
                #self.defineConvexHulls()
                self.target = None
                self.mainPath = None
                exclusionList = []
                while self.mainPath is None:
                    target = self.targetMethod(exclusionList)
                    if target is not None: 
                        self.mainPathIndex = 0
                        source = self.lastObj
                        # temporary solution!
                        self.grid.updateNeighOneNode(target)

                        weight, self.mainPath = (self.djikstra(source, target))

                        if self.mainPath is None:
                            exclusionList.append(target)
                        else:
                            self.addWeigthToPath()
                            self.hasObj = True
                            self.status = "movingMeasuringBot"
                            self.initCount+=1
                            
                    else : 
                        self.hasObj = False
                        self.status = "moveRefPointBot1stStep"
                        self.initCount = len(self.refPointBots) + 2 
                        break


        if self.status == "moveRefPointBot1stStep" or self.status == "moveRefPointBot2ndStep" or self.status == "moveRefPointBot3rdStep":
            self.moveRefPointBotsStep()


    # find closest cell to define as objective for Djikstra    
    def findTargetV1(self, exclusionList=[]):
        minDist = 10000
        minCoord = None
        for coord in self.grid.graph:
            if self.grid.graph[coord] == 0.5 and coord not in exclusionList:
                dist = distObjList(self.measurerBot, coord)
                if dist < minDist:
                    minDist = dist
                    minCoord = coord
        return minCoord
    

    def findTargetV2(self, exclusionList=[]):
        minDist = 10000
        minCoord = []
        for coord in self.grid.graph:
            if self.grid.graph[coord] == 0.5 and coord not in exclusionList:
                dist = distObjList(self.measurerBot, coord)
                if dist < minDist:
                    minDist = dist
                    minCoord = [coord]
                elif dist == minDist:
                    minCoord.append(coord)
        minx = 10000
        minCoordx = []
        for coord in minCoord:
            if coord[0] < minx:
                minCoordx = [coord]
            elif coord[0] == minx:
                    minCoordx.append(coord)
        miny = 10000
        minCoordy = []
        for coord in minCoordx:
            if coord[0] < miny:
                minCoordy = [coord]
            elif coord[0] == miny:
                    minCoordy.append(coord)
        if len(minCoordy) == 0:
            return None
        return minCoordy[0]


    def findTargetV3(self, exclusionList=[]):
        minDist = 10000
        minCoord = None
        for coord in self.grid.graph:
            if self.grid.graph[coord] == 0.5  and coord not in exclusionList:
                dist = distObjList(self.measurerBot, coord)
                if dist < minDist:
                    minDist = dist
                    minCoord = coord
        neigh = self.getNeighbours(self.lastObj)
        for coord in neigh:
            if coord in self.grid.graph and self.grid.graph[coord] == 0.5 and coord not in exclusionList:
                if coord not in self.targetHistory:
                    self.targetHistory.append(coord)
        if minCoord is not None and minCoord not in self.targetHistory:
            self.targetHistory.append(minCoord)
        if len(self.targetHistory) == 0:
            return None
        for coord in self.targetHistory:
            if coord not in exclusionList:
                dist = distObjList(self.measurerBot, coord)
                if dist == minDist:
                    self.targetHistory.remove(coord)
                    return coord


    def findClosestVisitedCell(self, point):
        minDist = 10000
        minCoord = None
        for coord in self.grid.graph:
            if self.grid.graph[coord] == 1:
                dist = distLists(point, coord)
                if dist < minDist:
                    minDist = dist
                    minCoord = coord
        return minCoord


    def findClosestVisitedCellSmart(self, point, source=False):
            minDist = 10000
            minCoord = None
            for coord in self.grid.graph:
                if self.grid.graph[coord] == 1:
                    dist = distLists(point, coord)
                    if dist < minDist:
                        visible = True
                        vectorDir = np.array([coord[0] - point[0],coord[1] - point[1]])
                        for wall in self.walls:
                            inter = lineSegmentInter([vectorDir, point], wall)
                            if inter != None:
                                vectorCol = np.array([inter[0] - point[0], inter[1] - point[1]])
                                if np.dot(vectorDir, vectorCol)>0:
                                    if np.linalg.norm(vectorCol) < np.linalg.norm(vectorDir):
                                        visible = False
                                        break
                        if visible :
                            minDist = dist
                            minCoord = coord
            if source:
                if minDist <= 2*np.sqrt(2)*self.grid.tileWidth:
                    return minCoord
                else:
                    return None
            else :
                return minCoord

              
    # add status of all the cells in the paths as info for dynamic Djikstra
    def addWeigthToPath(self):
        for i in range(len(self.mainPath)):
            self.mainPath[i] = [self.mainPath[i], self.grid.graph[self.mainPath[i]]]


    # attributes intermediary objectives to the measurerBot
    def goToObj(self, bot = None):
        if bot is None:
            bot = self.measurerBot
        if self.mainPathIndex < len(self.mainPath):
            if not self.checkMovingMeasurerBot():
                status = self.checkPathUpdates(self.mainPathIndex)
                #print(status)
                if status == "ok":
                    obj = self.mainPath[self.mainPathIndex][0]
                    
                    if self.instantMoving:
                        bot.defineObjective(obj)
                        x, y = obj
                        bot.x, bot.y = obj
                    else:
                        bot.defineObjective(obj)               
                    if bot == self.measurerBot:
                        if self.grid.graph[obj] != 1:
                            self.grid.graph[obj] = 1
                        self.lastObj = obj
                    
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
                try:
                    convexHullObstacles = ConvexHull(coordList)
                except QhullError:
                    "polygon shape incorrect, not taken into account"
                    continue
                polygon = [(coordList[i],refPointBotsPoints[i][2]) for i in list(convexHullObstacles.vertices)[:]]
                self.polygons.append(coordList)
                polygonsBot.append(refPointBotsPoints)
        leastUseful = (np.pi,None)
        for polygon in polygonsBot:
            for i in range(len(polygon)):
                selfCoord, selfKey = polygon[i][:2], polygon[i][2]

                if selfKey != self.lastRPBMoved and selfKey not in self.RPBExclusionList and selfKey not in self.RPBExclusionListWholeStep:

                    v1 = polygon[(i-1)%(len(polygon))][:2]
                    v2 = polygon[(i+1)%(len(polygon))][:2]
                    vect1 = (v1[0]-selfCoord[0], v1[1] - selfCoord[1])
                    vect2 = (v2[0]-selfCoord[0], v2[1] - selfCoord[1])
                    theta = signedAngle2Vects2(vect1, vect2)
                    if abs(abs(theta)-np.pi) < leastUseful[0]:
                        leastUseful = (abs(abs(theta)-np.pi), selfKey)

        key = leastUseful[1]
        if key is None:
            key = self.findLeastUsefulBotsNoPolygons()
        return key


    def findLeastUsefulBotsNoPolygons(self):
        # find furthest RPB (available)
        #print("No polygons left!")
        maxDist = 0
        bestBot = None
        for bot in self.refPointBots:
            if bot != self.lastRPBMoved and bot not in self.RPBExclusionList and bot not in self.RPBExclusionListWholeStep :

                dist = distObj(self.refPointBots[bot], self.measurerBot)
                if dist > maxDist:
                    maxDist = dist
                    bestBot = bot 

        return bestBot

      
    def findLeastUsefulBotsV2(self):
        self.defineConvexHulls()
        self.polygons = []
        polygonsBot = []
        for hull in self.convexHulls:
            # doesn't break triangles
            if len(hull)>=4:
                refPointBotsPoints = list(chain.from_iterable([[[self.refPointBots[keyBot].x, self.refPointBots[keyBot].y, keyBot]] for keyBot in hull]))
                coordList = [refPointBotsPoints[i][:2] for i in range(len(refPointBotsPoints))]
                try:
                    convexHullObstacles = ConvexHull(coordList)
                except QhullError:
                    "polygon shape incorrect, not taken into account"
                    continue
                polygon = [(coordList[i],refPointBotsPoints[i][2]) for i in list(convexHullObstacles.vertices)[:]]
                self.polygons.append(coordList)
                polygonsBot.append(refPointBotsPoints)
        leastUseful = (np.pi,None)
        leastUsefulDict = {}
        for polygon in polygonsBot:
            n = len(polygon)
            for i in range(n):
                selfCoord, selfKey = polygon[i][:2], polygon[i][2]
                if selfKey != self.lastRPBMoved and selfKey not in self.RPBExclusionList and selfKey not in self.RPBExclusionListWholeStep:
                    v1 = polygon[(i-1)%(len(polygon))][:2]
                    v2 = polygon[(i+1)%(len(polygon))][:2]
                    vect1 = (v1[0]-selfCoord[0], v1[1] - selfCoord[1])
                    vect2 = (v2[0]-selfCoord[0], v2[1] - selfCoord[1])
                    theta = signedAngle2Vects2(vect1, vect2)
                    if abs(abs(theta)-np.pi) < leastUseful[0]:
                        leastUseful = (abs(abs(theta)-np.pi), selfKey)
                    dist = distObjList(self.measurerBot, selfCoord)
                    leastUsefulDict[selfKey] = (abs(abs(theta)-np.pi), dist)
        bestBot = leastUseful[1]
        if bestBot is None:
            bestBot = self.findLeastUsefulBotsNoPolygons()
            return bestBot
        bestAngle = leastUseful[0]
        maxDist = leastUsefulDict[leastUseful[1]][1]
        for element in leastUsefulDict:
            if leastUsefulDict[element][0]  <= bestAngle + np.pi/6 and leastUsefulDict[element][1] > maxDist:
                maxDist = leastUsefulDict[element][1]
                bestBot = element
        return element
        

    def findClosestClusterToOrigin(self):
        minDist = 10000
        closestGoal = None
        for goal in self.nextRefStepGoals:
            if goal not in self.clusterExclusionList:
                dist = distLists(self.initMeasurerPos, goal)
                if dist < minDist:
                    minDist = dist
                    closestGoal = goal
        return closestGoal

    def findClosestClusterToMeasurerBot(self):
        minDist = 10000
        closestGoal = None
        for goal in self.nextRefStepGoals:
            if goal not in self.clusterExclusionList:
                dist = distLists((self.measurerBot.x, self.measurerBot.y), goal)
                if dist < minDist:
                    minDist = dist
                    closestGoal = goal
        return closestGoal


    def moveRefPointBotsStep(self):

        if not self.checkMovingRefPointBots()[0] and not self.checkMovingMeasurerBot():
            
            if self.status == "moveRefPointBot1stStep":
                self.checkMeasurerBotCovered()
                key = self.RPBSelectionMethod()
                #print("key chose : ", key)
                if  self.clusterExclusionList == []:
                    self.explorableClusters = []
                    self.explorableClustersDict = {}
                    self.nearestPoints = []
                    self.nextRefStepGoals = {}
                    self.nextRefStepGoal = None
                    self.detectExplorablePart()
                    self.defineGravityCenterExplorableClusters()
                if self.end_simulation : return
                if self.targetClusters == 2:
                    nextGoal = self.clusterExplorationMethod()
                elif self.targetClusters == 1.5:
                    nextGoal = self.visitedClusterExplorationMethod()
                #print("cluster chose : ", nextGoal)
                if key is None and nextGoal is not None:
                    if self.changeFirst == "cluster":
                        self.end_simulation = True
                    else :
                        self.clusterExclusionList.append(nextGoal)
                        if self.targetClusters == 2:
                            nextGoal = self.clusterExplorationMethod()
                        elif self.targetClusters == 1.5:
                            nextGoal = self.visitedClusterExplorationMethod()

                        #print("cluster chose after exclusion : ", nextGoal)
                        if nextGoal is None:
                            if self.targetClusters == 2:
                                self.targetClusters = 1.5
                                self.RPBExclusionList = []
                                self.clusterExclusionList = []
                                #print("existing explorable clusters but none accessible, moving to visited clusters")
                                self.moveRefPointBotsStep()    
                            elif self.targetClusters == 1.5:
                                self.end_simulation = True
                        else:    
                            self.RPBExclusionList = []
                            #print("current cluster not accessible by any RPB, moving to other clusters")
                            self.moveRefPointBotsStep()


                if nextGoal is None:
                    if self.targetClusters == 2 and not self.end_simulation:
                        if self.changeFirst == "cluster":
                            self.targetClusters = 1.5
                            self.RPBExclusionList = []
                            self.clusterExclusionList = []
                            #print("existing explorable clusters but none accessible, moving to visited clusters")
                            self.moveRefPointBotsStep()    
                        elif self.changeFirst == "RPB":
                            if key is None:
                                self.targetClusters = 1.5
                                self.RPBExclusionList = []
                                self.clusterExclusionList = []
                                #print("existing explorable clusters but none accessible, moving to visited clusters")
                                self.moveRefPointBotsStep() 

                            else :
                                #print("current RPB can't access any (not explored) cluster, moving to other RPBs")
                                self.RPBExclusionList.append(key)
                                self.clusterExclusionList = []
                                self.moveRefPointBotsStep()    

                    else : 
                        if self.changeFirst == "cluster":
                            self.end_simulation = True  
                        elif self.changeFirst == "RPB":
                            if key is None:
                                self.end_simulation = True
                            else:
                                #print("current RPB can't access any (visited) cluster, moving to other RPBs")
                                self.RPBExclusionList.append(key)
                                self.clusterExclusionList = []
                                self.moveRefPointBotsStep() 
                       
                if key is not None:
                    self.refPointBots[key].isMoving = True
                    for bot in self.refPointBots:
                        self.refPointBots[bot].color = (0, 0, 255)
                    self.refPointBots[key].color = (150, 0, 255)
                
                if nextGoal is not None and key is not None:
                    targetCell = self.findClosestVisitedCellSmart(nextGoal)
                    sourceCell = self.findClosestVisitedCellSmart((self.refPointBots[key].x, self.refPointBots[key].y), source=True)
                    minBot = key
                    self.nextRefStepGoal = [minBot, nextGoal]
                    if sourceCell is None:
                        #print("RPB in non covered space, trying other RPB")
                        self.RPBExclusionListWholeStep.append(key)
                        self.moveRefPointBotsStep()
                    else:
                        weight, self.mainPath = (self.djikstra(sourceCell, targetCell))
                        self.mainPathIndex = 0
                        if self.mainPath is not None:
                            if self.antiLoopMethod == "aggressive":
                                self.infiniteLoopDetectionAggressive(nextGoal)
                            elif self.antiLoopMethod == "patient":
                                self.infiniteLoopDetection(targetCell, sourceCell, key)
                            self.lastRPBMoved = key
                            self.lastRPBBaseCell = targetCell
                            self.targetClusters = 2
                            self.clusterExclusionList = []
                            self.RPBExclusionList = []
                            self.RPBExclusionListWholeStep = []
                            self.addWeigthToPath()
                            self.hasObj = True
                            self.status = "movingRefPointBot"
                            #print("__________________________________________")
                        else:
                            if self.changeFirst == "RPB":
                                #print("cluster unreachable by RPB, tryin other RPB")
                                self.RPBExclusionList.append(key)
                                self.moveRefPointBotsStep()
                            elif self.changeFirst == "cluster":
                                #print("cluster unreachable by RPB, tryin other cluster")
                                self.clusterExclusionList.append(nextGoal)
                                self.moveRefPointBotsStep()

            elif self.status == "moveRefPointBot2ndStep":
                if self.instantMovingRefPointBot:
                    bot = self.refPointBots[self.nextRefStepGoal[0]]
                    vec = self.nextRefStepGoals[self.nextRefStepGoal[1]]
                    if vec in self.lastRPBTarget or (vec, self.lastRPBBaseCell) in self.lastRPBTargetFull:
                        n=len(self.lastRPBTarget)
                        self.nextRefStepGoals[self.nextRefStepGoal[1]] = rot2D(vec, ((-1)**(n+1))*(1/((n+1)//2))*np.pi/6)
                        vec = self.nextRefStepGoals[self.nextRefStepGoal[1]]
                        self.lastRPBTarget.append(vec)
                        self.lastRPBTargetFull.append((vec, self.lastRPBBaseCell))
                    else :
                         self.lastRPBTarget = [vec]
                         self.lastRPBTargetFull.append((vec, self.lastRPBBaseCell))
                    target = self.instantMovingRefPointBot(self.nextRefStepGoal[0], self.nextRefStepGoals[self.nextRefStepGoal[1]])
                    if target is None:
                        self.RPBExclusionList.append(bot)
                    else:
                        bot.defineObjective(target)
                        bot.x, bot.y = target
                        bot.wallDetectionAction()
                else :
                    self.refPointBots[self.nextRefStepGoal[0]].defineObjective(self.nextRefStepGoals[self.nextRefStepGoal[1]])
                self.mainPathIndex = 0
                self.status = "moveRefPointBot3rdStep"
            # step used to wait for the map to be updated
            elif self.status == "moveRefPointBot3rdStep":
                if not self.checkMovingRefPointBots()[0]:
                    if self.thirdStepCount == 2:
                        self.thirdStepCount = 0
                        self.status = "transferRefPointBotToMeasuringBot"
                    else :
                        for bot in self.refPointBots:
                            if isinstance(self.refPointBots[bot],refB.RefPointBot):
                                self.refPointBots[bot].isMoving = False
                        self.thirdStepCount +=1


    def checkMeasurerBotCovered(self):
        if self.grid.graph[self.lastObj] == 1.5:
            #print("measurerBot not covered, switching to visited clusters")
            self.targetClusters = 1.5


    def infiniteLoopDetection(self, target, source, key):
        newElement = (source, target, key, self.targetClusters)
        if self.infiniteLoopCount == 0:
            if newElement in self.infiniteLoopList:
                self.infiniteLoopFirstElement = newElement
                self.infiniteLoopFirstIndex = self.infiniteLoopList.index(newElement)
                self.infiniteLoopCount +=1
                #print("first loop detected!")
        else:
            if newElement == self.infiniteLoopFirstElement:
                self.infiniteLoopCount +=1
                #print("new loop iteration : ", self.infiniteLoopCount)
            elif newElement != self.infiniteLoopList[self.infiniteLoopFirstIndex]:
                self.infiniteLoopFirstElement = None
                self.infiniteLoopCount = 0
                self.infiniteLoopFirstIndex = None
                #print("loop ended")
                if newElement in self.infiniteLoopList:
                    self.infiniteLoopFirstElement = newElement
                    self.infiniteLoopFirstIndex = self.infiniteLoopList.index(newElement)
                    self.infiniteLoopCount +=1
                    #print("first loop detected!")
        
        if len(self.infiniteLoopList) > 20:
            self.infiniteLoopList.pop()
        self.infiniteLoopList = [newElement] + self.infiniteLoopList

        if self.infiniteLoopCount >= 5:
            self.end_simulation = True


    def infiniteLoopDetectionAggressive(self, cluster):
        newElement = (cluster, self.targetClusters)
        if self.infiniteLoopCount == 0:
            if newElement in self.infiniteLoopList:
                self.infiniteLoopFirstElement = newElement
                self.infiniteLoopFirstIndex = self.infiniteLoopList.index(newElement)
                self.infiniteLoopCount +=1
                #print("first loop detected!")
        else:
            if newElement == self.infiniteLoopFirstElement:
                self.infiniteLoopCount +=1
                #print("new loop iteration : ", self.infiniteLoopCount)
            elif newElement != self.infiniteLoopList[self.infiniteLoopFirstIndex]:
                self.infiniteLoopFirstElement = None
                self.infiniteLoopCount = 0
                self.infiniteLoopFirstIndex = None
                #print("loop ended")
                if newElement in self.infiniteLoopList:
                    self.infiniteLoopFirstElement = newElement
                    self.infiniteLoopFirstIndex = self.infiniteLoopList.index(newElement)
                    self.infiniteLoopCount +=1
                    #print("first loop detected!")
        
        if len(self.infiniteLoopList) > 20:
            self.infiniteLoopList.pop()
        self.infiniteLoopList = [newElement] + self.infiniteLoopList

        if self.infiniteLoopCount >= 5:
            self.end_simulation = True

            
    def detectExplorablePart(self):
        for coord in self.grid.graph:  
            if self.grid.graph[coord] == self.targetClusters:
                neighbours = self.getNeighbours(coord)
                neighInCluster = False
                for neigh in neighbours:
                    for cluster in self.explorableClusters:
                        if neigh in cluster:
                            cluster.add(coord)
                            neighInCluster = True
                if not neighInCluster:
                    self.explorableClusters.append({coord})

        if self.explorableClusters == []:
            # Fin de simulation , plus de zones oranges, tout a été exploré
            if self.targetClusters == 2:
                self.end_simulation = True   
            # Fin de simulation si les robots UWB n'ont nulle part où aller
            elif self.targetClusters == 1.5:  
                self.end_simulation = True            
        
        # allInterNull = True
        # "clusterize" the explorable cells
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
        if len(self.polygons) == 0 or True:
            for point in self.explorableClustersDict:
                npoint = self.findClosestVisitedCellSmart(point)
                if npoint is not None:
                    vec = (point[0] - npoint[0], point[1] - npoint[1])
                    vec = np.array(vec)
                    vec = vec/np.linalg.norm(vec)
                    vec = list(np.around(vec, 5))
                    # nextGoal = (np.array(vec))*1000
                    self.nearestPoints.append([point, npoint])
                    self.nextRefStepGoals[point] = vec
        else:
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
    

   
