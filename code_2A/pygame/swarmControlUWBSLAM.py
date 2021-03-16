from utilities import *
from copy import deepcopy
import numpy as np

class SwarmControllerUWBSLAM():
    def __init__(self, surface, measurerBot, refPointBots, distRefPointBots = [110, 110], initRadius=50) :
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

        theta = 2*np.pi/(len(self.nbRefPointBots))

        initObjectives = []
        for i in range(self.nbRefPointBots):
            initObjectives.append((self.measurerBot.x + initRadius*np.cos(theta), self.measurerBot.y +initRadius*np.sin(theta)))
        
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
    

