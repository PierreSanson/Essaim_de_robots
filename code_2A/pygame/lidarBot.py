
import pygame

import numpy as np
from sympy.solvers import solve
from sympy import Symbol

from utilities import *

class LidarBot():
    def __init__(self, x, y, radius, room, objective):
        self.room = room
        self.x = x
        self.y = y
        self.radius = radius
        self.vel2D = np.asarray([0.1,0.1])
        self.objective = objective
        self.radiusDetection = 100
        self.rotationSpeed = 2
        self.speed = 1
        self.groupObj = []
        self.groupObjRadius = self.radius
        self.detectedObj = []
        self.safeCoeff = 1
        self.ontoObjectiveCoeff = 1
         


    def draw(self, win, surface1):
        pygame.draw.circle(surface1, (0,0,255, 64), (self.x, self.y), self.radiusDetection)
        
        pygame.draw.circle(win, (0,255,0), (self.x, self.y), self.radius)
        pygame.draw.circle(win, (255,255,255), (self.objective[0], self.objective[1]), self.radius)
        if np.linalg.norm(self.vel2D) !=0:
            vel2DU = self.vel2D/np.linalg.norm(self.vel2D)
            pygame.draw.line(win, (200,200,200), (self.x, self.y), (self.x + vel2DU[0]*self.radiusDetection, self.y + vel2DU[1]*self.radiusDetection))
        
        

    def move(self, win):
        self.goToObjective(win)
        if np.linalg.norm(self.vel2D) !=0:
            vel2DU = self.vel2D/np.linalg.norm(self.vel2D)

        self.x += vel2DU[0]*self.speed*self.safeCoeff*self.ontoObjectiveCoeff 
        self.y += vel2DU[1]*self.speed*self.safeCoeff*self.ontoObjectiveCoeff 

    def checkCollision(self):
        collision = {}
        self.detectedObj = []
        for obj in self.room.objects:
            if obj != self :
                if distObj(self, obj) <= self.radiusDetection:
                    if (obj not in self.detectedObj):
                        self.detectedObj.append(obj)
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
                            
                            collision[obj] = sols[minIndex]
                        else:
                            collision[obj] = sols[0]
        return collision

    def noColgoToObjective(self):
        self.safeCoeff = 1
        angleObj = signedAngle2Vects2(self.vel2D, np.array([self.objective[0]- self.x, self.objective[1] - self.y]))
        # if abs(angleObj) > self.rotationSpeed*np.pi/180:
        rotationSpeed = min(self.rotationSpeed*np.pi/180, abs(angleObj))
        if angleObj >= 0:
            self.vel2D = rotate(self.vel2D, rotationSpeed)
        elif angleObj < 0:
            self.vel2D = rotate(self.vel2D, - rotationSpeed)

    
    def goToObjective(self, surface1):
        if distObjList(self, self.objective)<10:
            self.ontoObjectiveCoeff = self.ontoObjectiveCoeff/2

        for obj in self.groupObj:
            angleCol = (signedAngle2Vects2(self.vel2D, np.array([obj.x - self.x, obj.y - self.y])))
            if abs(angleCol) > np.pi/2:
                self.groupObj.remove(obj)
        collision = self.checkCollision()

        
        checkedCollision = []
        if collision :
            init = True
            minDist = None
            minObj = None
            for obj in collision:
                dist = distObjDict(self, collision[obj])
                angleCol = (signedAngle2Vects2(self.vel2D, np.array([obj.x - self.x, obj.y - self.y])))
                if init : 
                    if abs(angleCol) <= np.pi/2:
                        checkedCollision.append(obj)
                        minDist = distObjDict(self, collision[obj])
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

                dist = distObj(self, minObj)
                if  dist - minObj.radius - self.radius < self.speed*100/(np.sqrt(self.rotationSpeed)):
                    self.safeCoeff = 0.02 + (dist - minObj.radius - self.radius)/(self.speed*100/(np.sqrt(self.rotationSpeed)))
            else:
                self.safeCoeff = 1

            i=0

            for obj in checkedCollision:
                if obj not in self.detectedObj:
                    self.detectedObj.append(obj)

            while i<len(self.groupObj):
                for obj in self.detectedObj : 
                    if obj not in self.groupObj :
                        if distObj(obj, self.groupObj[i]) < obj.radius + self.groupObj[i].radius + 2*self.radius + 10:
                            self.groupObj.append(obj)
                i+=1

            if (len(self.groupObj)) > 0:
                barycenterGroupObj = { 'x' : (1/len(self.groupObj))*np.sum(np.array([obj.x for obj in self.groupObj])), 'y' : (1/len(self.groupObj))*np.sum(np.array([obj.y for obj in self.groupObj]))}
                groupObjRadius = 0
                for obj in self.groupObj :
                    dist = distObjDict(obj, barycenterGroupObj) + obj.radius + 2*self.radius
                    if dist > groupObjRadius:
                        groupObjRadius = dist

                
                pygame.draw.circle(surface1, (200,50,50, 64), (barycenterGroupObj['x'], barycenterGroupObj['y']), groupObjRadius)
                pygame.draw.circle(surface1, (20,20,20, 64), (barycenterGroupObj['x'], barycenterGroupObj['y']), 4)
                

                angleCol = (signedAngle2Vects2(self.vel2D, np.array([barycenterGroupObj['x'] - self.x, barycenterGroupObj['y'] - self.y])))
                if abs(angleCol) <= np.pi/2 or distObjDict(self, barycenterGroupObj) < groupObjRadius:
                    if angleCol > 0:
                        self.vel2D = rotate(self.vel2D, - self.rotationSpeed*np.pi/180)
                    elif angleCol <= 0:
                        self.vel2D = rotate(self.vel2D, self.rotationSpeed*np.pi/180)
                else:
                    self.noColgoToObjective()
            else:
                self.noColgoToObjective()

        else :
            self.noColgoToObjective()



class Obstacle():
    def __init__(self, x, y, radius, room):
        self.room = room
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, win, surface1):
        pygame.draw.circle(win, (100,100,100), (self.x, self.y), self.radius)
    