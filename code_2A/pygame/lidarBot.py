
import pygame

import numpy as np
from sympy.solvers import solve
from sympy import Symbol

from utilities import *

class LidarBot():
    def __init__(self, x, y, radius, room):
        self.room = room
        self.x = x
        self.y = y
        self.radius = radius
        self.vel2D = np.asarray([0.1,0.1])
        self.objective = [x + 450, y]
        self.radiusDetection = 100
        self.rotationSpeed = 2
        self.speed = 1


    def draw(self, win):
        pygame.draw.circle(win, (0,255,0), (self.x, self.y), self.radius)

    def move(self):
        self.goToObjective()
        if np.linalg.norm(self.vel2D) !=0:
            vel2DU = self.vel2D/np.linalg.norm(self.vel2D)
        self.x += vel2DU[0]*self.speed
        self.y += vel2DU[1]*self.speed

    def checkCollision(self):
        collision = {}
        for obj in self.room.objects:
            if obj != self :
                if distObj(self, obj) <= self.radiusDetection:
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
    
    def goToObjective(self):
        collision = self.checkCollision()
        if collision :
            init = True
            minDist = None
            minObj = None
            for obj in collision:
                if init : 
                    minDist = distObjDict(self, collision[obj])
                    minObj = obj
                    init = False
                else :
                    dist = distObjDict(self, collision[obj])
                    if dist < minDist:
                        minDist = dist
                        minObj = obj
            
            angleCol = (signedAngle2Vects(self.vel2D, np.array([minObj.x - self.x, minObj.y - self.y])))
            if abs(angleCol) <= np.pi/2:
                if angleCol >= 0:
                    self.vel2D = rotate(self.vel2D, - self.rotationSpeed*np.pi/180)
                elif angleCol < 0:
                    self.vel2D = rotate(self.vel2D, self.rotationSpeed*np.pi/180)
            else:
                angleObj = signedAngle2Vects(self.vel2D, np.array([self.objective[0]- self.x, self.objective[1] - self.y]))
                # if abs(angleObj) > self.rotationSpeed*np.pi/180:
                if angleObj >= 0 :
                    self.vel2D = rotate(self.vel2D, self.rotationSpeed*np.pi/180)
                elif angleObj < 0:
                    self.vel2D = rotate(self.vel2D, - self.rotationSpeed*np.pi/180)

        else :
            angleObj = signedAngle2Vects(self.vel2D, np.array([self.objective[0]- self.x, self.objective[1] - self.y]))
            # if abs(angleObj) > self.rotationSpeed*np.pi/180:
            if angleObj >= 0:
                self.vel2D = rotate(self.vel2D, self.rotationSpeed*np.pi/180)
            elif angleObj < 0:
                self.vel2D = rotate(self.vel2D, - self.rotationSpeed*np.pi/180)



class Obstacle():
    def __init__(self, x, y, radius, room):
        self.room = room
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, win):
        pygame.draw.circle(win, (100,100,100), (self.x, self.y), self.radius)
    