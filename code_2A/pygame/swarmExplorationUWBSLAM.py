from token import SEMI
from utilities import *
from copy import deepcopy
import numpy as np
from scipy.spatial import ConvexHull
from itertools import chain
import colorsys


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
        self.lastMesurerPos = (self.measurerBot.x, self.measurerBot.y)
        self.initMeasurerPos = (self.measurerBot.x, self.measurerBot.y)
        self.surface = surface
        self.initCount = 0
        self.theta = 2*np.pi/self.nbRefPointBots
        self.refPointBotsVisibleBots = {}

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

        HSV_tuples = [(x*1.0/self.nbRefPointBots, 0.5, 0.5) for x in range(self.nbRefPointBots)]
        self.RGB_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))

        self.walls = []
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
        else :
            if not self.check3RefPointBotsAvailable(refPointBotsStatus[1]):
                self.refPointBots[refPointBotsStatus[1]].wallDetectionAction()


    def checkMovingRefPointBots(self):
        for key in self.refPointBots:
            if self.refPointBots[key].haveObjective:
                return True, key
        return False, None

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
        if self.initCount < self.nbRefPointBots:
            self.initMove()
        key = 4
        self.check3RefPointBotsAvailable(key)


    def draw(self):
        key = 4
        refPointBotsPoints = list(chain.from_iterable([self.refPointBots[keyBot].polygonPoints for keyBot in self.refPointBotsVisibleBots[key]]))
        convexHullObstacles = ConvexHull(refPointBotsPoints)
        self.convexHull = [refPointBotsPoints[i] for i in list(convexHullObstacles.vertices)[:]]
        color = self.RGB_tuples[key]
        pygame.draw.polygon(self.surface, (*color, 64), self.convexHull)

