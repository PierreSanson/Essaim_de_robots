from bot import Bot
from obstacle import Obstacle
from utilities import *

class RefPointBot(Bot):

    def __init__(self, x, y, radius, room, objective, randomObjective = False, randomInterval = 10, color = (0,0,255), haveObjective = True, radiusDetection = 200, showDetails = False, message = "ExplorerBot",):
        super(self.__class__, self).__init__(x, y, radius, room, objective, randomObjective = randomObjective, randomInterval = randomInterval, color = color, haveObjective = haveObjective, radiusDetection = radiusDetection, showDetails = showDetails)
        self.message = message
        self.wallDetectionRadius = 30

    def show_self(self):
        print(self.message)

    def sendIndDirection(self, direction):
        pass

    def wallDetectionAction(self):
        self.vel2D = np.asarray([0,0])
        self.haveObjective = False

    def checkCollision(self): ############################################################
        # pour les robots
        collision_bot = {}
        collision_wall = False
        for obj in self.room.objects:
            if obj != self :
                distO = distObj(self, obj)
                if distO <= self.radiusDetection:

                    if distO < self.radius + obj.radius :
                        print("COLLISION")
                    if isinstance(obj, Obstacle) and obj.isWall:
                        if distO <= self.wallDetectionRadius:
                            # if  np.linalg.norm(self.vel2D) !=0:
                            #     sols = circleLineInter(self, obj, self.vel2D)
                            # else:
                            sols = circleLineInter(self, obj, [self.objective[0]-self.x, self.objective[1]-self.y])
                            if len(sols)>0:
                                collision_wall = True
                                self.wallDetectionAction()
                                return collision_bot, collision_wall
                    else:
                        if (obj not in self.detectedObj):
                            self.detectedObj.append(obj)
                        if distO <= 50 + obj.radius*1.5 + self.radius:
                            sols = circleLineInter(self, obj, self.vel2D)
                            if len(sols)>0:
                                if len(sols)>1:
                                    minDist = distObjDict(self, sols[0])
                                    minIndex = 0
                                    for i in range(1, len(sols[1:])):
                                        dist = distObjDict(self, sols[i])
                                        if dist < minDist:
                                            minDist = dist
                                            minIndex = i
                                    
                                    collision_bot[obj] = sols[minIndex]
                                else:
                                    collision_bot[obj] = sols[0]
        
        for obj in self.detectedObj:
            if distObj(obj, self) > self.maxDistConsider:
                self.detectedObj.remove(obj)

        # pour les murs
        collision_wall = {}
        # for wall in self.room.walls:
        #     if wall != self :
        #         wall.distBotWall(self)
        #         if wall.dist_coll <= 50:

        #             if wall.dist_coll < self.radius:
        #                 print("COLLISION")

        #             if (wall not in self.detectedWall):
        #                 self.detectedWall.append(wall)

        #             collision_wall[wall] = wall

        return collision_bot, collision_wall