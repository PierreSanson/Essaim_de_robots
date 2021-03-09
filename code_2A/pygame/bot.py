from numpy.core.fromnumeric import argmin
from utilities import *

import pygame
import numpy as np
import random
from copy import deepcopy
from scipy.spatial import ConvexHull

class Bot():
    def __init__(self, x, y, radius, room, objective, randomObjective = False, randomInterval = 10, color = (0,255,0), haveObjective = True, radiusDetection = 100, showDetails = False):
        self.room = room
        self.x = x
        self.y = y
        self.radius = radius
        self.vel2D = np.asarray([0.0001,0.0001])
        self.lastVel2D = np.asarray([0.0001,0.0001])
        self.objective = objective
        self.radiusDetection = radiusDetection
        self.rotationSpeed = 32
        self.speed = 8
        self.groupObj = []
        self.detectedObj = []
        self.groupObjPoints = []
        self.walls = []
        self.groupWall = []
        self.detectedWall = []
        self.groupWallPoints = []
        self.safeCoeff = 1
        self.ontoObjectiveCoeff = 1
        self.randomObjective = randomObjective
        self.turnAroundCoeff = 1
        self.barycenterGroupObj = {'x' : 0, 'y' : 0}
        self.barycenterGroupWall = {'x' : 0, 'y' : 0}
        self.groupObjRadius = 0
        self.randomInterval = randomInterval
        self.margin=2
        self.polygonPointsAbsolute = createPolygonMask([0, 0], 10, self.radius + self.margin)
        self.polygonPoints = deepcopy(self.polygonPointsAbsolute)
        self.convexHullObstacles = None
        self.groupPolygonPoints = []
        self.mode = "polygon"
        self.color = color
        self.ontoObjective = False
        self.haveObjective = haveObjective
        self.showDetails = showDetails
        self.maxDistConsider = 100
        if not self.haveObjective:
            self.vel2D = np.asarray([0,0])
        for wall in self.room.walls:  
            self.walls.append([[wall.x_start, wall.y_start],[wall.x_start+wall.width, wall.y_start]])
            self.walls.append([[wall.x_start, wall.y_start],[wall.x_start, wall.y_start + wall.height]])
            self.walls.append([[wall.x_start + wall.width, wall.y_start],[wall.x_start + wall.width, wall.y_start + wall.height]])
            self.walls.append([[wall.x_start, wall.y_start+wall.height],[wall.x_start+wall.width, wall.y_start + wall.height]])
        self.defineObstaclesFromWalls()
         

    def defineObstaclesFromWalls(self):
        radiusObstacles = 2
        spaceBetweenObstaclesCenter = 15
        obstacles = []
        for wall in self.walls:
            if wall[0][1] == wall[1][1]:
                y = wall[0][1]
                for x in range(wall[0][0] + radiusObstacles, wall[1][0], spaceBetweenObstaclesCenter):
                    obstacles.append(Obstacle(x, y, radiusObstacles, self.room, isWall='x'))

            elif wall[0][0] == wall[1][0]:
                x = wall[0][0]
                for y in range(wall[0][1] + radiusObstacles, wall[1][1], spaceBetweenObstaclesCenter):
                    obstacles.append(Obstacle(x, y, radiusObstacles, self.room, isWall='y'))
        
        self.room.addObjects(obstacles)



    def draw(self, win, surface1):
        if not self.showDetails:
            if self.mode == "circle" :
                pygame.draw.circle(surface1, (255,0,255, 64), (self.barycenterGroupObj['x'], self.barycenterGroupObj['y']), self.groupObjRadius)
                pygame.draw.circle(surface1, (20,20,20, 64), (self.barycenterGroupObj['x'], self.barycenterGroupObj['y']), 4)
                
            pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)
            if np.linalg.norm(self.vel2D) !=0:
                vel2DU = self.vel2D/np.linalg.norm(self.vel2D)
                pygame.draw.line(surface1, (255,255,255), (self.x, self.y), (self.x + vel2DU[0]*self.radius, self.y + vel2DU[1]*self.radius))
        else:
            # Uncomment/comment for more/less details about the process !
            # pygame.draw.circle(surface1, (0,150,255, 128), (self.x, self.y), self.radiusDetection)
            if self.mode == "circle" :
                pygame.draw.circle(surface1, (255,0,255, 64), (self.barycenterGroupObj['x'], self.barycenterGroupObj['y']), self.groupObjRadius)
                pygame.draw.circle(surface1, (20,20,20, 64), (self.barycenterGroupObj['x'], self.barycenterGroupObj['y']), 4)
                
            pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)
            if self.haveObjective:
                pygame.draw.circle(win, (255,255,255), (self.objective[0], self.objective[1]), self.radius)
            if self.mode == "polygon":
                if self.groupPolygonPoints == []:
                    self.convexHullObstacles = None
                if self.convexHullObstacles is not None:
                    pygame.draw.polygon(surface1, (200,50,50, 64), self.groupPolygonPoints)
                    pygame.draw.circle(surface1, (200,200,200, 64), (self.barycenterGroupObj['x'], self.barycenterGroupObj['y']), 4)
            if np.linalg.norm(self.vel2D) !=0:
                vel2DU = self.vel2D/np.linalg.norm(self.vel2D)
                pygame.draw.line(surface1, (255,255,255), (self.x, self.y), (self.x + vel2DU[0]*self.radius, self.y + vel2DU[1]*self.radius))
        
        

    def move(self, win):
        for i in range(len(self.polygonPoints)):
            self.polygonPoints[i][0] = self.polygonPointsAbsolute[i][0] + self.x
            self.polygonPoints[i][1] = self.polygonPointsAbsolute[i][1] + self.y
        if self.randomObjective:
            if random.random() > (1 - 1/(100*self.randomInterval)) :
                self.objective[0] = random.randrange(50, win.get_width() - 50)
                self.objective[1] = random.randrange(50, win.get_height() - 50)
                self.haveObjective = True
                self.ontoObjective = False
                self.vel2D = np.asarray([0.01,0.01])
        if self.haveObjective:
            self.goToObjective(win)
        if np.linalg.norm(self.vel2D) !=0:
            vel2DU = self.vel2D/np.linalg.norm(self.vel2D)
            self.x += vel2DU[0]*self.speed*self.safeCoeff*self.ontoObjectiveCoeff 
            self.y += vel2DU[1]*self.speed*self.safeCoeff*self.ontoObjectiveCoeff 


    def checkCollision(self): ############################################################
        # pour les robots
        collision_bot = {}
        for obj in self.room.objects:
            if obj != self :
                distO = distObj(self, obj)
                if distO <= self.radiusDetection:

                    if distO < self.radius + obj.radius :
                        print("COLLISION")

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


    def checkColObjective(self):
        col = False
        for obj in self.groupObj:
            angleColObj = signedAngle2Vects2(np.array([obj.x- self.objective[0], obj.y - self.objective[1]]), -1*np.array([self.objective[0]- self.x, self.objective[1] - self.y]))

            
            if len(circleLineInter(self, obj, np.array([self.objective[0]- self.x, self.objective[1] - self.y]))) >0 and abs(angleColObj) < np.pi/2:
                col = True
                return col
        return col


    def noColgoToObjective(self, surface1):
        self.safeCoeff = 1
        angleCol = (signedAngle2Vects2(self.vel2D, np.array([self.barycenterGroupObj['x'] - self.x, self.barycenterGroupObj['y'] - self.y])))

        if not self.checkColObjective():
    
            angleObj = signedAngle2Vects2(self.vel2D, np.array([self.objective[0]- self.x, self.objective[1] - self.y]))
            rotationSpeed = min(self.rotationSpeed*np.pi/180, abs(angleObj))
            if angleObj >= 0:
                self.vel2D = rotate(self.vel2D, rotationSpeed)
            elif angleObj < 0:
                self.vel2D = rotate(self.vel2D, - rotationSpeed)

        elif self.mode == "circle":
            if distObjDict(self, self.barycenterGroupObj) < self.groupObjRadius:
                if random.random() > (1 - 1/(10000/self.speed))  :
                    self.turnAroundCoeff *= -1
                self.vel2D = self.vel2D
            
            elif len(circleLineInter(self, self.barycenterGroupObj, self.vel2D, objDict = True, objRadius = self.groupObjRadius)) >0 and abs(angleCol) < np.pi/2:
                if angleCol > 0:
                    self.vel2D = rotate(self.vel2D, - self.rotationSpeed*np.pi/180)
                elif angleCol <= 0:
                    self.vel2D = rotate(self.vel2D, self.rotationSpeed*np.pi/180)
            else :
                angleObj = signedAngle2Vects2(self.vel2D, np.array([self.objective[0]- self.x, self.objective[1] - self.y]))
                rotationSpeed = min(self.rotationSpeed*np.pi/180, abs(angleObj))
                if angleObj >= 0:
                    self.vel2D = rotate(self.vel2D, rotationSpeed)
                elif angleObj < 0:
                    self.vel2D = rotate(self.vel2D, - rotationSpeed)

        elif self.mode == "polygon":
            
            polygonInter = polygonLineInter(self, self.groupPolygonPoints,self.barycenterGroupObj, self.vel2D, surface1)
            if len (polygonInter) == 1:
                if angleCol > 0:
                    self.vel2D = rotate(self.vel2D, - self.rotationSpeed*np.pi/180)
                elif angleCol <= 0:
                    self.vel2D = rotate(self.vel2D, self.rotationSpeed*np.pi/180)
            elif len(polygonInter) == 2 and abs(angleCol) < np.pi/2:
                if angleCol > 0:
                    self.vel2D = rotate(self.vel2D, - self.rotationSpeed*np.pi/180)
                elif angleCol <= 0:
                    self.vel2D = rotate(self.vel2D, self.rotationSpeed*np.pi/180)
            elif len(polygonInter) >= 2 and abs(angleCol) < np.pi/2:
                if angleCol > 0:
                    self.vel2D = rotate(self.vel2D, - self.rotationSpeed*np.pi/180)
                elif angleCol <= 0:
                    self.vel2D = rotate(self.vel2D, self.rotationSpeed*np.pi/180)
            elif pointInPolygon(self, self.groupPolygonPoints):
                if random.random() > (1 - 1/(10000/self.speed))  :
                    self.turnAroundCoeff *= -1
                self.vel2D = self.vel2D
            else :
                angleObj = signedAngle2Vects2(self.vel2D, np.array([self.objective[0]- self.x, self.objective[1] - self.y]))
                rotationSpeed = min(self.rotationSpeed*np.pi/180, abs(angleObj))
                if angleObj >= 0:
                    self.vel2D = rotate(self.vel2D, rotationSpeed)
                elif angleObj < 0:
                    self.vel2D = rotate(self.vel2D, -rotationSpeed)


    def goToObjective(self, surface1):
        distObjective = distObjList(self, self.objective)
        if distObjective < 60*self.speed/self.rotationSpeed + self.radius*2:
            self.ontoObjectiveCoeff = distObjective/((60*self.speed/self.rotationSpeed)**(1.08))
            if distObjective < 0.1:
                self.ontoObjective = True
                self.haveObjective = False
                self.lastVel2D = self.vel2D
                self.vel2D = np.asarray([0,0])
                self.groupObj = []
                self.groupObjPoints = []
                self.groupWall = []
                self.groupWallPoints = []
                self.groupPolygonPoints = []
                self.convexHullObstacles = None
        else :
            self.ontoObjectiveCoeff = 1

        collision_bot, collision_wall = self.checkCollision() 
        
        checkedCollision = []
        checkedCollision_wall = []


        if collision_bot :
            init = True
            minDist = None
            minObj = None
            for obj in collision_bot:
                dist = distObjDict(self, collision_bot[obj])
                angleCol = signedAngle2Vects2(self.vel2D, np.array([obj.x - self.x, obj.y - self.y]))
                if init : 
                    if abs(angleCol) <= np.pi/2:
                        checkedCollision.append(obj)
                        minDist = distObjDict(self, collision_bot[obj])
                        minObj = obj
                        init = False
                else :
                    if abs(angleCol) <= np.pi/2:
                        checkedCollision.append(obj)
                        if dist < minDist :
                            minDist = dist
                            minObj = obj

            if minObj is not None:
                if minObj not in self.groupObj :
                    self.groupObj.append(minObj)
                    self.groupObjPoints+=minObj.polygonPoints[:]

                dist = distObj(self, minObj)
                if  dist - minObj.radius - self.radius < self.speed*40/(np.sqrt(self.rotationSpeed)):
                    self.safeCoeff = max((dist - minObj.radius - self.radius)/(self.speed*40/(np.sqrt(self.rotationSpeed))), 0.01)
            else:
                self.safeCoeff = 1

            

            for obj in checkedCollision:
                if obj not in self.detectedObj:
                    self.detectedObj.append(obj)
            
            if minObj is not None:
                checkedgroupObj = [minObj]
                checkedgroupObjPoints = minObj.polygonPoints[:]
                i=0
                while i<len(checkedgroupObj):
                    for obj in self.groupObj:
                        if obj not in checkedgroupObj:
                            if distObj(obj, checkedgroupObj[i]) < obj.radius + checkedgroupObj[i].radius + 2*self.radius + 2*self.margin:
                                if distObj(obj, self) < self.maxDistConsider :
                                    if minObj is not None and isinstance(minObj, Obstacle) and isinstance(obj, Obstacle) and (minObj.isWall or obj.isWall):
                                        if obj.isWall == minObj.isWall or distObj(obj, self) < 30:
                                            checkedgroupObj.append(obj)
                                            checkedgroupObjPoints+=obj.polygonPoints[:]
                                    else:
                                        checkedgroupObj.append(obj)
                                        checkedgroupObjPoints+=obj.polygonPoints[:]
                    i+=1
                self.groupObj = checkedgroupObj
                self.groupObjPoints = checkedgroupObjPoints

            elif len(self.groupObj) > 0 :
                distList = [distObj(obj, self) for obj in self.groupObj]
                minObj = self.groupObj[argmin(distList)]
                checkedgroupObj = [self.groupObj[argmin(distList)]]
                checkedgroupObjPoints = checkedgroupObj[0].polygonPoints[:]
                i=0
                while i<len(checkedgroupObj):
                    for obj in self.groupObj:
                        if obj not in checkedgroupObj:
                            if distObj(obj, checkedgroupObj[i]) < obj.radius + checkedgroupObj[i].radius + 2*self.radius + 2*self.margin:
                                if distObj(obj, self) < self.maxDistConsider :
                                    if minObj is not None and isinstance(minObj, Obstacle) and isinstance(obj, Obstacle) and (minObj.isWall or obj.isWall):
                                        if obj.isWall == minObj.isWall or distObj(obj, self) < 30:
                                            checkedgroupObj.append(obj)
                                            checkedgroupObjPoints+=obj.polygonPoints[:]
                                    else:
                                        checkedgroupObj.append(obj)
                                        checkedgroupObjPoints+=obj.polygonPoints[:]
                    i+=1
                self.groupObj = checkedgroupObj
                self.groupObjPoints = checkedgroupObjPoints
                # self.convexHullObstacles = ConvexHull(self.groupObjPoints)
                # if self.convexHullObstacles is not None:
                #     self.groupPolygonPoints = [self.groupObjPoints[i] for i in list(self.convexHullObstacles.vertices)[:]]
            else :
                self.groupObj = []
                self.groupObjPoints = []
                self.groupPolygonPoints = []
                self.convexHullObstacles = None
            

            i=0
            if minObj is not None and isinstance(minObj, Obstacle) and minObj.isWall:
                while i<len(self.groupObj):
                    for obj in self.detectedObj : 
                        if obj not in self.groupObj :
                            if distObj(obj, self.groupObj[i]) < obj.radius + self.groupObj[i].radius + 2*self.radius + 2*self.margin:
                                if isinstance(obj, Obstacle) and obj.isWall == minObj.isWall or distObj(obj, self) < 10:
                                    self.groupObj.append(obj)
                                    self.groupObjPoints+=obj.polygonPoints[:]
                    i+=1
            # else:
            #     while i<len(self.groupObj):
            #         for obj in self.detectedObj : 
            #             if obj not in self.groupObj :
            #                 if distObj(obj, self.groupObj[i]) < obj.radius + self.groupObj[i].radius + 2*self.radius + 2*self.margin:
            #                     self.groupObj.append(obj)
            #                     self.groupObjPoints+=obj.polygonPoints[:]
            #         i+=1
            
            
            
            

            if (len(self.groupObj)) > 0:
                self.barycenterGroupObj = { 'x' : (1/len(self.groupObj))*np.sum(np.array([obj.x for obj in self.groupObj])), 'y' : (1/len(self.groupObj))*np.sum(np.array([obj.y for obj in self.groupObj]))}

                self.convexHullObstacles = ConvexHull(self.groupObjPoints)
                if self.convexHullObstacles is not None:
                    self.groupPolygonPoints = [self.groupObjPoints[i] for i in list(self.convexHullObstacles.vertices)[:]]
                
                
                angleCol = (signedAngle2Vects2(self.vel2D, np.array([self.barycenterGroupObj['x'] - self.x, self.barycenterGroupObj['y'] - self.y])))
                polygonInter = polygonLineInter(self, self.groupPolygonPoints,self.barycenterGroupObj, self.vel2D, surface1)
                if len (polygonInter) == 1:
                    if angleCol > 0:
                        self.vel2D = rotate(self.vel2D, - self.rotationSpeed*np.pi/180)
                    elif angleCol <= 0:
                        self.vel2D = rotate(self.vel2D, self.rotationSpeed*np.pi/180)
                elif not self.checkColObjective():
                    
                    angleObj = signedAngle2Vects2(self.vel2D, np.array([self.objective[0]- self.x, self.objective[1] - self.y]))
                    rotationSpeed = min(self.rotationSpeed*np.pi/180, abs(angleObj))
                    if angleObj >= 0:
                        self.vel2D = rotate(self.vel2D, rotationSpeed)
                    elif angleObj < 0:
                        self.vel2D = rotate(self.vel2D, - rotationSpeed)
                elif pointInPolygon(self, self.groupPolygonPoints):
                    if angleCol > 0:
                        self.vel2D = rotate(self.vel2D, self.turnAroundCoeff*self.rotationSpeed*np.pi/180)
                    elif angleCol <= 0:
                        self.vel2D = rotate(self.vel2D, self.turnAroundCoeff*self.rotationSpeed*np.pi/180)
                elif abs(angleCol) <= np.pi/2 :
                    if angleCol > 0:
                        self.vel2D = rotate(self.vel2D, - self.rotationSpeed*np.pi/180)
                    elif angleCol <= 0:
                        self.vel2D = rotate(self.vel2D, self.rotationSpeed*np.pi/180)
                else:
                    self.noColgoToObjective(surface1)
            else:
                self.noColgoToObjective(surface1)
        

        elif collision_wall : # évitement des murs

            init = True
            minDist = None
            minWall = None
            for wall in collision_wall:
                wall.distBotWall(self)
                angleCol = signedAngle2Vects2(self.vel2D, np.array([wall.x - self.x, wall.y - self.y]))
                if init : 
                    if abs(angleCol) <= np.pi/2:
                        checkedCollision.append(wall)
                        minDist = wall.dist_coll
                        minWall = wall
                        init = False
                else :
                    if abs(angleCol) <= np.pi/2:
                        checkedCollision_wall.append(wall)
                        if wall.dist_coll < minDist :
                            minDist = wall.dist_coll
                            minWall = wall

            if minWall is not None:
                if minWall not in self.groupWall :
                    # self.groupWall.append(minWall)
                    self.groupWall = [minWall]
                    # self.groupWallPoints+=minWall.borderPoints[:]
                    self.groupWallPoints=minWall.borderPoints[:]

                minWall.distBotWall(self)
                if  minWall.dist_coll - self.radius < self.speed*150/(np.sqrt(self.rotationSpeed)):
                    # self.safeCoeff = max((minWall.dist_coll - self.radius)/(self.speed*150/(np.sqrt(self.rotationSpeed))), 0.01)
                    self.safeCoeff = self.safeCoeff
            else:
                self.safeCoeff = 1

            
            for wall in checkedCollision_wall:
                if wall not in self.detectedWall:
                    self.detectedWall.append(wall)
            
            if minWall is not None:
                checkedgroupWall = [minWall]
                checkedgroupWallPoints = minWall.borderPoints[:]
                # i=0
                # while i<len(checkedgroupWall):
                #     for wall in self.groupWall:
                #         if wall not in checkedgroupWall:
                #             if distObj(wall, checkedgroupWall[i]) < 2*self.radius + 2*self.margin:
                #                 checkedgroupWall.append(wall)
                #                 checkedgroupWallPoints+=wall.borderPoints[:]
                #     i+=1
                self.groupWall = checkedgroupWall
                self.groupWallPoints = checkedgroupWallPoints

            elif len(self.groupWall) > 0 :
                checkedgroupWall = [self.groupWall[0]]
                checkedgroupWallPoints = self.groupWall[0].borderPoints[:]
                # i=0
                # while i<len(checkedgroupWall):
                #     for wall in self.groupWall:
                #         if wall not in checkedgroupWall:
                #             if distObj(wall, checkedgroupWall[i]) < 2*self.radius + 2*self.margin:
                #                 checkedgroupWall.append(wall)
                #                 checkedgroupWallPoints+=wall.borderPoints[:]
                #     i+=1
                self.groupWall = checkedgroupWall
                self.groupWallPoints = checkedgroupWallPoints

                if len(self.groupObjPoints) > 0 and len(self.groupWallPoints) > 0:
                    self.convexHullObstacles = ConvexHull(self.groupWallPoints + self.groupObjPoints)
                    if self.convexHullObstacles is not None:
                        groupPoints = self.groupWallPoints + self.groupObjPoints
                        self.groupPolygonPoints = [groupPoints[i] for i in list(self.convexHullObstacles.vertices)[:]]
                elif len(self.groupWallPoints) > 0:
                    self.convexHullObstacles = ConvexHull(self.groupWallPoints)
                    if self.convexHullObstacles is not None:
                            self.groupPolygonPoints = [self.groupWallPoints[i] for i in list(self.convexHullObstacles.vertices)[:]]
                    
            else :
                self.groupWall = []
                self.groupWallPoints = []
                self.groupPolygonPoints = []
                self.convexHullObstacles = None
            

            # i=0
            # while i<len(self.groupWall):
            #     for wall in self.detectedWall : 
            #         if wall not in self.groupWall :
            #             if distObj(wall, self.groupWall[i]) < 2*self.radius + 2*self.margin:
            #                 self.groupWall.append(wall)
            #                 self.groupWallPoints+=wall.borderPoints[:]
            #     i+=1
            
            
            

            if (len(self.groupWall)) > 0:
                self.barycenterGroupWall = { 'x' : (1/len(self.groupWall))*np.sum(np.array([wall.x for wall in self.groupWall])), 'y' : (1/len(self.groupWall))*np.sum(np.array([wall.y for wall in self.groupWall]))}

                # if len(self.groupObjPoints) > 0 and len(self.groupWallPoints) > 0:
                #     self.convexHullObstacles = ConvexHull(self.groupWallPoints + self.groupObjPoints)
                #     if self.convexHullObstacles is not None:
                #         groupPoints = self.groupWallPoints + self.groupObjPoints
                #         self.groupPolygonPoints = [groupPoints[i] for i in list(self.convexHullObstacles.vertices)[:]]
                # elif len(self.groupWallPoints) > 0:
                #         self.convexHullObstacles = ConvexHull(self.groupWallPoints)
                #         if self.convexHullObstacles is not None:
                #             self.groupPolygonPoints = [self.groupWallPoints[i] for i in list(self.convexHullObstacles.vertices)[:]]

                if len(self.groupWallPoints) > 0:
                        self.convexHullObstacles = ConvexHull(self.groupWallPoints)
                        if self.convexHullObstacles is not None:
                            self.groupPolygonPoints = [self.groupWallPoints[i] for i in list(self.convexHullObstacles.vertices)[:]]
                
                
                angleCol = (signedAngle2Vects2(self.vel2D, np.array([self.barycenterGroupWall['x'] - self.x, self.barycenterGroupWall['y'] - self.y])))
                polygonInter = polygonLineInter(self, self.groupPolygonPoints,self.barycenterGroupWall, self.vel2D, surface1)
                if len (polygonInter) == 1:
                    if angleCol > 0:
                        self.vel2D = rotate(self.vel2D, - self.rotationSpeed*np.pi/180)
                    elif angleCol <= 0:
                        self.vel2D = rotate(self.vel2D, self.rotationSpeed*np.pi/180)
                elif not self.checkColObjective():
                    
                    angleWall = signedAngle2Vects2(self.vel2D, np.array([self.objective[0]- self.x, self.objective[1] - self.y]))
                    rotationSpeed = min(self.rotationSpeed*np.pi/180, abs(angleWall))
                    if angleWall >= 0:
                        self.vel2D = rotate(self.vel2D, rotationSpeed)
                    elif angleWall < 0:
                        self.vel2D = rotate(self.vel2D, - rotationSpeed)
                # elif pointInPolygon(self, self.groupPolygonPoints):
                #     if angleCol > 0:
                #  
                #         self.vel2D = rotate(self.vel2D, self.turnAroundCoeff*self.rotationSpeed*np.pi/180)
                #     elif angleCol <= 0:
                #  
                #         self.vel2D = rotate(self.vel2D, self.turnAroundCoeff*self.rotationSpeed*np.pi/180)
                elif abs(angleCol) <= np.pi/2 :
                    if angleCol > 0:
                        self.vel2D = rotate(self.vel2D, - self.rotationSpeed*np.pi/180)
                    elif angleCol <= 0:
                        self.vel2D = rotate(self.vel2D, self.rotationSpeed*np.pi/180)
                else:
                    self.noColgoToObjective(surface1)
            else:
                self.noColgoToObjective(surface1)


        else :
            # pour les robots
            if len(self.groupObj) > 0 :
                checkedgroupObj = [self.groupObj[0]]
                checkedgroupObjPoints = self.groupObj[0].polygonPoints[:]
                i=0
                while i<len(checkedgroupObj):
                    for obj in self.groupObj:
                        if obj not in checkedgroupObj:
                            if distObj(obj, checkedgroupObj[i]) < obj.radius + checkedgroupObj[i].radius + 2*self.radius + 2*self.margin:
                                if distObj(obj, self) < self.maxDistConsider :
                                    checkedgroupObj.append(obj)
                                    checkedgroupObjPoints+=obj.polygonPoints[:]
                    i+=1
                self.groupObj = checkedgroupObj
                self.groupObjPoints = checkedgroupObjPoints
                self.convexHullObstacles = ConvexHull(self.groupObjPoints)
                if self.convexHullObstacles is not None:
                    self.groupPolygonPoints = [self.groupObjPoints[i] for i in list(self.convexHullObstacles.vertices)[:]]
            else :
                self.groupObj = []
                self.groupObjPoints = []
                self.groupPolygonPoints = []

            # pour les murs
            if len(self.groupWall) > 0 :
                checkedgroupWall = [self.groupWall[0]]
                checkedgroupWallPoints = self.groupWall[0].borderPoints[:]
                i=0
                while i<len(checkedgroupWall):
                    for wall in self.groupWall:
                        if wall not in checkedgroupWall:
                            if distObj(wall, checkedgroupWall[i]) < 2*self.radius + 2*self.margin:
                                checkedgroupWall.append(wall)
                                checkedgroupWallPoints+=wall.borderPoints[:]
                    i+=1
                self.groupWall = checkedgroupWall
                self.groupWallPoints = checkedgroupWallPoints

                if len(self.groupObjPoints) > 0 and len(self.groupWallPoints) > 0:
                    self.convexHullObstacles = ConvexHull(self.groupWallPoints + self.groupObjPoints)
                    if self.convexHullObstacles is not None:
                        groupPoints = self.groupWallPoints + self.groupObjPoints
                        self.groupPolygonPoints = [groupPoints[i] for i in list(self.convexHullObstacles.vertices)[:]]
                elif len(self.groupWallPoints) > 0:
                    self.convexHullObstacles = ConvexHull(self.groupWallPoints)
                    if self.convexHullObstacles is not None:
                        self.groupPolygonPoints = [self.groupWallPoints[i] for i in list(self.convexHullObstacles.vertices)[:]]

                
            else :
                self.groupWall = []
                self.groupWallPoints = []
                self.groupPolygonPoints = []


            self.noColgoToObjective(surface1)


    def defineObjective(self, coord):
        self.haveObjective = True
        self.objective = [0,0]
        self.objective[0] = coord[0]
        self.objective[1] = coord[1]
        self.ontoObjective = False
        self.vel2D = self.lastVel2D



