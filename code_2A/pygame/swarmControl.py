from utilities import *
from copy import deepcopy

class SwarmController():
    def __init__(self, win, measurerBot, refPointBots, distRefPointBots = [110, 110]) :
        self.distRefPointBots = distRefPointBots
        self.measurerBot = measurerBot
        self.refPointBots = {}
        self.nbRefPointBots = len(refPointBots)
        self.orientation = 'h'
        self.status = 0
        self.nextMoves = [['straight', 7], ['turnRight', 1],  ['turnRight', 1], ['straight', 8], ['turnLeft', 1], ['turnLeft', 1], ['straight',8]]
        # self.nextMoves = [['straight', 4], ['turnRight', 2]]
        self.actualSequenceLength = 0
        self.actualSequenceCount = 0
        self.actualOneStepCount = 0
        self.actualDeplacement = None
        self.maxOneStepCount = (self.nbRefPointBots//2 - 2)
        self.orientation = 'right'
        self.lastMesurerPos = (self.measurerBot.x, self.measurerBot.y)
        self.initMeasurerPos = (self.measurerBot.x, self.measurerBot.y)
        self.win = win


        initObjectives = []
        for i in range(self.nbRefPointBots):
            initObjectives.append((self.measurerBot.x + distRefPointBots[0]/2 + ((i-2)//2)*distRefPointBots[0], self.measurerBot.y - distRefPointBots[1]/2 + (i%2)*distRefPointBots[1]))
        
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
    

    def moveOneStepRefPointBots(self):
        self.refPointBots[0].color = (0,255,255)
        self.refPointBots[1].color = (0,255,255)
        for i in range(2):
            
            if self.orientation == 'right':
                self.refPointBots[i].defineObjective((self.measurerBot.x + self.distRefPointBots[0]/2 + (self.actualOneStepCount + 1)*self.distRefPointBots[0], 
                    self.measurerBot.y - self.distRefPointBots[1]/2 + (i%2)*self.distRefPointBots[1]))
            
            if self.orientation == 'down':
                self.refPointBots[i].defineObjective((self.measurerBot.x - self.distRefPointBots[0]/2 + ((1-i)%2)*self.distRefPointBots[0], 
                    self.measurerBot.y + self.distRefPointBots[1]/2 + (self.actualOneStepCount + 1)*self.distRefPointBots[1]))

            if self.orientation == 'left':
                self.refPointBots[i].defineObjective((self.measurerBot.x - self.distRefPointBots[0]/2 - (self.actualOneStepCount + 1)*self.distRefPointBots[0], 
                    self.measurerBot.y - self.distRefPointBots[1]/2 + ((1-i)%2)*self.distRefPointBots[1]))

            if self.orientation == 'up':
                self.refPointBots[i].defineObjective((self.measurerBot.x + self.distRefPointBots[0]/2 - ((1-i)%2)*self.distRefPointBots[0], 
                    self.measurerBot.y - self.distRefPointBots[1]/2 - (self.actualOneStepCount + 1)*self.distRefPointBots[1]))

        robotsTemp = [self.refPointBots[0],self.refPointBots[1]]
        for i in range(self.nbRefPointBots-2):
            self.refPointBots[i] = self.refPointBots[i+2]
        self.refPointBots[self.nbRefPointBots-1] = robotsTemp[1]
        self.refPointBots[self.nbRefPointBots-2] = robotsTemp[0]

    def moveOneStepRefPointBots2(self, shift):
        for i in range(self.nbRefPointBots - 4 - shift):
            self.refPointBots[i].defineObjective((self.measurerBot.x + (i//2 +1/2)*self.distRefPointBots[0] + self.distRefPointBots[0], 
            self.measurerBot.y - self.distRefPointBots[1]/2 + (i%2)*self.distRefPointBots[1]))

        robotsTemp = [self.refPointBots[i] for i in range(self.nbRefPointBots - 4 - shift)]
        print(shift)
        for i in range(4 + shift):
            self.refPointBots[i] = self.refPointBots[i+self.nbRefPointBots-shift-4]
        for i in range(self.nbRefPointBots - 4 - shift):
            self.refPointBots[self.nbRefPointBots-i] = robotsTemp[-i-1]


    def moveOneStepMeasurerBot(self, lenMove):
        if self.orientation == 'right':
            self.measurerBot.defineObjective((self.measurerBot.x + (lenMove-2)*(self.distRefPointBots[0]), self.measurerBot.y))
        if self.orientation == 'down':
            self.measurerBot.defineObjective((self.measurerBot.x , self.measurerBot.y + (lenMove-2)*(self.distRefPointBots[1])))
        if self.orientation == 'left':
            self.measurerBot.defineObjective((self.measurerBot.x - (lenMove-2)*(self.distRefPointBots[0]), self.measurerBot.y))
        if self.orientation == 'up':
            self.measurerBot.defineObjective((self.measurerBot.x , self.measurerBot.y - (lenMove-2)*(self.distRefPointBots[1])))

    def checkMovingRefPointBots(self):
        for key in self.refPointBots:
            if self.refPointBots[key].haveObjective:
                return True
        return False

    def checkMovingMeasurerBot(self):
        if self.measurerBot.haveObjective:
            return True
        return False

    def moveOneStraight(self):
        
        if self.actualSequenceCount <= self.actualSequenceLength and self.actualOneStepCount == self.maxOneStepCount  and  not self.checkMovingRefPointBots():
            self.refPointBots[self.nbRefPointBots-1].color = (0,0,255)
            self.refPointBots[self.nbRefPointBots-2].color = (0,0,255)
            if self.actualSequenceCount == self.actualSequenceLength:
                print(self.actualSequenceLength%(self.nbRefPointBots//2 -2))
                if self.actualSequenceLength%(self.nbRefPointBots//2 -2) == 0:
                    self.moveOneStepMeasurerBot(self.nbRefPointBots//2)
                else :
                    self.moveOneStepMeasurerBot(self.actualSequenceLength%(self.nbRefPointBots//2 -2) +2)
                return False
            if self.actualSequenceLength - self.actualSequenceCount <= self.nbRefPointBots//2 - 2:

                self.moveOneStepMeasurerBot(self.nbRefPointBots//2)
                self.maxOneStepCount = self.actualSequenceLength - self.actualSequenceCount
                self.actualOneStepCount = 0
            else:
                self.moveOneStepMeasurerBot(self.nbRefPointBots//2)
                self.actualOneStepCount = (self.nbRefPointBots//2) - 2
                self.actualOneStepCount = 0

        elif self.actualOneStepCount == 0 and not self.checkMovingMeasurerBot():
            self.moveOneStepRefPointBots()
            self.actualOneStepCount += 1
            self.actualSequenceCount += 1

        elif self.actualOneStepCount > 0 and self.actualOneStepCount < self.maxOneStepCount and not self.checkMovingRefPointBots() and not self.checkMovingMeasurerBot():
            self.refPointBots[self.nbRefPointBots-1].color = (0,0,255)
            self.refPointBots[self.nbRefPointBots-2].color = (0,0,255)
            self.moveOneStepRefPointBots()
            self.actualOneStepCount += 1
            self.actualSequenceCount += 1
        return True

    def moveOneStraight2(self):
        
        if self.actualSequenceCount <= self.actualSequenceLength and self.actualOneStepCount == 1 and  not self.checkMovingRefPointBots():
            if self.actualSequenceCount == self.actualSequenceLength:
                self.moveOneStepMeasurerBot(self.actualSequenceLength%(self.nbRefPointBots//2))
                return False
            if self.actualSequenceLength - self.actualSequenceCount <= self.nbRefPointBots//2:

                self.moveOneStepMeasurerBot(self.nbRefPointBots//2)
                self.actualOneStepCount = 0
            else:
                self.moveOneStepMeasurerBot(self.nbRefPointBots//2)
                self.actualOneStepCount = 0

        elif self.actualOneStepCount == 0 and not self.checkMovingMeasurerBot():
            if self.actualSequenceLength - self.actualSequenceCount <= self.nbRefPointBots -4:
                self.moveOneStepRefPointBots2(self.nbRefPointBots -4 -self.actualSequenceLength + self.actualSequenceCount)
                self.actualOneStepCount += 1
                self.actualSequenceCount = self.actualSequenceLength
            else:
                self.moveOneStepRefPointBots2(0)
                self.actualOneStepCount += 1
                self.actualSequenceCount += self.nbRefPointBots -4
        return True

    def turnRight(self):

        for i in range(self.nbRefPointBots):
            print('avant : ' + str(i) + " : " + str(self.refPointBots[i].x) + "," + str(self.refPointBots[i].y))

        robotTemp = {key: value for key, value in self.refPointBots.items()}            
        self.refPointBots[self.nbRefPointBots- 2] =  robotTemp[self.nbRefPointBots- 1]
        self.refPointBots[self.nbRefPointBots- 4] =  robotTemp[self.nbRefPointBots- 2]
        self.refPointBots[self.nbRefPointBots- 1] =  robotTemp[self.nbRefPointBots- 3]
        self.refPointBots[self.nbRefPointBots- 3] =  robotTemp[self.nbRefPointBots- 4] 
        if self.orientation == 'right':
            self.orientation = 'down'
        
        elif self.orientation == 'down':
            self.orientation = 'left'

        elif self.orientation == 'left':
            self.orientation = 'up'

        elif self.orientation == 'up':
            self.orientation = 'right'
        
        for i in range(self.nbRefPointBots):
            print('après : ' +  str(i) + " : " + str(self.refPointBots[i].x) + "," + str(self.refPointBots[i].y))

        self.maxOneStepCount = self.actualSequenceLength
        if self.actualSequenceLength == 0 or self.actualSequenceLength >= self.nbRefPointBots//2 - 2:
            self.actualSequenceLength = self.nbRefPointBots//2 - 2
            self.maxOneStepCount = self.nbRefPointBots//2 - 2
        
        self.actualDeplacement = self.moveOneStraight 

    def turnLeft(self):

        robotTemp = {key: value for key, value in self.refPointBots.items()}            
        self.refPointBots[self.nbRefPointBots- 2] =  robotTemp[self.nbRefPointBots- 4]
        self.refPointBots[self.nbRefPointBots- 4] =  robotTemp[self.nbRefPointBots- 3] 
        self.refPointBots[self.nbRefPointBots- 1] =  robotTemp[self.nbRefPointBots- 2] 
        self.refPointBots[self.nbRefPointBots- 3] =  robotTemp[self.nbRefPointBots- 1] 
        
        if self.orientation == 'right':
            self.orientation = 'up'

        
        elif self.orientation == 'down':
            self.orientation = 'right'


        elif self.orientation == 'left':
            self.orientation = 'down'


        elif self.orientation == 'up':
            self.orientation = 'left'
        

        self.maxOneStepCount = self.actualSequenceLength
        if self.actualSequenceLength == 0 or self.actualSequenceLength >= self.nbRefPointBots//2 - 2:
            self.actualSequenceLength = self.nbRefPointBots//2 - 2
            self.maxOneStepCount = self.nbRefPointBots//2 - 2
        
        self.actualDeplacement = self.moveOneStraight 
    
    def move(self):
        if self.actualDeplacement():
            pass
        else :
            self.lastMesurerPos = (self.measurerBot.x, self.measurerBot.y)
            previousOrientation = self.orientation
            if len(self.nextMoves) > 0:
                self.nextMoves.pop(0) 
            
            if len(self.nextMoves) > 0:
                
                self.actualSequenceCount = 0
                self.actualOneStepCount = 0
                self.actualSequenceLength = self.nextMoves[0][1]
                if self.nextMoves[0][0] == 'straight':
                    if self.actualSequenceLength < self.nbRefPointBots//2 - 2:
                        self.maxOneStepCount = self.actualSequenceLength
                    else:
                        self.maxOneStepCount = self.nbRefPointBots//2 - 2
                    self.actualDeplacement = self.moveOneStraight
                elif self.nextMoves[0][0] == 'turnRight':
                    self.turnRight()
                elif self.nextMoves[0][0] == 'turnLeft':
                    self.turnLeft()
            else:
                self.actualDeplacement = self.void

    def initMove(self):
        self.actualSequenceCount = 0
        self.actualOneStepCount = (self.nbRefPointBots//2 - 2)
        self.actualSequenceLength = self.nextMoves[0][1]
        if self.nextMoves[0][0] == 'straight':
            self.actualDeplacement = self.moveOneStraight

    def void(self):
        pass

    def draw(self):
        previousOrientations = [self.orientation]
        previousPositions = [self.lastMesurerPos]
        for i in range (len(self.nextMoves)):
            nextPos = None
            previousOrientation = None
            if self.nextMoves[i][0] == 'straight':
                if previousOrientations[i] == 'right':
                    nextPos = (previousPositions[i][0] + self.nextMoves[i][1]*self.distRefPointBots[0], previousPositions[i][1])
                    pygame.draw.circle(self.win, (0,255,0, 255/(i+1)), (nextPos[0], nextPos[1]) , self.measurerBot.radius)
                elif previousOrientations[i] == 'left':
                    nextPos = (previousPositions[i][0] - self.nextMoves[i][1]*self.distRefPointBots[0], previousPositions[i][1])
                    pygame.draw.circle(self.win, (0,255,0, 255/(i+1)), (nextPos[0], nextPos[1]) , self.measurerBot.radius)
                elif previousOrientations[i] == 'up':
                    nextPos = (previousPositions[i][0] , previousPositions[i][1] - self.nextMoves[i][1]*self.distRefPointBots[1])
                    pygame.draw.circle(self.win, (0,255,0, 255/(i+1)), (nextPos[0], nextPos[1]) , self.measurerBot.radius)
                elif previousOrientations[i] == 'down':
                    nextPos = (previousPositions[i][0], previousPositions[i][1] + self.nextMoves[i][1]*self.distRefPointBots[1])
                    pygame.draw.circle(self.win, (0,255,0, 255/(i+1)), (nextPos[0], nextPos[1]) , self.measurerBot.radius)
                previousOrientation = previousOrientations[i]

            elif self.nextMoves[i][0] == 'turnRight':
                if previousOrientations[i] == 'right':
                    nextPos = (previousPositions[i][0], previousPositions[i][1] + self.nextMoves[i][1]*self.distRefPointBots[1])
                    pygame.draw.circle(self.win, (0,255,0, 255/(i+1)), (nextPos[0], nextPos[1]) , self.measurerBot.radius)
                    previousOrientation = 'down'
                elif previousOrientations[i] == 'left':
                    nextPos = (previousPositions[i][0] , previousPositions[i][1] - self.nextMoves[i][1]*self.distRefPointBots[1])
                    pygame.draw.circle(self.win, (0,255,0, 255/(i+1)), (nextPos[0], nextPos[1]) , self.measurerBot.radius)
                    previousOrientation = 'up'
                elif previousOrientations[i] == 'up':
                    nextPos = (previousPositions[i][0] + self.nextMoves[i][1]*self.distRefPointBots[0], previousPositions[i][1])
                    pygame.draw.circle(self.win, (0,255,0, 255/(i+1)), (nextPos[0], nextPos[1]) , self.measurerBot.radius)
                    previousOrientation = 'right'
                elif previousOrientations[i] == 'down':
                    nextPos = (previousPositions[i][0] - self.nextMoves[i][1]*self.distRefPointBots[0], previousPositions[i][1])
                    pygame.draw.circle(self.win, (0,255,0, 255/(i+1)), (nextPos[0], nextPos[1]) , self.measurerBot.radius)
                    previousOrientation = 'left'

            elif self.nextMoves[i][0] == 'turnLeft':
                if previousOrientations[i] == 'right':
                    nextPos = (previousPositions[i][0] , previousPositions[i][1] - self.nextMoves[i][1]*self.distRefPointBots[1])
                    pygame.draw.circle(self.win, (0,255,0, 255/(i+1)), (nextPos[0], nextPos[1]) , self.measurerBot.radius)
                    previousOrientation  ='up'
                elif previousOrientations[i] == 'left':
                    nextPos = (previousPositions[i][0], previousPositions[i][1] + self.nextMoves[i][1]*self.distRefPointBots[1])
                    pygame.draw.circle(self.win, (0,255,0, 255/(i+1)), (nextPos[0], nextPos[1]) , self.measurerBot.radius)
                    previousOrientation = 'down'
                elif previousOrientations[i] == 'up':
                    nextPos = (previousPositions[i][0] - self.nextMoves[i][1]*self.distRefPointBots[0], previousPositions[i][1])
                    pygame.draw.circle(self.win, (0,255,0, 255/(i+1)), (nextPos[0], nextPos[1]) , self.measurerBot.radius)
                    previousOrientation = 'left'
                elif previousOrientations[i] == 'down':
                    nextPos = (previousPositions[i][0] + self.nextMoves[i][1]*self.distRefPointBots[0], previousPositions[i][1])
                    pygame.draw.circle(self.win, (0,255,0, 255/(i+1)), (nextPos[0], nextPos[1]) , self.measurerBot.radius)
                    previousOrientation = 'right'
            previousOrientations.append(previousOrientation)
            previousPositions.append(nextPos)
                    
                    

