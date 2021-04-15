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

        self.time = time.time()

        self.instantMovingRPB = True

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

        ############ Détection de la fin de la simulation
        self.end_simulation = False


    # Sortie du simulateur
    def print_metrics(self):

        print('\r\n')

        ### Résumé des entrées du simulateur
        print('Nombre de robots points de repère : %s' %self.nbRefPointBots)
        print('Nombre de robots mesureurs : %s' %(len(self.room.bots)-self.nbRefPointBots))
        print('Algorithme : déplacement vers la case la plus proche non explorée')  # intégrer le nom de l'algo dans le code, et pouvoir sélectionner
                                                                                    # spéarer algo UWB et algo mesureur
        # autres entrées, pas top à afficher : positions de départ, directions de départ pour les points de repère
        
        print('\r\n')

        measuredTiles, surface, pathLength, history, visitsPerTile = self.grid.get_metrics()
        simulationDuration =  time.time() - self.time      
        ### Sorties du simulateur
        print('Durée de la simulation : %s' %simulationDuration)
        print('Nombre de cases mesurées : %s/%s' %(measuredTiles, surface))
        print('Longueur du parcours : %s cases' %pathLength)
        # autres sorties, pas pratiques à print : historique des états des différentes cases, nombre de passages par case, ce qui permettra d'extraire un peu tout ce qu'on veut

        metrics = { 'measuredTiles' : measuredTiles,
                    'surface'       : surface,
                    'pathLength'    : pathLength,
                    'history'       : history,
                    'visitsPerTile' : visitsPerTile,
                    'simulationDuration' : simulationDuration }

        print('\r\n')

        return metrics # ici on renvoie tout, affichable ou pas


    # Initial move of the refPointBots
    def initMove(self):
        refPointBotsStatus = self.checkMovingRefPointBots()
        if not refPointBotsStatus[0]:
            self.updateUWBcoverArea = self.room.updateUWBcoverArea()
            #self.defineConvexHulls()
            if self.instantMovingRefPointBot:
                print((np.cos(self.theta*self.initCount), np.sin(self.theta*self.initCount)))
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
        print(key)
        for wall in self.walls:
            inter = lineSegmentInter([vectorDir, [bot.x , bot.y]], wall)
            if inter != None:
                vectorCol = np.array([inter[0] - bot.x, inter[1] - bot.y])
                if np.dot(vectorDir, vectorCol)>=0:
                    print("inter")
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
        tMove = time.time()
        # print("########### duration of step : ", tMove - self.time)
        self.time = tMove
        t = time.time()
        self.grid.update(self.surfaceUWB,self.status)
        # print("duration of grid.update : ", time.time() - t)
        

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
                    target = self.findClosestCell()

                    if target is not None: 
                        self.mainPathIndex = 0
                        source = self.lastObj
                        # temporary solution!
                        self.grid.updateNeighOneNode(target)
                        # t = time.time()
                        weight, self.mainPath = (self.djikstra(source, target))
                        # print("duration of djikstra : ", time.time() - t)
                        if self.mainPath is None:
                            self.hasObj = False
                            # self.moveRefPointBotsStep()
                            self.status = "moveRefPointBot1stStep"
                        else:
                            self.addWeigthToPath()
                    else : 
                        self.hasObj = False

                        # self.moveRefPointBotsStep()
                        self.status = "moveRefPointBot1stStep"

                elif step == "changedObj":
                    
                    target = self.findClosestCell()

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

                # print("duration of movingMeasuringBot : ", time.time() - tTot)

        if self.status == "FirsttransferRefPointBotToMeasuringBot":

            if not self.checkMovingRefPointBots()[0]:

                #self.updatePolygon()
                #self.defineConvexHulls()
                self.updateUWBcoverArea = self.room.updateUWBcoverArea()
                
                self.grid.graph[self.grid.origin] = 1

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
                    # self.moveRefPointBotsStep()
                    self.status = "moveRefPointBot1stStep"

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
                    if self.mainPath is None:
                        self.hasObj = False
                        # self.moveRefPointBotsStep()
                        self.status = "moveRefPointBot1stStep"
                    else:
                        self.addWeigthToPath()
                        self.hasObj = True
                        self.status = "movingMeasuringBot"
                        self.initCount+=1
                else:
                    self.hasObj = False
                    # self.moveRefPointBotsStep()
                    self.status = "moveRefPointBot1stStep"
                    self.initCount = len(self.refPointBots) + 2   

        if self.status == "moveRefPointBot1stStep" or self.status == "moveRefPointBot2ndStep" or self.status == "moveRefPointBot3rdStep":
            self.moveRefPointBotsStep()

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

    def findClosestVisitedCellSmart(self, point):
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
            
            if self.status == "moveRefPointBot1stStep":
                key = self.findLeastUsefulBots()
                for bot in self.refPointBots:
                    self.refPointBots[bot].color = (0, 0, 255)
                self.refPointBots[key].color = (150, 0, 255)
                #self.defineConvexHulls()
                self.explorableClusters = []
                self.explorableClustersDict = {}
                self.nearestPoints = []
                self.nextRefStepGoals = {}
                self.nextRefStepGoal = None
                # self.nextRefStepIndex = 0
                self.detectExplorablePart()
                self.defineGravityCenterExplorableClusters()
                nextGoal = None
                for goal in self.nextRefStepGoals:
                    nextGoal = goal
                    break
                if nextGoal!=None:
                    targetCell = self.findClosestVisitedCellSmart(nextGoal)
                    sourceCell = self.findClosestVisitedCell((self.refPointBots[key].x, self.refPointBots[key].y))
                    minBot = key
                    self.nextRefStepGoal = [minBot, nextGoal]
                    weight, self.mainPath = (self.djikstra(sourceCell, targetCell))
                    self.mainPathIndex = 0
                    self.addWeigthToPath()
                    self.hasObj = True
                    self.status = "movingRefPointBot"
            elif self.status == "moveRefPointBot2ndStep":
                # print("called")
                self.refPointBots[self.nextRefStepGoal[0]].defineObjective(self.nextRefStepGoals[self.nextRefStepGoal[1]])
                self.mainPathIndex = 0
                self.status = "moveRefPointBot3rdStep"
            elif self.status == "moveRefPointBot3rdStep":
                # print("called4")
                if not self.checkMovingRefPointBots()[0]:
                    # print("called5")
                    self.status = "transferRefPointBotToMeasuringBot"
                    self.updateUWBcoverArea = self.room.updateUWBcoverArea()
    

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

        # Fin de simulation si les robots UWB n'ont nulle part où aller
        if self.explorableClusters == []:
            self.end_simulation = True            
        
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
            if p1[0]!=p2[0]:
                a = (p1[1]-p2[1])/(p1[0]-p2[0])
                b = p1[1]-a*p1[0]
                pygame.draw.line(self.surfaceReferenceBot, (200, 0, 200, 200),(0,int(b)), (1600,int(a*1600+b)) , 1)
        # print(self.grid.adjacencyList)