class Obstacle():
    def __init__(self, x, y, radius, room, movable = False, vel = 2, margin = 2, isWall = False):
        self.isWall = isWall
        self.room = room
        self.x = x
        self.y = y
        self.radius = radius
        self.vel = vel
        self.movable = movable
        self.margin = margin
        self.polygonPointsAbsolute = createPolygonMask([0, 0], 10, self.radius + self.margin)
        self.polygonPoints = deepcopy(self.polygonPointsAbsolute)

        for i in range(len(self.polygonPoints)):
            self.polygonPoints[i][0] = self.polygonPointsAbsolute[i][0] + self.x
            self.polygonPoints[i][1] = self.polygonPointsAbsolute[i][1] + self.y


    def move(self, surface1):
        keys = pygame.key.get_pressed()
    
        if keys[pygame.K_LEFT] and self.x > self.vel + self.radius: 
            self.x -= self.vel

        if keys[pygame.K_RIGHT] and self.x < surface1.get_width() - self.vel - self.radius:  
            self.x += self.vel

        if keys[pygame.K_UP] and self.y > self.vel + self.radius: 
            self.y -= self.vel

        if keys[pygame.K_DOWN] and self.y < surface1.get_height() - self.radius - self.vel:
            self.y += self.vel
        
        for i in range(len(self.polygonPoints)):
            self.polygonPoints[i][0] = self.polygonPointsAbsolute[i][0] + self.x
            self.polygonPoints[i][1] = self.polygonPointsAbsolute[i][1] + self.y



    def draw(self, win, surface1):
        pygame.draw.circle(win, (100,100,100), (self.x, self.y), self.radius)
        # pygame.draw.polygon(surface1, (255, 255, 0, 128), self.polygonPoints)

    