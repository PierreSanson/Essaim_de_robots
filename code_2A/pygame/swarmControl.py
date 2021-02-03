from utilities import *


class SwarmControl():
    def __init__(self, measuringBot, refPointBots, distRefPointBots = [110, 110]) :
        self.distRefPointBots = [110, 110]
        self.measuringBot = measuringBot
        self.refPointBots = {}
        self.nbRefPointBots = len(refPointBots)
        initObjectives = []
        for i in range(self.nbRefPointBots):
            initObjectives.append((self.measuringBot.x + distRefPointBots[0]/2 + ((i-2)//2)*distRefPointBots[0], self.measuringBot.y - distRefPointBots[1]/2 + (i%2)*distRefPointBots[1]))
        
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
            print('objective defined!')
            self.refPointBots[i].defineObjective(initObjectives[i])