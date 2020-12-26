
import pygame

import numpy as np
from sympy.solvers import solve
from sympy import Symbol

from utilities import *

import random

class LidarBot():
    def __init__(self, x, y, radius, room, objective, randomObjective = False, randomInterval = 10):
        self.room = room
        self.x = x
        self.y = y
        self.radius = radius
        self.vel2D = np.asarray([0.1,0.1])
        self.objective = objective
        self.radiusDetection = 150
        self.rotationSpeed = 2
        self.speed = 2
        self.groupObj = []
        self.detectedObj = []
        self.safeCoeff = 1
        self.ontoObjectiveCoeff = 1
        self.randomObjective = randomObjective
        self.turnAroundCoeff = -1
        self.barycenterGroupObj = {'x' : 0, 'y' : 0}
        self.groupObjRadius = 0
        self.randomInterval = randomInterval
         


    def draw(self, win, surface1):

        # Uncomment for more details about the process !

        # pygame.draw.circle(surface1, (0,150,255, 128), (self.x, self.y), self.radiusDetection)
        # pygame.draw.circle(surface1, (200,50,50, 64), (self.barycenterGroupObj['x'], self.barycenterGroupObj['y']), self.groupObjRadius)
        # pygame.draw.circle(surface1, (20,20,20, 64), (self.barycenterGroupObj['x'], self.barycenterGroupObj['y']), 4)
        
        pygame.draw.circle(win, (0,255,0), (self.x, self.y), self.radius)
        pygame.draw.circle(win, (255,255,255), (self.objective[0], self.objective[1]), self.radius)
        if np.linalg.norm(self.vel2D) !=0:
            vel2DU = self.vel2D/np.linalg.norm(self.vel2D)
            # pygame.draw.line(win, (200,200,200), (self.x, self.y), (self.x + vel2DU[0]*self.radiusDetection, self.y + vel2DU[1]*self.radiusDetection))
        
        

    def move(self, win):
        if self.randomObjective:
            if random.random() > (1 - 1/(100*self.randomInterval)) :
                self.objective[0] = random.randrange(50, win.get_width() - 50)
                self.objective[1] = random.randrange(50, win.get_height() - 50)
        
        self.goToObjective(win)
        if np.linalg.norm(self.vel2D) !=0:
            vel2DU = self.vel2D/np.linalg.norm(self.vel2D)

        self.x += vel2DU[0]*self.speed*self.safeCoeff*self.ontoObjectiveCoeff 
        self.y += vel2DU[1]*self.speed*self.safeCoeff*self.ontoObjectiveCoeff 

    def checkCollision(self):
        collision = {}
        for obj in self.room.objects:
            if obj != self :
                distO = distObj(self, obj)
                if distO <= self.radiusDetection:

                    if distO < self.radius + obj.radius :
                        print("COLLISION")

                    if (obj not in self.detectedObj):
                        self.detectedObj.append(obj)
                    if distO <= min (self.radiusDetection, 50 + obj.radius):
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

    def checkColObjective(self):
        col = False
        for obj in self.groupObj:
            angleColObj = signedAngle2Vects2(np.array([obj.x- self.objective[0], obj.y - self.objective[1]]), -1*np.array([self.objective[0]- self.x, self.objective[1] - self.y]))
            if len(circleLineInter(self, obj, np.array([self.objective[0]- self.x, self.objective[1] - self.y]))) >0 and abs(angleColObj) < np.pi/2:
                col = True
                return col
        return col

    def noColgoToObjective(self):

        self.safeCoeff = 1
        angleCol = (signedAngle2Vects2(self.vel2D, np.array([self.barycenterGroupObj['x'] - self.x, self.barycenterGroupObj['y'] - self.y])))

        if not self.checkColObjective():
            angleObj = signedAngle2Vects2(self.vel2D, np.array([self.objective[0]- self.x, self.objective[1] - self.y]))
            rotationSpeed = min(self.rotationSpeed*np.pi/180, abs(angleObj))
            if angleObj >= 0:
                self.vel2D = rotate(self.vel2D, rotationSpeed)
            elif angleObj < 0:
                self.vel2D = rotate(self.vel2D, - rotationSpeed)

        # TODO : change groupObj Hitbox from circle to polygon
        elif distObjDict(self, self.barycenterGroupObj) < self.groupObjRadius:
            if random.random() > 0.999 :
                self.turnAroundCoeff *= -1
            self.vel2D = self.vel2D
        
        # TODO : change groupObj Hitbox from circle to polygon
        elif len(circleLineInter(self, self.barycenterGroupObj, self.vel2D, objDict = True, objRadius = self.groupObjRadius)) == 2 and abs(angleCol) < np.pi/2:
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


    def goToObjective(self, surface1):
        if distObjList(self, self.objective) < 40*self.speed/self.rotationSpeed + self.radius*2:
            self.ontoObjectiveCoeff = distObjList(self, self.objective)/((40*self.speed/self.rotationSpeed)**(1.25))
        else :
            self.ontoObjectiveCoeff = 1

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
                if  dist - minObj.radius - self.radius < self.speed*150/(np.sqrt(self.rotationSpeed)):
                    self.safeCoeff = max((dist - minObj.radius - self.radius)/(self.speed*150/(np.sqrt(self.rotationSpeed))), 0.01)
            else:
                self.safeCoeff = 1

            

            for obj in checkedCollision:
                if obj not in self.detectedObj:
                    self.detectedObj.append(obj)
            
            if minObj is not None:
                checkedgroupObj = [minObj]
                i=0
                while i<len(checkedgroupObj):
                    for obj in self.groupObj:
                        if obj not in checkedgroupObj:
                            if distObj(obj, checkedgroupObj[i]) < obj.radius + checkedgroupObj[i].radius + 2*self.radius:
                                checkedgroupObj.append(obj)
                    i+=1
                self.groupObj = checkedgroupObj

            i=0
            while i<len(self.groupObj):
                for obj in self.detectedObj : 
                    if obj not in self.groupObj :
                        if distObj(obj, self.groupObj[i]) < obj.radius + self.groupObj[i].radius + 2*self.radius:
                            self.groupObj.append(obj)
                i+=1


            # TODO : change groupObj Hitbox from circle to polygon

            if (len(self.groupObj)) > 0:
                self.barycenterGroupObj = { 'x' : (1/len(self.groupObj))*np.sum(np.array([obj.x for obj in self.groupObj])), 'y' : (1/len(self.groupObj))*np.sum(np.array([obj.y for obj in self.groupObj]))}
                self.groupObjRadius = 0
                for obj in self.groupObj :
                    dist = distObjDict(obj, self.barycenterGroupObj) + obj.radius + self.radius
                    if dist > self.groupObjRadius:
                        self.groupObjRadius = dist

                
                
                
                angleCol = (signedAngle2Vects2(self.vel2D, np.array([self.barycenterGroupObj['x'] - self.x, self.barycenterGroupObj['y'] - self.y])))

                if not self.checkColObjective():
                    angleObj = signedAngle2Vects2(self.vel2D, np.array([self.objective[0]- self.x, self.objective[1] - self.y]))
                    rotationSpeed = min(self.rotationSpeed*np.pi/180, abs(angleObj))
                    if angleObj >= 0:
                        self.vel2D = rotate(self.vel2D, rotationSpeed)
                    elif angleObj < 0:
                        self.vel2D = rotate(self.vel2D, - rotationSpeed)
                # TODO : change groupObj Hitbox from circle to polygon
                elif abs(angleCol) > np.pi/2 and distObjDict(self, self.barycenterGroupObj) < self.groupObjRadius:
                    if angleCol > 0:
                        self.vel2D = rotate(self.vel2D, self.turnAroundCoeff*self.rotationSpeed*np.pi/180)
                    elif angleCol <= 0:
                        self.vel2D = rotate(self.vel2D, self.turnAroundCoeff*self.rotationSpeed*np.pi/180)
                elif abs(angleCol) <= np.pi/2 and distObjDict(self, self.barycenterGroupObj) < self.groupObjRadius:
                    if angleCol > 0:
                        self.vel2D = rotate(self.vel2D, self.turnAroundCoeff*self.rotationSpeed*np.pi/180)
                    elif angleCol <= 0:
                        self.vel2D = rotate(self.vel2D, self.turnAroundCoeff*self.rotationSpeed*np.pi/180)
                elif abs(angleCol) <= np.pi/2 or distObjDict(self, self.barycenterGroupObj) < self.groupObjRadius:
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
    def __init__(self, x, y, radius, room, movable = False, vel = 0):
        self.room = room
        self.x = x
        self.y = y
        self.radius = radius
        self.vel = vel
        self.movable = movable

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


    def draw(self, win, surface1):
        pygame.draw.circle(win, (100,100,100), (self.x, self.y), self.radius)
    