from utilities import *


class RoomExplorator():
    def __init__(self, room, swarmController):
        self.room = room
        self.SC = swarmController
        self.graph = {}
        self.minimumSpanningTree = {}


    def graphConstruction(self):
        ExtremePoints= [[-1, -1], [-1, -1]]
        distMaxX = -1
        distMaxY =  -1
        for i in range(len(self.room.walls)):
            for j in range (i+1, len(self.room.walls)):
                distMax = distMaxXY2Segments(self.room.walls[i], self.room.walls[j])
                if distMax[0] > distMaxX:
                    distMaxX = distMax[0]
                    ExtremePoints[0] = distMax[2][0]
                if distMax[1] > distMaxY:
                    distMaxY = distMax[1]
                    ExtremePoints[1] = distMax[2][1]

        distMax = distMaxXY2Segments(distMaxX, distMaxY)
        nbLines = distMax[1]//self.SC.distRefPointBots[1]
        nbCols = distMax[0]//self.SC.distRefPointBots[0]
        self.initNode = self.SC.measurerBot

    def minimumSpanningTreeComputation(self):
        pass

    def dfsComputation(self):
        pass


